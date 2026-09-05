import re
from typing import List, Dict, Set, Tuple
from app.schemas.recommendation import SkillGapReport

STOP_WORDS = {
    "and", "or", "the", "in", "of", "for", "with", "at", "to", "a", "an",
    "basics", "basic", "skills", "usage", "operation", "handling", "work",
    "का", "के", "की", "में", "से", "पर", "और", "તથા", "અને", "માટે", "નું", "ના"
}

# Technical root word clusters across English, Hindi, and Gujarati
SKILL_STEMS = {
    "electric": ["electric", "electrical", "electrician", "wire", "wiring", "wireman", "circuit", "mcb", "earthing", "switchboard", "bijli", "voltage", "ઇલેક્ટ્રિક", "વાયરિંગ", "વીજળી", "बिजली", "वायर"],
    "solar": ["solar", "pv", "suryamitra", "inverter", "rooftop", "sun", "panel", "renewable", "સોલર", "સૂર્યમિત્ર", "सोलर", "सौर"],
    "tailor": ["tailor", "tailoring", "sewing", "stitch", "stitching", "needle", "needlework", "cloth", "garment", "fabric", "darji", "silai", "દરજી", "સિલાઈ", "सिलाई", "दर्जी", "कपड़ा"],
    "motor": ["motor", "pump", "engine", "two wheeler", "bike", "scooter", "mechanic", "automobile", "spanner", "garage", "વાહન", "બાઇક", "મિકેનિક", "मोटरसाइकिल", "गैरेज", "मैकेनिक"],
    "plumb": ["plumb", "plumber", "pipe", "fitting", "sanitary", "leak", "valve", "tap", "પાણી", "પ્લમ્બર", "पाइप", "प्लंबर", "नलसाजी"],
    "farm": ["farm", "farming", "crop", "agriculture", "farmer", "soil", "harvest", "kisan", "kheti", "ખેતી", "ખેડૂત", "खेती", "किसान", "फसल"],
    "dairy": ["dairy", "milk", "cattle", "cow", "buffalo", "ghee", "pashupalan", "પશુપાલન", "દૂધ", "ડેરી", "पशुपालन", "दूध", "डेयरी"],
    "mobile": ["mobile", "phone", "smartphone", "screen", "display", "pcb", "soldering", "મોબાઇલ", "ફોન", "मोबाइल", "फोन"],
    "computer": ["computer", "data", "entry", "csc", "typing", "digital", "internet", "software", "કમ્પ્યુટર", "ડેટા", "कंप्यूटर", "डाटा"],
    "construct": ["construct", "mason", "masonry", "brick", "cement", "concrete", "wall", "plaster", "ચણતર", "કડિયો", "चिनाई", "राजमिस्त्री", "भवन"],
    "weld": ["weld", "welder", "welding", "metal", "fabrication", "arc", "gas", "વેલ્ડિંગ", "ધાતુ", "वेल्डिंग", "वेल्डर", "धातु"],
    "health": ["health", "nurse", "nursing", "patient", "hospital", "clinic", "caregiver", "gda", "દવાખાનું", "નર્સિંગ", "अस्पताल", "नर्सिंग", "मरीज"]
}

def normalize_text(text: str) -> str:
    """Lowercase and strip unwanted punctuation while preserving devanagari & gujarati chars."""
    clean = re.sub(r'[^\w\s]', ' ', text.lower(), flags=re.UNICODE)
    return " ".join(clean.split()).strip()

def extract_keywords(phrase: str) -> Set[str]:
    """Extract significant keywords and stems from a skill or interest phrase."""
    norm = normalize_text(phrase)
    tokens = norm.split()
    stems = set()
    for t in tokens:
        if len(t) >= 2 and t not in STOP_WORDS:
            stems.add(t)
            # Add canonical group root if token belongs to a known technical stem
            for stem_group, members in SKILL_STEMS.items():
                if any(m in t or t in m for m in members):
                    stems.add(stem_group)
    return stems

def calculate_skill_overlap(user_skills: List[str], target_skills: List[str]) -> Tuple[List[str], List[str]]:
    """
    Returns (matched_target_skills, unmatched_target_skills)
    Checks keyword, substring, and technical stem overlaps between user's expressed skills and trade skills.
    """
    matched = []
    unmatched = []

    user_keywords_map = {us: extract_keywords(us) for us in user_skills}

    for req_skill in target_skills:
        req_norm = normalize_text(req_skill)
        req_keywords = extract_keywords(req_skill)
        is_match = False

        for user_skill, u_kw in user_keywords_map.items():
            u_norm = normalize_text(user_skill)
            # Direct exact or substring match
            if u_norm in req_norm or req_norm in u_norm:
                is_match = True
                break
            # Technical root or keyword intersection
            if req_keywords and u_kw:
                intersection = req_keywords.intersection(u_kw)
                if len(intersection) >= 1:
                    is_match = True
                    break

        if is_match:
            matched.append(req_skill)
        else:
            unmatched.append(req_skill)

    return matched, unmatched

class SkillGapEngine:
    @staticmethod
    def analyze(
        user_skills: List[str],
        core_skills_required: List[str],
        transferable_skills_catalog: List[str]
    ) -> Tuple[SkillGapReport, float]:
        """
        Analyzes the beneficiary's skills against a job role.
        Produces mathematically distinct readiness scores:
        - Exact core matches: high readiness (75-100)
        - Transferable matches: solid bridge readiness (50-75)
        - Zero overlap: low readiness (10-20), avoiding false equal-score floors.
        """
        if not user_skills:
            return SkillGapReport(
                matching_skills=[],
                missing_skills=core_skills_required,
                transferable_skills=[]
            ), 15.0 # Entry-level baseline for novice learner

        # 1. Match core skills
        matched_core, missing_core = calculate_skill_overlap(user_skills, core_skills_required)

        # 2. Match transferable skills (from job role's transferable list)
        matched_transferable, _ = calculate_skill_overlap(user_skills, transferable_skills_catalog)

        # 3. Calculate mathematically distinct skill score
        total_core = max(len(core_skills_required), 1)
        core_ratio = len(matched_core) / total_core

        total_trans = max(len(transferable_skills_catalog), 1)
        trans_ratio = len(matched_transferable) / total_trans

        if matched_core or matched_transferable:
            # Candidate has direct or adjacent competencies
            core_pts = core_ratio * 60.0
            trans_pts = trans_ratio * 25.0
            readiness_bonus = 15.0 if matched_core else (10.0 if matched_transferable else 0.0)
            raw_score = 20.0 + core_pts + trans_pts + readiness_bonus
        else:
            # Unrelated trade: candidate has prior skills in a different domain
            # Score must remain distinctly low (10 to 18 pts) to prevent equal score anomalies
            raw_score = 10.0 + min(len(user_skills) * 2.0, 8.0)

        final_skill_score = min(max(raw_score, 10.0), 98.0)

        # Combine matched core and matched transferable so report is transparent
        displayed_matches = list(matched_core)
        for ts in matched_transferable:
            if ts not in displayed_matches:
                displayed_matches.append(f"{ts} (transferable)")

        report = SkillGapReport(
            matching_skills=displayed_matches,
            missing_skills=missing_core,
            transferable_skills=matched_transferable
        )

        return report, round(final_skill_score, 1)

skill_gap_engine = SkillGapEngine()

