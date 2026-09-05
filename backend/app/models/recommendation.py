import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, Text, ForeignKey
from app.database import Base

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    beneficiary_id = Column(String(36), ForeignKey("beneficiaries.id"), nullable=False)
    job_role_id = Column(String(50), ForeignKey("nsqf_job_roles.id"), nullable=False)
    rank = Column(Integer, default=1)
    
    overall_match_score = Column(Float, nullable=False) # 0 to 100
    score_breakdown = Column(JSON, default=dict)
    
    matching_skills = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    transferable_skills = Column(JSON, default=list)
    
    llm_explanation_hi = Column(Text, nullable=True)
    llm_explanation_gu = Column(Text, nullable=True)
    llm_explanation_en = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
