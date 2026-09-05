from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.beneficiary import Beneficiary
from app.schemas.beneficiary import BeneficiaryCreate, BeneficiaryUpdate, BeneficiaryResponse

router = APIRouter(prefix="/beneficiaries", tags=["Beneficiaries"])

@router.post("", response_model=BeneficiaryResponse)
def create_beneficiary(payload: BeneficiaryCreate, db: Session = Depends(get_db)):
    beneficiary = Beneficiary(**payload.model_dump())
    db.add(beneficiary)
    db.commit()
    db.refresh(beneficiary)
    return beneficiary

@router.get("", response_model=List[BeneficiaryResponse])
def list_beneficiaries(
    district: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Beneficiary)
    if district:
        query = query.filter(Beneficiary.location_district.ilike(f"%{district}%"))
    if status:
        query = query.filter(Beneficiary.status == status)
    return query.order_by(Beneficiary.created_at.desc()).limit(limit).all()

@router.get("/{beneficiary_id}", response_model=BeneficiaryResponse)
def get_beneficiary(beneficiary_id: str, db: Session = Depends(get_db)):
    b = db.query(Beneficiary).filter(Beneficiary.id == beneficiary_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Beneficiary profile not found")
    return b

@router.put("/{beneficiary_id}", response_model=BeneficiaryResponse)
def update_beneficiary(beneficiary_id: str, payload: BeneficiaryUpdate, db: Session = Depends(get_db)):
    b = db.query(Beneficiary).filter(Beneficiary.id == beneficiary_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Beneficiary profile not found")
    
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(b, key, value)
        
    db.commit()
    db.refresh(b)
    return b
