import sys
sys.stdout.reconfigure(encoding='utf-8')
from app.database import SessionLocal
from app.models.beneficiary import Beneficiary
from app.models.nsqf_job_role import NSQFJobRole
from app.models.training_center import TrainingCenter
from app.services.recommendation_engine import recommendation_engine

def run_test():
    db = SessionLocal()
    try:
        roles = db.query(NSQFJobRole).all()
        centers = db.query(TrainingCenter).all()
        print(f"Loaded Catalog: {len(roles)} NSQF Job Roles, {len(centers)} PM-AJAY Training Centers\n")

        test_cases = [
            ("Ramesh Solanki", "Rural solar & electrical worker"),
            ("Sunita Vaghela", "Women artisan tailoring & sewing"),
            ("Dinesh Rathod", "Masonry worker with physical mobility constraint / knee injury"),
            ("Prakash Parmar", "Youth seeking mobile & electronic security career")
        ]

        for name, profile_desc in test_cases:
            person = db.query(Beneficiary).filter_by(name=name).first()
            if not person:
                continue

            results = recommendation_engine.evaluate_beneficiary(person, roles, centers, top_k=3)
            print(f"============================================================")
            print(f"BENEFICIARY: {person.name} ({profile_desc})")
            print(f"Edu: {person.education_level} | Skills: {person.existing_skills} | Interests: {person.interests} | Mobility Constrained: {person.has_mobility_constraint}")
            print(f"------------------------------------------------------------")
            for rec in results:
                print(f"  Rank {rec.rank}: {rec.trade_title} (NSQF Level {rec.nsqf_level}) - Score: {rec.overall_match_score}%")
                print(f"    Breakdown: Edu={rec.score_breakdown.weighted_education} | Skill={rec.score_breakdown.weighted_skill} | Int={rec.score_breakdown.weighted_interest} | Loc={rec.score_breakdown.weighted_local_opportunity}")
                print(f"    Matching skills: {rec.skill_gap.matching_skills}")
                print(f"    Nearest Center: {rec.nearby_training_centers[0].name if rec.nearby_training_centers else 'State Center'}")
                print(f"    Wage Route: {rec.wage_route.job_role} ({rec.wage_route.starting_salary_range})")
                print(f"    Self-Emp Route: {rec.self_employment_route.enterprise_name} ({rec.self_employment_route.pm_ajay_grant_support})\n")

    finally:
        db.close()

if __name__ == "__main__":
    run_test()

