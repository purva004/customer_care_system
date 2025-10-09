from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession
from langdetect import detect as lang_detect

from app.config import settings
from app.db import get_db
from app.models import GenderEnum
from app.services import crm as crm_svc
from app.services import nlp
from app.services import profiles as prof_svc
from app.utils.twiml import xml_response, say_twiml, gather_speech_twiml


router = APIRouter(tags=["voice"]) 


def select_voice(language_code: str, gender: str) -> tuple[str, str]:
    """
    Return (twilio_language, twilio_voice)
    Favor `alice` for female-like voice in many locales, or 'man'/'woman'.
    For Indian languages, try Polly voices if available via Twilio (requires account enablement).
    """
    lang = language_code or settings.default_language
    g = gender or settings.default_gender

    # Basic defaults
    voice = "alice" if g == GenderEnum.female.value else ("man" if g == GenderEnum.male.value else "alice")
    twilio_lang = lang

    # Map common base languages to Twilio-supported variants
    base = lang.split("-")[0]
    if base == "en":
        twilio_lang = "en-US"
        voice = "alice" if g != GenderEnum.male.value else "man"
    elif base == "hi":
        # Polly Aditi/Raveena if enabled on Twilio; fallback to en-US alice if not supported
        twilio_lang = "hi-IN"
        voice = "Polly.Aditi" if g != GenderEnum.male.value else "Polly.Raveena"
    elif base == "mr":
        # Marathi TTS may not be available via Twilio Say; fallback to Hindi or English
        twilio_lang = "hi-IN"
        voice = "Polly.Aditi"

    return twilio_lang, voice


@router.post("/voice/incoming")
async def voice_incoming(request: Request, db: AsyncSession = Depends(get_db)):
    # Twilio will provide caller number in `From` like +14155551234
    form = await request.form()
    caller = str(form.get("From") or "").strip()

    # Find profile or use defaults
    profile = None
    if caller:
        profile = await prof_svc.get_by_phone(db, caller)
        if not profile:
            external = await crm_svc.fetch_profile(caller)
            if external:
                profile = await prof_svc.upsert_from_crm(
                    db,
                    external,
                    settings.default_language,
                    settings.default_gender,
                )

    language = (profile.language_code if profile else settings.default_language)
    gender = (profile.gender if profile else settings.default_gender)
    twilio_lang, voice = select_voice(language, gender)

    prompt = {
        "en": "Welcome. Please say your question after the beep.",
        "hi": "स्वागत है। बीप के बाद अपना प्रश्न बोलें।",
        "mr": "स्वागत आहे. बीपनंतर आपला प्रश्न बोला.",
    }.get(language.split("-")[0], "Welcome. Please say your question after the beep.")

    twiml = gather_speech_twiml(
        prompt=prompt,
        action_url=f"/voice/handle",
        language=twilio_lang,
        voice=voice,
        hints=None,
    )
    return xml_response(twiml)


@router.post("/voice/handle")
async def voice_handle(
    request: Request,
    db: AsyncSession = Depends(get_db),
    From: str = Form(default=""),
    SpeechResult: str = Form(default=""),
):
    caller = (From or "").strip()
    utterance = (SpeechResult or "").strip()

    profile = await prof_svc.get_by_phone(db, caller) if caller else None
    if not profile and caller:
        external = await crm_svc.fetch_profile(caller)
        if external:
            profile = await prof_svc.upsert_from_crm(
                db,
                external,
                settings.default_language,
                settings.default_gender,
            )
    if not profile:
        # Create a default profile with detected language if possible
        detected = None
        try:
            if utterance:
                detected = lang_detect(utterance)
        except Exception:
            detected = None
        lang_map = {"en": "en-US", "hi": "hi-IN", "mr": "mr-IN"}
        language = lang_map.get(detected, settings.default_language)
        profile = await prof_svc.get_or_create_default(db, caller or "unknown", language, settings.default_gender)

    language = profile.language_code
    gender = profile.gender
    twilio_lang, voice = select_voice(language, gender)

    reply_text = await nlp.generate_reply(utterance, language_code=language, name=profile.name)
    twiml = say_twiml(reply_text, language=twilio_lang, voice=voice)
    return xml_response(twiml)





