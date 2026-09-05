from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from app.schemas.beneficiary import BeneficiaryProfileExtract

class VoiceChatMessage(BaseModel):
    role: str # 'user' or 'assistant'
    content: str
    timestamp: Optional[str] = None

class VoiceTurnRequest(BaseModel):
    beneficiary_id: Optional[str] = None
    user_message: str
    language: str = "hi" # 'hi', 'gu', 'en'
    conversation_history: List[VoiceChatMessage] = Field(default_factory=list)
    current_profile: Optional[Dict[str, Any]] = None

class VoiceTurnResponse(BaseModel):
    beneficiary_id: str
    ai_response: str
    language: str
    is_profile_complete: bool = False
    profile_data: Optional[BeneficiaryProfileExtract] = None
    missing_fields: List[str] = Field(default_factory=list)
    suggested_quick_replies: List[str] = Field(default_factory=list)
    next_question_field: Optional[str] = None
