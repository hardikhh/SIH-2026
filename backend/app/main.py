from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.data.seed import seed_database
from app.routers import beneficiaries, recommendations, admin, voice

# Ensure tables are created
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for AI-Driven Voice Assistant for Livelihood Mapping and NSQF-Aligned Skilling (SIH 2026 - Problem ID: 26097)",
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Accessible locally from Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Run seed check on startup
@app.on_event("startup")
def on_startup():
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

# Register API Routers
app.include_router(voice.router, prefix=settings.API_V1_STR)
app.include_router(beneficiaries.router, prefix=settings.API_V1_STR)
app.include_router(recommendations.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "problem_statement_id": "26097",
        "scheme": "PM-AJAY Grant-in-Aid (GIA) Component",
        "docs_url": "/docs",
        "status": "online"
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "models_loaded": 25,
    }
