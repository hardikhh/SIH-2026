import os
import json
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.config import settings
from app.models.nsqf_job_role import NSQFJobRole
from app.models.training_center import TrainingCenter
from app.models.beneficiary import Beneficiary
from app.schemas.recommendation import (
    ScoreBreakdown,
    RecommendationItem,
    RecommendationResponse,
    NearbyTrainingCenter,
    LocalJobVacancy,
    WageRoute,
    SelfEmploymentRoute,
)
from app.services.skill_gap_engine import skill_gap_engine, normalize_text, extract_keywords

# Hierarchical education levels mapping
EDUCATION_LEVELS = {
    "no formal education": 1,
    "none": 1,
    "below 8th": 2,
    "5th pass": 2,
    "primary": 2,
    "8th pass": 3,
    "middle school": 3,
    "10th pass": 4,
    "matric": 4,
    "secondary": 4,
    "12th pass": 5,
    "higher secondary": 5,
    "iti": 6,
    "diploma": 6,
    "graduate": 7,
    "post graduate": 8
}

def get_edu_score(beneficiary_edu: str, min_required: str) -> float:
    b_val = EDUCATION_LEVELS.get(normalize_text(beneficiary_edu or "below 8th"), 2)
    r_val = EDUCATION_LEVELS.get(normalize_text(min_required or "below 8th"), 2)

    if b_val >= r_val:
        return 100.0
    elif b_val == r_val - 1:
        # 1 level below: RPL (Recognition of Prior Learning) bridge pathway in PM-AJAY
        return 75.0
    elif b_val == r_val - 2:
        return 50.0
    else:
        return 30.0

def get_interest_score(user_interests: List[str], role: NSQFJobRole) -> float:
    if not user_interests:
        return 55.0 # Neutral baseline for unspecified interests

    user_kw = set()
    user_norms = []
    for item in user_interests:
        u_norm = normalize_text(item)
        user_norms.append(u_norm)
        user_kw.update(extract_keywords(item))

    # Compile comprehensive trade keywords & titles across languages
    trade_kw = set()
    trade_texts = [
        role.trade_title or "",
        role.trade_title_hi or "",
        role.trade_title_gu or "",
        role.sector or "",
    ]
    for txt in trade_texts:
        trade_kw.update(extract_keywords(txt))

    keywords_list = getattr(role, 'keywords', []) or role.interests or []
    for kw in keywords_list:
        trade_kw.update(extract_keywords(kw))

    for cs in (role.core_skills or []):
        trade_kw.update(extract_keywords(cs))

    # Check for direct phrase containment
    direct_title_match = False
    title_norm = normalize_text(f"{role.trade_title} {role.trade_title_hi or ''} {role.trade_title_gu or ''}")
    for u_n in user_norms:
        if len(u_n) > 2 and (u_n in title_norm or any(u_n in normalize_text(kw) for kw in keywords_list)):
            direct_title_match = True
            break

    intersection = user_kw.intersection(trade_kw)

    if direct_title_match:
        return 98.0
    elif len(intersection) >= 3:
        return 95.0
    elif len(intersection) == 2:
        return 88.0
    elif len(intersection) == 1:
        return 78.0
    else:
        # Unrelated trade
        return 15.0

def get_experience_score(years: float) -> float:
    if years >= 4.0:
        return 100.0
    elif years >= 2.0:
        return 85.0
    elif years >= 1.0:
        return 70.0
    elif years > 0.0:
        return 60.0
    return 50.0 # Novice baseline

def get_preference_score(preference: str, wage_route: Dict, self_emp_route: Dict) -> float:
    pref_norm = normalize_text(preference or "both")
    if "both" in pref_norm:
        return 95.0
    elif "wage" in pref_norm or "job" in pref_norm or "salary" in pref_norm:
        # High score if trade has verified starting salary & known employers
        return 100.0 if wage_route.get("job_role") else 75.0
    elif "self" in pref_norm or "business" in pref_norm or "shop" in pref_norm or "own" in pref_norm:
        # High score if trade has PM-AJAY GIA grant support
        return 100.0 if self_emp_route.get("pm_ajay_grant_support") else 75.0
    return 80.0

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

