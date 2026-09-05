import json
import os
from sqlalchemy.orm import Session
from app.database import Base, engine, SessionLocal
from app.models.nsqf_job_role import NSQFJobRole
from app.models.training_center import TrainingCenter
from app.models.beneficiary import Beneficiary
from app.models.ground_intervention import GroundIntervention

DATA_DIR = os.path.dirname(__file__)

def seed_database(db: Session = None):
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    try:
        # 1. Seed / Refresh NSQF Job Roles
        catalog_path = os.path.join(DATA_DIR, "nsqf_catalog.json")
        if os.path.exists(catalog_path):
            with open(catalog_path, "r", encoding="utf-8") as f:
                roles_data = json.load(f)
                for item in roles_data:
                    existing = db.query(NSQFJobRole).filter(NSQFJobRole.id == item["id"]).first()
                    kw = item.get("keywords", [])
                    if existing:
                        existing.sector = item["sector"]
                        existing.trade_title = item["trade_title"]
                        existing.trade_title_hi = item.get("trade_title_hi")
                        existing.trade_title_gu = item.get("trade_title_gu")
                        existing.nsqf_level = item["nsqf_level"]
                        existing.min_education = item["min_education"]
                        existing.training_duration_hours = item.get("training_duration_hours", 300)
                        existing.mobility_required = item.get("mobility_required")
                        existing.core_skills = item.get("core_skills", [])
                        existing.transferable_skills = item.get("transferable_skills", [])
                        existing.interests = kw
                        existing.keywords = kw
                        existing.wage_route = item.get("wage_route", {})
                        existing.self_employment_route = item.get("self_employment_route", {})
                    else:
                        job_role = NSQFJobRole(
                            id=item["id"],
                            sector=item["sector"],
                            trade_title=item["trade_title"],
                            trade_title_hi=item.get("trade_title_hi"),
                            trade_title_gu=item.get("trade_title_gu"),
                            nsqf_level=item["nsqf_level"],
                            min_education=item["min_education"],
                            training_duration_hours=item.get("training_duration_hours", 300),
                            mobility_required=item.get("mobility_required"),
                            core_skills=item.get("core_skills", []),
                            transferable_skills=item.get("transferable_skills", []),
                            interests=kw,
                            keywords=kw,
                            wage_route=item.get("wage_route", {}),
                            self_employment_route=item.get("self_employment_route", {}),
                        )
                        db.add(job_role)
                db.commit()
                print(f"Successfully seeded/refreshed {len(roles_data)} NSQF job roles.")

        # 2. Seed / Refresh Training Centers
        opp_path = os.path.join(DATA_DIR, "local_opportunities.json")
        if os.path.exists(opp_path):
            with open(opp_path, "r", encoding="utf-8") as f:
                opp_data = json.load(f)
                for tc in opp_data.get("training_centers", []):
                    existing = db.query(TrainingCenter).filter(TrainingCenter.id == tc["id"]).first()
                    if existing:
                        existing.courses_offered = tc.get("courses_offered", [])
                        existing.available_seats = tc.get("available_seats", 30)
                        existing.free_daily_stipend_inr = tc.get("free_daily_stipend_inr", 150)
                    else:
                        center = TrainingCenter(
                            id=tc["id"],
                            name=tc["name"],
                            state=tc.get("state", "Gujarat"),
                            district=tc.get("district", "Ahmedabad"),
                            block=tc.get("block"),
                            address=tc.get("address"),
                            distance_km_from_center=tc.get("distance_km_from_center", 10),
                            contact_person=tc.get("contact_person"),
                            phone=tc.get("phone"),
                            affiliated_scheme=tc.get("affiliated_scheme", "PM-AJAY GIA"),
                            courses_offered=tc.get("courses_offered", []),
                            available_seats=tc.get("available_seats", 30),
                            free_hostel_available=tc.get("free_hostel_available", False),
                            free_daily_stipend_inr=tc.get("free_daily_stipend_inr", 150),
                            free_uniform_and_toolkit=tc.get("free_uniform_and_toolkit", True),
                            next_batch_date=tc.get("next_batch_date"),
                        )
                        db.add(center)
                db.commit()
                print("Successfully seeded/refreshed training centers.")

        # 3. Seed / Refresh Realistic Demo Beneficiaries for Admin Dashboard Live Demonstration
        sample_beneficiaries = [
            {
                "name": "Ramesh Solanki",
                "phone_number": "+91 98251 12345",
                "language_preference": "gu",
                "age": 24,
                "gender": "Male",
                "education_level": "10th Pass",
                "location_state": "Gujarat",
                "location_district": "Ahmedabad",
                "location_block": "Viramgam",
                "max_travel_distance_km": 20,
                "has_mobility_constraint": False,
                "family_occupation": "Agricultural Labor",
                "current_livelihood": "Daily Wage Farm Worker",
                "work_experience_years": 2.5,
                "existing_skills": ["basic electrical work", "hand tool usage", "physical fitness"],
                "interests": ["solar systems", "electrical appliances"],
                "livelihood_preference": "Both",
                "status": "In Training"
            },
            {
                "name": "Sunita Vaghela",
                "phone_number": "+91 97241 88921",
                "language_preference": "hi",
                "age": 29,
                "gender": "Female",
                "education_level": "8th Pass",
                "location_state": "Gujarat",
                "location_district": "Ahmedabad",
                "location_block": "Dholka",
                "max_travel_distance_km": 5,
                "has_mobility_constraint": False,
                "family_occupation": "Weaving & Tailoring",
                "current_livelihood": "Home Alteration Sewing",
                "work_experience_years": 4.0,
                "existing_skills": ["hand needlework", "cloth cutting", "color matching"],
                "interests": ["sewing", "fashion and clothing", "home business"],
                "livelihood_preference": "Self Employment",
                "status": "Certified"
            },
            {
                "name": "Prakash Parmar",
                "phone_number": "+91 94280 65112",
                "language_preference": "gu",
                "age": 21,
                "gender": "Male",
                "education_level": "12th Pass",
                "location_state": "Gujarat",
                "location_district": "Vadodara",
                "location_block": "Savli",
                "max_travel_distance_km": 15,
                "has_mobility_constraint": False,
                "family_occupation": "Leather Craft",
                "current_livelihood": "Shop Assistant",
                "work_experience_years": 1.0,
                "existing_skills": ["basic computer literacy", "wire twisting", "hand tool usage"],
                "interests": ["mobile phones", "electronics repair"],
                "livelihood_preference": "Wage Employment",
                "status": "Placed"
            },
            {
                "name": "Manjula Makwana",
                "phone_number": "+91 99092 34189",
                "language_preference": "gu",
                "age": 34,
                "gender": "Female",
                "education_level": "Below 8th",
                "location_state": "Gujarat",
                "location_district": "Anand",
                "location_block": "Petlad",
                "max_travel_distance_km": 8,
                "has_mobility_constraint": False,
                "family_occupation": "Farming & Animal Husbandry",
                "current_livelihood": "Cattle Grazer",
                "work_experience_years": 8.0,
                "existing_skills": ["livestock rearing", "cow buffalo handling", "fodder cutting"],
                "interests": ["dairy animals", "milk business"],
                "livelihood_preference": "Self Employment",
                "status": "Self Employed"
            },
            {
                "name": "Dinesh Rathod",
                "phone_number": "+91 98981 77234",
                "language_preference": "hi",
                "age": 38,
                "gender": "Male",
                "education_level": "Below 8th",
                "location_state": "Gujarat",
                "location_district": "Ahmedabad",
                "location_block": "Daskroi",
                "max_travel_distance_km": 10,
                "has_mobility_constraint": True,
                "family_occupation": "Construction Labor",
                "current_livelihood": "Masonry Helper",
                "work_experience_years": 12.0,
                "existing_skills": ["trowel usage", "sand cement mixing", "physical endurance"],
                "interests": ["building construction", "house renovation"],
                "livelihood_preference": "Wage Employment",
                "status": "Intervention Needed"
            },
            {
                "name": "Kavita Chauhan",
                "phone_number": "+91 97123 44019",
                "language_preference": "en",
                "age": 22,
                "gender": "Female",
                "education_level": "10th Pass",
                "location_state": "Gujarat",
                "location_district": "Ahmedabad",
                "location_block": "Viramgam",
                "max_travel_distance_km": 25,
                "has_mobility_constraint": False,
                "family_occupation": "Poultry & Farming",
                "current_livelihood": "Unemployed",
                "work_experience_years": 0.5,
                "existing_skills": ["caregiving", "cleanliness maintenance", "empathy and communication"],
                "interests": ["healthcare", "patient care", "nursing assistance"],
                "livelihood_preference": "Wage Employment",
                "status": "In Training"
            },
            {
                "name": "Jignesh Chavda",
                "phone_number": "+91 98244 55198",
                "language_preference": "gu",
                "age": 26,
                "gender": "Male",
                "education_level": "8th Pass",
                "location_state": "Gujarat",
                "location_district": "Vadodara",
                "location_block": "Savli",
                "max_travel_distance_km": 15,
                "has_mobility_constraint": False,
                "family_occupation": "Blacksmith & Metalwork",
                "current_livelihood": "Garage Helper",
                "work_experience_years": 3.0,
                "existing_skills": ["spanner and socket tool usage", "greasing and lubrication", "cycle repair"],
                "interests": ["motorcycles and scooters", "mechanical engines"],
                "livelihood_preference": "Self Employment",
                "status": "Profiled"
            }
        ]
        for item in sample_beneficiaries:
            existing_b = db.query(Beneficiary).filter_by(name=item["name"]).first()
            if existing_b:
                for k, v in item.items():
                    setattr(existing_b, k, v)
            else:
                b = Beneficiary(**item)
                db.add(b)
        db.commit()

        # Add sample ground intervention for Dinesh Rathod
        dinesh = db.query(Beneficiary).filter_by(name="Dinesh Rathod").first()
        if dinesh and db.query(GroundIntervention).filter_by(beneficiary_id=dinesh.id).count() == 0:
            intervention = GroundIntervention(
                beneficiary_id=dinesh.id,
                intervention_type="Mobility Support & Tool-kit Grant",
                assigned_officer_name="Shri J. P. Rathod (Welfare Officer)",
                assigned_officer_phone="+91 79265 89011",
                priority="High",
                status="Open",
                notes="Beneficiary injured left knee during masonry work. Needs mobility aid and shift to light indoor skilling or PM-AJAY GIA toolkit support."
            )
            db.add(intervention)
            db.commit()

        print("Successfully seeded realistic demo beneficiaries and intervention tickets.")

    finally:
        if should_close:
            db.close()

if __name__ == "__main__":
    seed_database()
