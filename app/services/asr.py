"""
ASR abstraction.

MVP uses Twilio <Gather input="speech"> so Twilio provides SpeechResult.
This module is a placeholder to plug external ASR providers if needed.
"""

from __future__ import annotations

from typing import Optional


async def transcribe_audio(url: str) -> Optional[str]:
    """
    Download and transcribe audio at `url` using your provider.
    Not used in current Twilio <Gather> flow.
    """
    return None