class RecommendationEngine:
    def __init__(self):
        self.w_edu = settings.WEIGHT_EDUCATION
        self.w_skill = settings.WEIGHT_SKILLS
        self.w_int = settings.WEIGHT_INTERESTS
        self.w_exp = settings.WEIGHT_EXPERIENCE
        self.w_loc = settings.WEIGHT_LOCAL_OPPORTUNITY
        self.w_pref = settings.WEIGHT_PREFERENCE
        self.vacancies = []
        self._load_local_data()

    def _load_local_data(self):
        opp_path = os.path.join(DATA_DIR, "local_opportunities.json")
        if os.path.exists(opp_path):
            try:
                with open(opp_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.vacancies = data.get("local_job_vacancies", [])
            except Exception as e:
                print(f"Error loading vacancies: {e}")

    def evaluate_beneficiary(
        self,
        beneficiary: Beneficiary,
        all_job_roles: List[NSQFJobRole],
        training_centers: List[TrainingCenter],
        top_k: int = 3
    ) -> List[RecommendationItem]:
        scored_candidates = []

        b_district = (beneficiary.location_district or "Ahmedabad").lower()
        max_dist = beneficiary.max_travel_distance_km or 15
        has_mobility_constraint = beneficiary.has_mobility_constraint

        for role in all_job_roles:
            # 1. Skill Gap Analysis
            skill_gap_report, raw_skill_score = skill_gap_engine.analyze(
                user_skills=beneficiary.existing_skills or [],
                core_skills_required=role.core_skills or [],
                transferable_skills_catalog=role.transferable_skills or []
            )

            # 2. Education Score
            raw_edu_score = get_edu_score(beneficiary.education_level, role.min_education)

            # 3. Interest Score
            raw_int_score = get_interest_score(beneficiary.interests or [], role)

            # 4. Experience Score
            raw_exp_score = get_experience_score(beneficiary.work_experience_years or 0.0)

            # 5. Local Opportunity Score & Center Matching
            matching_centers = []
            loc_score = 40.0 # Base

            for tc in training_centers:
                courses = tc.courses_offered or []
                if role.id in courses:
                    tc_dist = tc.distance_km_from_center or 10
                    is_same_district = (tc.district or "").lower() == b_district

                    if is_same_district:
                        loc_score = max(loc_score, 80.0)
                        if tc_dist <= max_dist:
                            loc_score = 100.0

                    b_state = (beneficiary.location_state or "Gujarat").lower()
                    tc_state = (tc.state or "").lower()
                    is_same_state = tc_state == b_state

                    center_obj = NearbyTrainingCenter(
                        id=tc.id,
                        name=tc.name,
                        state=tc.state,
                        district=tc.district,
                        block=tc.block,
                        distance_km=tc_dist,
                        address=tc.address,
                        contact_person=tc.contact_person,
                        phone=tc.phone,
                        available_seats=tc.available_seats,
                        free_hostel=tc.free_hostel_available,
                        free_daily_stipend_inr=tc.free_daily_stipend_inr,
                        next_batch_date=tc.next_batch_date,
                    )

                    # Tiered center prioritization:
                    # 1. Exact same district (Highest priority)
                    # 2. Same state
                    # 3. Other states (only if no same state centers found)
                    if is_same_district:
                        matching_centers.insert(0, center_obj)
                    elif is_same_state:
                        # Insert before other states but after same district
                        district_count = sum(1 for c in matching_centers if (c.district or "").lower() == b_district)
                        matching_centers.insert(district_count, center_obj)
                    else:
                        matching_centers.append(center_obj)

            # Filter out cross-state centers if we already have centers in the beneficiary's home state!
            b_state = (beneficiary.location_state or "Gujarat").lower()
            same_state_centers = [c for c in matching_centers if (c.state or "").lower() == b_state]
            if same_state_centers:
                matching_centers = same_state_centers

            # Fallback: If no center currently lists this exact course code, assign their district's own PM-AJAY Academy!
            # Under PM-AJAY GIA, district academies enroll demand-driven batches.
            if not matching_centers:
                for tc in training_centers:
                    if (tc.district or "").lower() == b_district:
                        matching_centers.append(
                            NearbyTrainingCenter(
                                id=tc.id,
                                name=tc.name,
                                state=tc.state,
                                district=tc.district,
                                block=tc.block,
                                distance_km=tc.distance_km_from_center or 8,
                                address=tc.address,
                                contact_person=tc.contact_person,
                                phone=tc.phone,
                                available_seats=tc.available_seats,
                                free_hostel=tc.free_hostel_available,
                                free_daily_stipend_inr=tc.free_daily_stipend_inr,
                                next_batch_date=tc.next_batch_date,
                            )
                        )
                        break

            # Match local vacancies for this job role strictly prioritizing beneficiary's district, then same state
            matching_vacancies = []
            for v in self.vacancies:
                if v.get("job_role_id") == role.id:
                    v_dist = (v.get("district") or "").lower()
                    v_state = (v.get("state") or "").lower()
                    if v_dist == b_district:
                        matching_vacancies.insert(0, LocalJobVacancy(**v))
                    elif v_state == b_state:
                        matching_vacancies.append(LocalJobVacancy(**v))

            # If there are open vacancies in beneficiary's district, give a boost to local opportunity score
            if any((v.district or "").lower() == b_district for v in matching_vacancies):
                loc_score = min(loc_score + 25.0, 100.0)
            elif matching_vacancies:
                loc_score = min(loc_score + 10.0, 90.0)

            # 6. Preference Score
            raw_pref_score = get_preference_score(
                beneficiary.livelihood_preference,
                role.wage_route or {},
                role.self_employment_route or {}
            )

            # Calculate weighted composite score
            weighted_edu = round(raw_edu_score * self.w_edu, 2)
            weighted_skill = round(raw_skill_score * self.w_skill, 2)
            weighted_int = round(raw_int_score * self.w_int, 2)
            weighted_exp = round(raw_exp_score * self.w_exp, 2)
            weighted_loc = round(loc_score * self.w_loc, 2)
            weighted_pref = round(raw_pref_score * self.w_pref, 2)

            total_match_score = round(
                weighted_edu + weighted_skill + weighted_int + weighted_exp + weighted_loc + weighted_pref, 1
            )

            # Mobility Constraint adjustment (Protects PwD and physical mobility limitations)
            mobility_req = (role.mobility_required or "").lower()
            if has_mobility_constraint:
                if any(w in mobility_req for w in ["sedentary", "low", "home", "indoor", "desk", "bench", "seated"]):
                    total_match_score = min(total_match_score + 15.0, 99.0) # Boost accessible trades
                elif any(w in mobility_req for w in ["high", "rooftop", "climbing", "heavy", "field", "strenuous"]):
                    total_match_score = max(total_match_score - 35.0, 10.0) # Strong penalty for hazardous/strenuous roles

            score_breakdown = ScoreBreakdown(
                education_score=raw_edu_score,
                skill_score=raw_skill_score,
                interest_score=raw_int_score,
                experience_score=raw_exp_score,
                local_opportunity_score=loc_score,
                preference_score=raw_pref_score,
                weighted_education=weighted_edu,
                weighted_skill=weighted_skill,
                weighted_interest=weighted_int,
                weighted_experience=weighted_exp,
                weighted_local_opportunity=weighted_loc,
                weighted_preference=weighted_pref,
            )

            # Build explainable summaries
            exp_en = self._generate_explanation(beneficiary, role, skill_gap_report, "en")
            exp_hi = self._generate_explanation(beneficiary, role, skill_gap_report, "hi")
            exp_gu = self._generate_explanation(beneficiary, role, skill_gap_report, "gu")

            candidate = RecommendationItem(
                rank=0, # Populated after sorting
                job_role_id=role.id,
                sector=role.sector,
                trade_title=role.trade_title,
                trade_title_hi=role.trade_title_hi,
                trade_title_gu=role.trade_title_gu,
                nsqf_level=role.nsqf_level,
                min_education=role.min_education,
                training_duration_hours=role.training_duration_hours,
                overall_match_score=min(total_match_score, 98.5),
                score_breakdown=score_breakdown,
                skill_gap=skill_gap_report,
                wage_route=WageRoute(**(dict(role.wage_route) if isinstance(role.wage_route, dict) else {})),
                self_employment_route=SelfEmploymentRoute(**(dict(role.self_employment_route) if isinstance(role.self_employment_route, dict) else {})),
                nearby_training_centers=matching_centers[:2],
                local_vacancies=matching_vacancies[:2],
                explanation_hi=exp_hi,
                explanation_gu=exp_gu,
                explanation_en=exp_en,
            )
            scored_candidates.append(candidate)

        # Sort descending by match score
        scored_candidates.sort(key=lambda x: x.overall_match_score, reverse=True)

        # Assign ranks
        for i, item in enumerate(scored_candidates[:top_k]):
            item.rank = i + 1

        return scored_candidates[:top_k]

    def _generate_explanation(
        self,
        b: Beneficiary,
        r: NSQFJobRole,
        gap: Any,
        lang: str
    ) -> str:
        matching_count = len(gap.matching_skills)
        missing_count = len(gap.missing_skills)
        hours = r.training_duration_hours

        district_name = b.location_district or "आपके जिले"

        if lang == "hi":
            title = r.trade_title_hi or r.trade_title
            if matching_count > 0:
                return (
                    f"यह ट्रेड आपके पिछले हुनर और {district_name} में उपलब्ध अवसरों से काफी मेल खाता है। आपके पास {matching_count} हुनर पहले से हैं। "
                    f"केवल {missing_count} नए हुनर सीखने के लिए PM-AJAY के अंतर्गत {hours} घंटे की निःशुल्क NSQF ट्रेनिंग, स्टाइपेंड और टूलकिट मिलेगी।"
                )
            else:
                return (
                    f"आपकी रुचि और {district_name} के स्थानीय अवसरों के अनुसार {title} एक बेहतरीन आजीविका विकल्प है। "
                    f"PM-AJAY GIA के तहत {hours} घंटे का निःशुल्क प्रशिक्षण व ₹50,000 तक स्वरोजगार सहायता उपलब्ध है।"
                )
        elif lang == "gu":
            title = r.trade_title_gu or r.trade_title
            if matching_count > 0:
                return (
                    f"આ ટ્રેડ તમારા અનુભવ સાથે ખુબ સારો મેળ ખાય છે. તમારી પાસે {matching_count} કૌશલ્ય પહેલેથી છે. "
                    f"બાકીના {missing_count} કૌશલ્ય માટે PM-AJAY હેઠળ {hours} કલાકની મફત NSQF તાલીમ અને ટૂલકિટ મળશે."
                )
            else:
                return (
                    f"તમારા રસ અને સ્થાનિક માંગ મુજબ {title} એક ઉત્તમ આજીવિકા માર્ગ છે. "
                    f"PM-AJAY GIA હેઠળ {hours} કલાકની મફત તાલીમ અને ₹50,000 સુધીની સ્વરોજગાર સહાય ઉપલબ્ધ છે."
                )
        else:
            if matching_count > 0:
                return (
                    f"Strong alignment with your background. You already possess {matching_count} matching skills. "
                    f"Only {missing_count} additional skills needed through a free {hours}-hour NSQF training under PM-AJAY with stipend and starter toolkit."
                )
            else:
                return (
                    f"Excellent fit for your interests and local district demand. "
                    f"Eligible for free {hours}-hour NSQF certified training and up to ₹50,000 PM-AJAY GIA micro-enterprise grant."
                )

recommendation_engine = RecommendationEngine()
