import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

class Settings(BaseModel):
    PROJECT_NAME: str = "PM-AJAY GIA Livelihood & NSQF Skilling Assistant"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./livelihood.db")
    
    # LLM API Keys (Groq is recommended for free high-speed inference)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Configurable Recommendation Scoring Weights (Sum = 1.0)
    WEIGHT_EDUCATION: float = 0.20
    WEIGHT_SKILLS: float = 0.25
    WEIGHT_INTERESTS: float = 0.20
    WEIGHT_EXPERIENCE: float = 0.10
    WEIGHT_LOCAL_OPPORTUNITY: float = 0.15
    WEIGHT_PREFERENCE: float = 0.10
    
    # Default District Focus for PM-AJAY GIA Pilot (e.g. Gujarat & MP SC Clusters)
    DEFAULT_STATE: str = "Gujarat"
    DEFAULT_DISTRICT: str = "Ahmedabad"

settings = Settings()
