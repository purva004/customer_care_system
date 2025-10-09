from __future__ import annotations

from typing import Optional

try:
    from openai import AsyncOpenAI
except Exception:  # pragma: no cover - optional
    AsyncOpenAI = None  # type: ignore

from app.config import settings


async def generate_reply(user_utterance: str, language_code: str, name: Optional[str] = None) -> str:
    """
    Generate a reply. If OpenAI key is configured, use LLM; otherwise return a simple template.
    """
    if settings.openai_api_key and AsyncOpenAI is not None:
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        sys = (
            "You are a concise, friendly customer-care assistant. "
            "Answer in the same language as the user. Be helpful and brief."
        )
        name_part = f" The caller's name is {name}." if name else ""
        prompt = (
            f"Language hint: {language_code}. {name_part} "
            f"User said: {user_utterance}"
        )
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": sys}, {"role": "user", "content": prompt}],
            max_tokens=120,
            temperature=0.3,
        )
        return resp.choices[0].message.content or ""
    # Fallback rule-based reply
    return (
        {
            "en": "Thanks for calling. How can I help you today?",
            "hi": "फोन करने के लिए धन्यवाद। मैं आपकी कैसे मदद कर सकता/सकती हूँ?",
            "mr": "फोन केल्याबद्दल धन्यवाद. मी तुम्हाला कशी मदत करू?",
        }
        .get(language_code.split("-")[0], "Thanks for calling. How can I help you today?")
    )

