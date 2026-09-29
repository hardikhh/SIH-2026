import uuid
import io
from typing import Optional
from fastapi import APIRouter, Depends
from fastapi.responses import Response
try:
    from gtts import gTTS
except ImportError:
    gTTS = None
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.beneficiary import Beneficiary
from app.schemas.voice import VoiceTurnRequest, VoiceTurnResponse
from app.services.ai_agent import ai_agent, DIALOGUE_SCRIPTS

import re

import hashlib
import os
import threading

CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "tts_cache"))
os.makedirs(CACHE_DIR, exist_ok=True)
_TTS_RAM_CACHE: dict[str, bytes] = {}

router = APIRouter(prefix="/voice", tags=["Voice Assistant"])

def clean_for_tts(text: str) -> str:
    if not text:
        return ""
    # Strip markdown symbols (*, _, #, `, ~, >, etc.)
    cleaned = re.sub(r"[*_#`~>\[\]\(\)]", "", text)
    # Replace slashes and colons with space to prevent unnatural pauses
    cleaned = cleaned.replace("/", " ").replace(":", " ")
    # Normalize whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned

def get_tts_cache_key(clean_text: str, lang: str) -> str:
    return hashlib.md5(f"{lang}:{clean_text}".encode("utf-8")).hexdigest()

def get_or_generate_tts(text: str, lang: str = "hi") -> bytes:
    language = lang if lang in ["hi", "gu", "en"] else "hi"
    clean_text = clean_for_tts(text) or ("નમસ્તે" if language == "gu" else "नमस्ते")
    key = get_tts_cache_key(clean_text, language)

    # 1. In-memory cache check (0ms)
    if key in _TTS_RAM_CACHE:
        return _TTS_RAM_CACHE[key]

    # 2. Disk cache check (<1ms)
    disk_path = os.path.join(CACHE_DIR, f"{key}.mp3")
    if os.path.exists(disk_path):
        try:
            with open(disk_path, "rb") as f:
                content = f.read()
                if content:
                    _TTS_RAM_CACHE[key] = content
                    return content
        except Exception as e:
            print(f"Error reading disk cache: {e}", flush=True)

    # 3. Generate via gTTS
    if gTTS is None:
        raise RuntimeError("gTTS is not installed or failed to import.")
    tts = gTTS(text=clean_text, lang=language, slow=False)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    audio_bytes = fp.getvalue()

    # Save to RAM and Disk cache
    _TTS_RAM_CACHE[key] = audio_bytes
    try:
        with open(disk_path, "wb") as f:
            f.write(audio_bytes)
    except Exception as e:
        print(f"Error saving to disk cache: {e}", flush=True)

    return audio_bytes

def prewarm_tts():
    """Background task to pre-generate and cache TTS audio for all standard prompts."""
    try:
        for lang, script in DIALOGUE_SCRIPTS.items():
            for key in ["welcome", "ask_education", "ask_skills", "ask_interests", "ask_mobility", "ask_preference", "ask_location", "complete"]:
                text = script.get(key)
                if text:
                    try:
                        get_or_generate_tts(text, lang)
                    except Exception as e:
                        print(f"TTS prewarm notice ({lang}:{key}): {e}", flush=True)
        print("TTS cache pre-warming finished successfully.", flush=True)
    except Exception as e:
        print(f"TTS prewarm exception: {e}", flush=True)

# Start background pre-warming on load
threading.Thread(target=prewarm_tts, daemon=True).start()

@router.get("/tts")
def stream_tts_audio(text: str, lang: str = "hi"):
    """
    Streams high-fidelity authentic TTS audio for Gujarati, Hindi, or English.
    Returns cached audio in <2ms for instantaneous start.
    """
    language = lang if lang in ["hi", "gu", "en"] else "hi"
    try:
        audio_bytes = get_or_generate_tts(text, language)
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=tts.mp3",
                "Cache-Control": "public, max-age=86400",
                "Accept-Ranges": "bytes",
            }
        )
    except Exception as e:
        print(f"TTS generation error: {e}", flush=True)
        return Response(content=b"", status_code=500)



