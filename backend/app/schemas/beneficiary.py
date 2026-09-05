from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

class BeneficiaryBase(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    language_preference: str = "hi"
    age: Optional[int] = None
    gender: Optional[str] = None
    education_level: Optional[str] = None
    location_state: Optional[str] = None
    location_district: Optional[str] = None
    location_block: Optional[str] = None
    full_address: Optional[str] = None
    pincode: Optional[str] = None
    max_travel_distance_km: int = 15
    has_mobility_constraint: bool = False
    family_occupation: Optional[str] = None
    current_livelihood: Optional[str] = None
    work_experience_years: float = 0.0
    existing_skills: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    livelihood_preference: str = "Both"
    status: str = "Profiled"

class BeneficiaryCreate(BeneficiaryBase):
    pass

class BeneficiaryUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    language_preference: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    education_level: Optional[str] = None
    location_state: Optional[str] = None
    location_district: Optional[str] = None
    location_block: Optional[str] = None
    full_address: Optional[str] = None
    pincode: Optional[str] = None
    max_travel_distance_km: Optional[int] = None
    has_mobility_constraint: Optional[bool] = None
    family_occupation: Optional[str] = None
    current_livelihood: Optional[str] = None
    work_experience_years: Optional[float] = None
    existing_skills: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    livelihood_preference: Optional[str] = None
    status: Optional[str] = None

class BeneficiaryResponse(BeneficiaryBase):
    id: str
    conversation_transcript: List[Any] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Canonical schema used for LLM structured extraction
class BeneficiaryProfileExtract(BaseModel):
    name: Optional[str] = Field(None, description="Beneficiary name if mentioned")
    age: Optional[int] = Field(None, description="Age in years")
    gender: Optional[str] = Field(None, description="Male, Female, or Other")
    education_level: Optional[str] = Field(None, description="e.g., Below 8th, 8th Pass, 10th Pass, 12th Pass, Graduate")
    family_occupation: Optional[str] = Field(None, description="Traditional or family caste/artisan work")
    current_livelihood: Optional[str] = Field(None, description="Current occupation or source of income")
    existing_skills: List[str] = Field(default_factory=list, description="Skills, tools, or techniques the user already knows")
    work_experience_years: Optional[float] = Field(0.0, description="Estimated years of practical work experience")
    interests: List[str] = Field(default_factory=list, description="Trades, hobbies, or areas they are interested in learning")
    max_travel_distance_km: Optional[int] = Field(15, description="Maximum travel distance in kilometers")
    has_mobility_constraint: Optional[bool] = Field(False, description="True if beneficiary has physical disability or cannot travel far")
    livelihood_preference: Optional[str] = Field("Both", description="'Wage Employment', 'Self Employment', or 'Both'")
    location_state: Optional[str] = Field(None, description="State name: Gujarat or Rajasthan")
    location_district: Optional[str] = Field(None, description="District name")
    location_block: Optional[str] = Field(None, description="Block, Tehsil, or City")
    full_address: Optional[str] = Field(None, description="Complete street address, village, or landmark")
    pincode: Optional[str] = Field(None, description="6-digit postal PIN code")
