from sqlalchemy import Column, String, Integer, JSON, Text
from app.database import Base

class NSQFJobRole(Base):
    __tablename__ = "nsqf_job_roles"

    id = Column(String(50), primary_key=True) # e.g. 'SGJ/Q0101'
    sector = Column(String(100), nullable=False)
    trade_title = Column(String(150), nullable=False)
    trade_title_hi = Column(String(150), nullable=True)
    trade_title_gu = Column(String(150), nullable=True)
    
    nsqf_level = Column(Integer, nullable=False)
    min_education = Column(String(50), nullable=False)
    training_duration_hours = Column(Integer, default=300)
    mobility_required = Column(String(100), nullable=True)
    
    core_skills = Column(JSON, default=list)
    transferable_skills = Column(JSON, default=list)
    interests = Column(JSON, default=list)
    keywords = Column(JSON, default=list)
    
    wage_route = Column(JSON, default=dict) # job_role, starting_salary_range, hiring_companies
    self_employment_route = Column(JSON, default=dict) # enterprise_name, pm_ajay_grant_support, equipment_needed, estimated_monthly_income
