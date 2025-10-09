from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Customer, CustomerCreate, CustomerUpdate, GenderEnum

if TYPE_CHECKING:
    from app.services.crm import CRMProfile


def gender_from_string(value: str | None) -> GenderEnum | None:
    if not value:
        return None
    try:
        return GenderEnum(value)
    except ValueError:
        return None


async def get_by_phone(db: AsyncSession, phone: str) -> Customer | None:
    res = await db.execute(select(Customer).where(Customer.phone_number == phone))
    return res.scalar_one_or_none()


async def create(db: AsyncSession, payload: CustomerCreate) -> Customer:
    obj = Customer(
        phone_number=payload.phone_number,
        name=payload.name,
        gender=(payload.gender.value if payload.gender else None) or "neutral",
        language_code=payload.language_code or "en-US",
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def update(db: AsyncSession, obj: Customer, payload: CustomerUpdate) -> Customer:
    if payload.name is not None:
        obj.name = payload.name
    if payload.gender is not None:
        obj.gender = payload.gender.value
    if payload.language_code is not None:
        obj.language_code = payload.language_code
    await db.commit()
    await db.refresh(obj)
    return obj


async def get_or_create_default(db: AsyncSession, phone: str, default_language: str, default_gender: str) -> Customer:
    existing = await get_by_phone(db, phone)
    if existing:
        return existing
    return await create(
        db,
        CustomerCreate(phone_number=phone, gender=None, language_code=default_language),
    )


async def upsert_from_crm(
    db: AsyncSession,
    crm_profile: "CRMProfile",
    fallback_language: str,
    fallback_gender: str,
) -> Customer:
    phone = crm_profile.phone_number
    existing = await get_by_phone(db, phone)
    language = crm_profile.normalized_language or fallback_language
    gender_enum = gender_from_string(crm_profile.normalized_gender)
    gender_value = (gender_enum.value if gender_enum else fallback_gender) or fallback_gender

    if existing:
        if crm_profile.name:
            existing.name = crm_profile.name
        if gender_enum:
            existing.gender = gender_enum.value
        elif not existing.gender:
            existing.gender = fallback_gender
        existing.language_code = language or existing.language_code or fallback_language
        await db.commit()
        await db.refresh(existing)
        return existing

    obj = Customer(
        phone_number=phone,
        name=crm_profile.name,
        gender=gender_value or fallback_gender,
        language_code=language or fallback_language,
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


