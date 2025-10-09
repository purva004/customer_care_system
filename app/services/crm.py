from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus

import httpx
from pydantic import BaseModel, Field, ValidationError

from app.config import settings


class CRMProfile(BaseModel):
    phone_number: str = Field(alias="phone_number")
    name: str | None = None
    gender: str | None = None
    language_code: str | None = Field(default=None, alias="language_code")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

    @property
    def normalized_gender(self) -> str | None:
        return self.gender.lower() if isinstance(self.gender, str) else None

    @property
    def normalized_language(self) -> str | None:
        if not isinstance(self.language_code, str):
            return None
        return self.language_code.replace("_", "-")


async def fetch_profile(phone_number: str) -> CRMProfile | None:
    base_url = settings.crm_api_base_url
    if not base_url or not phone_number:
        return None

    headers: dict[str, str] = {}
    if settings.crm_api_token:
        headers["Authorization"] = f"Bearer {settings.crm_api_token}"

    url = base_url
    params: dict[str, str] | None
    if "{phone}" in base_url:
        url = base_url.replace("{phone}", quote_plus(phone_number))
        params = None
    else:
        url = base_url.rstrip("/")
        params = {"phone": phone_number}

    try:
        async with httpx.AsyncClient(timeout=settings.crm_timeout_seconds) as client:
            response = await client.get(url, params=params, headers=headers)
    except httpx.HTTPError:
        return None

    if response.status_code == 404:
        return None
    if response.status_code >= 400:
        return None

    try:
        payload: Any = response.json()
    except ValueError:
        return None

    if isinstance(payload, dict) and "profile" in payload and isinstance(payload["profile"], dict):
        payload = payload["profile"]

    if isinstance(payload, dict):
        if "phone" in payload and "phone_number" not in payload:
            payload["phone_number"] = payload["phone"]
        if "language" in payload and "language_code" not in payload:
            payload["language_code"] = payload["language"]

    try:
        return CRMProfile.model_validate(payload)
    except ValidationError:
        return None
