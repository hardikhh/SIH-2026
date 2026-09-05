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

router = APIRouter(prefix="/voice", tags=["Voice Assistant"])

@router.get("/tts")
def stream_tts_audio(text: str, lang: str = "hi"):
    """
    Streams high-fidelity authentic TTS audio for Gujarati, Hindi, or English.
    Solves missing OS voice packs on Windows for Gujarati (gu).
    """
    language = lang if lang in ["hi", "gu", "en"] else "hi"
    try:
        clean_text = text.strip() or "नमस्ते"
        tts = gTTS(text=clean_text, lang=language, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return Response(content=fp.getvalue(), media_type="audio/mpeg")
    except Exception as e:
        print(f"TTS generation error: {e}")
        return Response(content=b"", status_code=500)


@router.get("/welcome")
def get_welcome_prompt(lang: str = "hi"):
    language = lang if lang in DIALOGUE_SCRIPTS else "hi"
    script = DIALOGUE_SCRIPTS[language]
    # Provide top district quick-reply chips right away
    initial_chips = ["📍 गुजरात (अहमदाबाद, सूरत...)", "📍 राजस्थान (जयपुर, जोधपुर...)", "8वीं पास", "10वीं पास"]
    if language == "gu":
        initial_chips = ["📍 ગુજરાત (અમદાવાદ, સુરત...)", "📍 રાજસ્થાન (જયપુર, જોધપુર...)", "8 પાસ", "10 પાસ"]
    elif language == "en":
        initial_chips = ["📍 Gujarat (Ahmedabad, Surat...)", "📍 Rajasthan (Jaipur, Jodhpur...)", "8th Pass", "10th Pass"]

    return {
        "language": language,
        "welcome_message": script["welcome"],
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
