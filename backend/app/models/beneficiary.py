import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, DateTime, Text
from app.database import Base

class Beneficiary(Base):
    __tablename__ = "beneficiaries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)
    language_preference = Column(String(10), default="hi") # 'hi', 'gu', 'en'
    
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    education_level = Column(String(50), nullable=True) # e.g. 'Below 8th', '8th Pass', '10th Pass', '12th Pass'
    
    location_state = Column(String(50), default="Gujarat")
    location_district = Column(String(50), default="Ahmedabad")
    location_block = Column(String(50), nullable=True)
    full_address = Column(String(255), nullable=True)
    pincode = Column(String(10), nullable=True)
    
    max_travel_distance_km = Column(Integer, default=15)
    has_mobility_constraint = Column(Boolean, default=False)
    
    family_occupation = Column(String(100), nullable=True)
    current_livelihood = Column(String(100), nullable=True)
    work_experience_years = Column(Float, default=0.0)
    
    # Stored as JSON lists of strings
    existing_skills = Column(JSON, default=list)
    interests = Column(JSON, default=list)
    
    livelihood_preference = Column(String(50), default="Both") # 'Wage Employment', 'Self Employment', 'Both'
    status = Column(String(50), default="Profiled") # 'Profiling', 'Profiled', 'In Training', 'Certified', 'Placed', 'Self Employed', 'Intervention Needed'
    
    conversation_transcript = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
