from sqlalchemy import Column, String, Integer, Boolean, JSON
from app.database import Base

class TrainingCenter(Base):
    __tablename__ = "training_centers"

    id = Column(String(50), primary_key=True)
    name = Column(String(150), nullable=False)
    state = Column(String(50), default="Gujarat")
    district = Column(String(50), default="Ahmedabad")
    block = Column(String(50), nullable=True)
    address = Column(String(255), nullable=True)
    distance_km_from_center = Column(Integer, default=10)
    contact_person = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    affiliated_scheme = Column(String(100), default="PM-AJAY GIA")
    courses_offered = Column(JSON, default=list) # List of job_role_ids
    available_seats = Column(Integer, default=30)
    free_hostel_available = Column(Boolean, default=False)
    free_daily_stipend_inr = Column(Integer, default=150)
    free_uniform_and_toolkit = Column(Boolean, default=True)
    next_batch_date = Column(String(20), nullable=True)