@router.get("/welcome")
def get_welcome_prompt(lang: str = "hi"):
    language = lang if lang in DIALOGUE_SCRIPTS else "hi"
    script = DIALOGUE_SCRIPTS[language]
    welcome_text = script["welcome"]
    
    # Pre-cache welcome audio in background thread if not already in RAM
    threading.Thread(target=get_or_generate_tts, args=(welcome_text, language), daemon=True).start()

    # Provide top district quick-reply chips right away
    initial_chips = ["📍 गुजरात (अहमदाबाद, सूरत...)", "📍 राजस्थान (जयपुर, जोधपुर...)", "8वीं पास", "10वीं पास"]
    if language == "gu":
        initial_chips = ["📍 ગુજરાત (અમદાવાદ, સુરત...)", "📍 રાજસ્થાન (જયપુર, જોધપુર...)", "8 પાસ", "10 પાસ"]
    elif language == "en":
        initial_chips = ["📍 Gujarat (Ahmedabad, Surat...)", "📍 Rajasthan (Jaipur, Jodhpur...)", "8th Pass", "10th Pass"]

    return {
        "language": language,
        "welcome_message": welcome_text,
        "suggested_quick_replies": initial_chips,
    }

@router.post("/turn", response_model=VoiceTurnResponse)
def process_voice_turn(payload: VoiceTurnRequest, db: Session = Depends(get_db)):
    beneficiary_id = payload.beneficiary_id or str(uuid.uuid4())
    
    # Process turn with AI Agent
    ai_response, profile_data, is_complete, missing_fields, quick_replies, next_field = ai_agent.process_turn(
        user_message=payload.user_message,
        language=payload.language,
        current_profile=payload.current_profile or {},
        conversation_history=[m.model_dump() for m in payload.conversation_history]
    )

    # Immediately queue/ensure TTS audio is cached so frontend plays it with 0ms wait
    threading.Thread(target=get_or_generate_tts, args=(ai_response, payload.language), daemon=True).start()

    # If beneficiary exists or if profile is complete, save/update in database
    b = db.query(Beneficiary).filter(Beneficiary.id == beneficiary_id).first()
    if not b and (is_complete or len(payload.conversation_history) > 2):
        b = Beneficiary(
            id=beneficiary_id,
            name=profile_data.name or "Beneficiary (Voice User)",
            language_preference=payload.language,
            age=profile_data.age,
            gender=profile_data.gender,
            education_level=profile_data.education_level or "8th Pass",
            location_state=profile_data.location_state or "Gujarat",
            location_district=profile_data.location_district or "Ahmedabad",
            location_block=profile_data.location_block,
            full_address=profile_data.full_address,
            pincode=profile_data.pincode,
            max_travel_distance_km=profile_data.max_travel_distance_km or 15,
            has_mobility_constraint=profile_data.has_mobility_constraint,
            family_occupation=profile_data.family_occupation,
            current_livelihood=profile_data.current_livelihood,
            work_experience_years=profile_data.work_experience_years or 0.0,
            existing_skills=profile_data.existing_skills or [],
            interests=profile_data.interests or [],
            livelihood_preference=profile_data.livelihood_preference or "Both",
            status="Profiled" if is_complete else "Profiling",
            conversation_transcript=[
                {"role": "user", "content": payload.user_message},
                {"role": "assistant", "content": ai_response}
            ]
        )
        db.add(b)
        db.commit()
    elif b:
        # Update existing record
        for k, v in profile_data.model_dump(exclude_none=True).items():
            setattr(b, k, v)
        if is_complete:
            b.status = "Profiled"
        current_transcript = list(b.conversation_transcript or [])
        current_transcript.append({"role": "user", "content": payload.user_message})
        current_transcript.append({"role": "assistant", "content": ai_response})
        b.conversation_transcript = current_transcript
        db.commit()

    return VoiceTurnResponse(
        beneficiary_id=beneficiary_id,
        ai_response=ai_response,
        language=payload.language,
        is_profile_complete=is_complete,
        profile_data=profile_data,
        missing_fields=missing_fields,
        suggested_quick_replies=quick_replies,
        next_question_field=next_field,
    )
