from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models.beneficiary import Beneficiary
from app.models.nsqf_job_role import NSQFJobRole
from app.models.training_center import TrainingCenter
from app.schemas.beneficiary import BeneficiaryBase
from app.schemas.recommendation import RecommendationResponse, RecommendationItem
from app.services.recommendation_engine import recommendation_engine

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.get("/catalog")
def get_nsqf_catalog(db: Session = Depends(get_db)):
    """Returns the complete verified NSQF job role catalog."""
    roles = db.query(NSQFJobRole).all()
    return roles

@router.get("/training-centers")
def get_training_centers(db: Session = Depends(get_db)):
    """Returns all verified PM-AJAY affiliated training centers."""
    centers = db.query(TrainingCenter).all()
    return centers

@router.get("/beneficiary/{beneficiary_id}", response_model=RecommendationResponse)
def get_recommendations_for_beneficiary(beneficiary_id: str, db: Session = Depends(get_db)):
    """Computes transparent top-3 recommendations for a saved beneficiary."""
    beneficiary = db.query(Beneficiary).filter(Beneficiary.id == beneficiary_id).first()
    if not beneficiary:
        raise HTTPException(status_code=404, detail="Beneficiary not found")
    
    all_roles = db.query(NSQFJobRole).all()
    all_centers = db.query(TrainingCenter).all()

    top_recs = recommendation_engine.evaluate_beneficiary(
        beneficiary=beneficiary,
        all_job_roles=all_roles,
        training_centers=all_centers,
        top_k=3
    )

    return RecommendationResponse(
        beneficiary_id=beneficiary.id,
        recommendations=top_recs,
        total_evaluated_trades=len(all_roles),
        weights_used={
            "education": settings.WEIGHT_EDUCATION,
            "skills": settings.WEIGHT_SKILLS,
            "interests": settings.WEIGHT_INTERESTS,
            "experience": settings.WEIGHT_EXPERIENCE,
            "local_opportunity": settings.WEIGHT_LOCAL_OPPORTUNITY,
            "preference": settings.WEIGHT_PREFERENCE,
        }
    )

@router.post("/evaluate-direct", response_model=RecommendationResponse)
def evaluate_direct_profile(profile: BeneficiaryBase, db: Session = Depends(get_db)):
    """Evaluates an ad-hoc beneficiary profile on-the-fly without saving to DB first."""
    temp_beneficiary = Beneficiary(**profile.model_dump())
    all_roles = db.query(NSQFJobRole).all()
    all_centers = db.query(TrainingCenter).all()

    top_recs = recommendation_engine.evaluate_beneficiary(
        beneficiary=temp_beneficiary,
        all_job_roles=all_roles,
        training_centers=all_centers,
        top_k=3
    )

    return RecommendationResponse(
        beneficiary_id=None,
        recommendations=top_recs,
        total_evaluated_trades=len(all_roles),
        weights_used={
            "education": settings.WEIGHT_EDUCATION,
            "skills": settings.WEIGHT_SKILLS,
            "interests": settings.WEIGHT_INTERESTS,
            "experience": settings.WEIGHT_EXPERIENCE,
            "local_opportunity": settings.WEIGHT_LOCAL_OPPORTUNITY,
            "preference": settings.WEIGHT_PREFERENCE,
        }
    )
