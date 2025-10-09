from __future__ import annotations

from typing import Optional
from fastapi import Response


def xml_response(xml: str) -> Response:
    return Response(content=xml, media_type="application/xml")


def say_twiml(text: str, language: str, voice: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say language="{language}" voice="{voice}">{escape(text)}</Say>
</Response>"""


def gather_speech_twiml(prompt: str, action_url: str, language: str, voice: str, hints: Optional[str] = None) -> str:
    hints_attr = f' hints="{escape(hints)}"' if hints else ""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Gather input="speech" action="{action_url}" method="POST" language="{language}"{hints_attr}>
    <Say language="{language}" voice="{voice}">{escape(prompt)}</Say>
  </Gather>
  <Say language="{language}" voice="{voice}">We did not receive any input. Goodbye.</Say>
  <Hangup/>
</Response>"""


def escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )

