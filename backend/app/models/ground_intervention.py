import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from app.database import Base

class GroundIntervention(Base):
    __tablename__ = "ground_interventions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    beneficiary_id = Column(String(36), ForeignKey("beneficiaries.id"), nullable=False)
    
    intervention_type = Column(String(100), nullable=False) # 'PM-AJAY GIA Grant', 'Mobilization / Counseling', 'Mobility Support', 'Placement Follow-up'
    assigned_officer_name = Column(String(100), default="District PM-AJAY Field Coordinator")
    assigned_officer_phone = Column(String(20), default="+91 98251 00000")
    
    priority = Column(String(20), default="Medium") # 'Low', 'Medium', 'High', 'Urgent'
    status = Column(String(50), default="Open") # 'Open', 'In-Progress', 'Resolved'
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
