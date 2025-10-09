from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import CustomerOut, CustomerCreate, CustomerUpdate, Customer
from app.services import profiles as svc


router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("", response_model=CustomerOut)
async def create_profile(payload: CustomerCreate, db: AsyncSession = Depends(get_db)):
    existing = await svc.get_by_phone(db, payload.phone_number)
    if existing:
        raise HTTPException(status_code=409, detail="Profile already exists for this phone")
    obj = await svc.create(db, payload)
    return obj


@router.get("/by_phone/{phone}", response_model=CustomerOut)
async def get_profile_by_phone(phone: str, db: AsyncSession = Depends(get_db)):
    obj = await svc.get_by_phone(db, phone)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj


@router.put("/{id}", response_model=CustomerOut)
async def update_profile(id: int, payload: CustomerUpdate, db: AsyncSession = Depends(get_db)):
    obj = await db.get(Customer, id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    updated = await svc.update(db, obj, payload)
    return updated
