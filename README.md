# Personalized Customer Care Response System (MVP)

## Overview
- Goal: API-driven IVR backend that personalizes responses by caller profile (gender, native language), supports multilingual prompts, and integrates with telephony (Twilio) for real-time calls.
- This MVP implements: profile-based voice/language selection, adaptable IVR prompts, privacy-conscious storage, optional AI-generated replies, and a path to external CRM integration.

## Quick Start
1. **Python setup**
   - Python 3.10+
   - `pip install -r requirements.txt`
2. **Environment**
   - Copy `.env.example` to `.env` and adjust values.
   - Minimal local run needs no secrets. For webhook validation or LLM replies add `TWILIO_AUTH_TOKEN`, `OPENAI_API_KEY`, etc.
3. **Run the API**
   - `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
   - Health check: `GET http://localhost:8000/healthz`
4. **Interact**
   - Swagger UI: `http://localhost:8000/docs`
   - Create profiles: `POST /profiles`
   - Look up profiles: `GET /profiles/by_phone/{phone}`

## Real-Time Phone Support Flow
1. Run the FastAPI app (step above).
2. Expose it publicly during testing with ngrok: `ngrok http 8000` (install first). Copy the HTTPS forwarding URL.
3. Configure Twilio Voice number webhook to `https://<ngrok-id>.ngrok.io/voice/incoming`.
4. Call the Twilio number. The flow:
   - Twilio sends call events to `/voice/incoming`.
   - The app loads caller context (profile DB, CRM lookup, or default language detection).
   - `/voice/handle` returns TwiML `<Say>` using personalized language + voice.
5. Adjust prompts or responses in `app/services/nlp.py` and restart (or rely on `--reload`).

## CRM / External Profile Lookup
- Set these env vars (optional):
  - `CRM_API_BASE_URL`: Base URL for your profile service. Use `{phone}` placeholder or rely on a `?phone=` query, e.g. `https://crm.example.com/api/profile?phone=` or `https://crm.example.com/api/profile/{phone}`.
  - `CRM_API_TOKEN`: Bearer token added to `Authorization` header.
  - `CRM_TIMEOUT_SECONDS`: Request timeout (default 3.0).
- When a call arrives and no local profile exists, the app calls the CRM API.
  - Expected JSON keys: `phone_number` (or `phone`), optional `name`, `gender`, `language_code` (or `language`).
  - Successful responses auto-upsert into the local SQLite cache via `app/services/profiles.py` and drive voice selection instantly.
- If CRM lookup fails or lacks data, the system falls back to language detection + default gender from env settings.

## Design Notes
- **Database**: SQLite via SQLAlchemy; tables auto-created on startup.
- **Voice selection**: Maps gender/language to Twilio-compatible voices (uses Polly voices when available for Indic languages).
- **Speech**: Uses Twilio `<Gather input="speech">` for ASR. Swap to external ASR in `app/services/asr.py` if needed.
- **TTS**: Uses `<Say>`. Custom TTS streaming hooks live in `app/services/tts.py`.
- **Dynamic replies**: Implemented in `app/services/nlp.py`; plug in OpenAI or rule-based templates.
- **Security**: Stores minimal PII (phone, gender, language). Add HTTPS, webhook signature validation (enable via `TWILIO_AUTH_TOKEN`), and access controls before production deployments.

## Local Testing Without Twilio
- Call `POST /voice/handle` with form data (`From`, `SpeechResult`) to inspect returned TwiML.
- Example:
  ```bash
  curl -X POST http://localhost:8000/voice/handle \
       -d "From=+15551234567" \
       -d "SpeechResult=I need help with my order"
  ```

## Next Enhancements
- Add RAG over your knowledge base for accurate answers.
- Build an admin UI for analytics and prompt/voice management.
- Add authentication for profile management APIs.
- Capture or confirm gender/language preferences on first call.
