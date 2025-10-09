from __future__ import annotations

import asyncio
from pathlib import Path

from base64 import b64decode

from fastapi import FastAPI
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncEngine

from app.config import settings
from app.db import Base, engine
from app.routers import profiles as profiles_router
from app.routers import voice as voice_router


_FAVICON_PNG = b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/xcAAgMBAp/n8SkAAAAASUVORK5CYII="
)

app = FastAPI(title="Personalized Customer Care Response System")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(content=_FAVICON_PNG, media_type="image/png")


@app.on_event("startup")
async def on_startup():
    # Create database tables if not present (simple auto-migration for MVP)
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    async with engine.begin() as conn:  # type: ignore[call-arg]
        await conn.run_sync(Base.metadata.create_all)


@app.get("/healthz")
async def healthz():
    return {
        "status": "ok",
        "env": settings.app_env,
    }


app.include_router(profiles_router.router)
app.include_router(voice_router.router)


