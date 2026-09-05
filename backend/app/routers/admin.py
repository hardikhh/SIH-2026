from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.beneficiary import Beneficiary
from app.models.ground_intervention import GroundIntervention

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

class InterventionCreate(BaseModel):
    beneficiary_id: str
    intervention_type: str
    assigned_officer_name: Optional[str] = "District PM-AJAY Field Coordinator"
    assigned_officer_phone: Optional[str] = "+91 98251 00000"
    priority: Optional[str] = "Medium"
    notes: Optional[str] = None

class InterventionUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None

@router.get("/kpis")
def get_admin_kpis(db: Session = Depends(get_db)):
    total = db.query(Beneficiary).count()
    profiled = db.query(Beneficiary).filter(Beneficiary.status == "Profiled").count()
    in_training = db.query(Beneficiary).filter(Beneficiary.status == "In Training").count()
    certified = db.query(Beneficiary).filter(Beneficiary.status == "Certified").count()
    placed = db.query(Beneficiary).filter(Beneficiary.status == "Placed").count()
    self_employed = db.query(Beneficiary).filter(Beneficiary.status == "Self Employed").count()
    interventions_needed = db.query(Beneficiary).filter(Beneficiary.status == "Intervention Needed").count()
    open_tickets = db.query(GroundIntervention).filter(GroundIntervention.status != "Resolved").count()

    # Estimated PM-AJAY GIA grant disbursement calculation (₹50,000 per self-employed + ₹25,000 toolkits)
    estimated_grant_inr = (self_employed * 50000) + (certified * 25000)

    return {
        "total_beneficiaries": total,
        "profiled": profiled,
        "in_training": in_training,
        "certified": certified,
        "placed": placed,
        "self_employed": self_employed,
        "interventions_needed": interventions_needed,
        "open_tickets": open_tickets,
        "placement_rate_percent": round((placed / total * 100), 1) if total > 0 else 0,
        "estimated_grant_disbursed_inr": estimated_grant_inr,
        "scheme": "PM-AJAY Grant-in-Aid (GIA) Component",
        "last_updated": datetime.utcnow().isoformat(),
    }

@router.get("/districts")
def get_district_analytics(db: Session = Depends(get_db)):
    results = db.query(
        Beneficiary.location_district,
        func.count(Beneficiary.id).label("total"),
        Beneficiary.status
    ).group_by(Beneficiary.location_district, Beneficiary.status).all()

    district_map = {}
    for district, count, status in results:
        dist_name = district or "Ahmedabad"
        if dist_name not in district_map:
            district_map[dist_name] = {
                "district": dist_name,
                "total": 0,
                "in_training": 0,
                "certified": 0,
                "placed": 0,
                "self_employed": 0,
                "intervention_needed": 0,
            }
        district_map[dist_name]["total"] += count
        if status == "In Training":
            district_map[dist_name]["in_training"] += count
        elif status == "Certified":
            district_map[dist_name]["certified"] += count
        elif status == "Placed":
            district_map[dist_name]["placed"] += count
        elif status == "Self Employed":
            district_map[dist_name]["self_employed"] += count
        elif status == "Intervention Needed":
            district_map[dist_name]["intervention_needed"] += count

    return list(district_map.values())

@router.get("/interventions")
def list_interventions(db: Session = Depends(get_db)):
    interventions = db.query(GroundIntervention).order_by(GroundIntervention.created_at.desc()).all()
    results = []
    for item in interventions:
        b = db.query(Beneficiary).filter(Beneficiary.id == item.beneficiary_id).first()
        results.append({
            "id": item.id,
            "beneficiary_id": item.beneficiary_id,
            "beneficiary_name": b.name if b else "Unknown",
            "beneficiary_phone": b.phone_number if b else "N/A",
            "beneficiary_district": b.location_district if b else "N/A",
            "intervention_type": item.intervention_type,
            "assigned_officer_name": item.assigned_officer_name,
            "assigned_officer_phone": item.assigned_officer_phone,
            "priority": item.priority,
            "status": item.status,
            "notes": item.notes,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "resolved_at": item.resolved_at.isoformat() if item.resolved_at else None,
        })
    return results

@router.post("/interventions")
def create_intervention(payload: InterventionCreate, db: Session = Depends(get_db)):
    ticket = GroundIntervention(**payload.model_dump())
    db.add(ticket)
    # Update beneficiary status to Intervention Needed
    b = db.query(Beneficiary).filter(Beneficiary.id == payload.beneficiary_id).first()
    if b:
        b.status = "Intervention Needed"
    db.commit()
    db.refresh(ticket)
    return ticket

@router.put("/interventions/{ticket_id}")
def update_intervention(ticket_id: str, payload: InterventionUpdate, db: Session = Depends(get_db)):
    ticket = db.query(GroundIntervention).filter(GroundIntervention.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Intervention ticket not found")

    if payload.status:
        ticket.status = payload.status
        if payload.status == "Resolved":
            ticket.resolved_at = datetime.utcnow()
    if payload.priority:
        ticket.priority = payload.priority
    if payload.notes:
        ticket.notes = payload.notes

    db.commit()
    db.refresh(ticket)
    return ticket
