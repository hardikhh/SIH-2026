from app.database import Base
from app.models.beneficiary import Beneficiary
from app.models.nsqf_job_role import NSQFJobRole
from app.models.recommendation import Recommendation
from app.models.training_center import TrainingCenter
from app.models.ground_intervention import GroundIntervention

__all__ = [
    "Base",
    "Beneficiary",
    "NSQFJobRole",
    "Recommendation",
    "TrainingCenter",
    "GroundIntervention",
]
