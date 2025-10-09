"""
TTS abstraction.

MVP relies on Twilio <Say> so we do not generate audio here.
This module can be extended to call OpenAI/Azure/Polly and return an audio URL.
"""

from __future__ import annotations

from typing import Optional


async def synthesize_to_url(text: str, language_code: str, gender: str) -> Optional[str]:
    """
    Return a URL to synthesized audio (e.g., S3 or CDN) for the given text.
    Not used in MVP when Twilio <Say> is used.
    """
    return None

