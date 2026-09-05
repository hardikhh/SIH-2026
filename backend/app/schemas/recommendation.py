from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class ScoreBreakdown(BaseModel):
    education_score: float = Field(..., description="Compatibility score for formal education (0-100)")
    skill_score: float = Field(..., description="Match score for existing vs required skills (0-100)")
    interest_score: float = Field(..., description="Compatibility score for user interests (0-100)")
    experience_score: float = Field(..., description="Score based on years of work experience (0-100)")
    local_opportunity_score: float = Field(..., description="Score based on local training centers and vacancies (0-100)")
    preference_score: float = Field(..., description="Alignment with wage vs self-employment preference (0-100)")
    
    # Weighted contributions that sum to overall_match_score
    weighted_education: float
    weighted_skill: float
    weighted_interest: float
    weighted_experience: float
    weighted_local_opportunity: float
    weighted_preference: float

class WageRoute(BaseModel):
    job_role: str
    starting_salary_range: str
    hiring_companies: str

class SelfEmploymentRoute(BaseModel):
    enterprise_name: str
    pm_ajay_grant_support: str
    equipment_needed: str
    estimated_monthly_income: str

class SkillGapReport(BaseModel):
    matching_skills: List[str]
    missing_skills: List[str] # Skills to be trained under NSQF
    transferable_skills: List[str] # Relevant informal skills

class NearbyTrainingCenter(BaseModel):
    id: str
    name: str
    state: Optional[str] = "Gujarat"
    district: str
    block: Optional[str] = None
    distance_km: int
    address: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    available_seats: int
    free_hostel: bool
    free_daily_stipend_inr: int
    next_batch_date: Optional[str] = None

class LocalJobVacancy(BaseModel):
    id: str
    job_role_id: str
    title: str
    employer: str
    district: str
    state: str = "Gujarat"
    openings: int
    stipend_or_salary: str
    transport_provided: bool = False

class RecommendationItem(BaseModel):
    rank: int
    job_role_id: str
    sector: str
    trade_title: str
    trade_title_hi: Optional[str] = None
    trade_title_gu: Optional[str] = None
    nsqf_level: int
    min_education: str
    training_duration_hours: int
    
    overall_match_score: float # 0 to 100
    score_breakdown: ScoreBreakdown
    
    skill_gap: SkillGapReport
    wage_route: WageRoute
    self_employment_route: SelfEmploymentRoute
    
    nearby_training_centers: List[NearbyTrainingCenter] = Field(default_factory=list)
    local_vacancies: List[LocalJobVacancy] = Field(default_factory=list)
    
    explanation_hi: str
    explanation_gu: str
    explanation_en: str

class RecommendationResponse(BaseModel):
    beneficiary_id: Optional[str] = None
    recommendations: List[RecommendationItem]
    total_evaluated_trades: int
    weights_used: Dict[str, float]
