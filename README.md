# SIH 2026 - AI Voice Assistant for Livelihood Mapping & NSQF Skill Recommendations

**Ministry:** Ministry of Social Justice and Empowerment  
**Scheme:** Pradhan Mantri Anusuchit Jaati Abhyuday Yojana (PM-AJAY) - Grants-in-Aid (GIA)  
**Theme:** Agriculture, FoodTech & Rural Development  
**Institution:** Silver Oak University, College of Technology

An AI-powered livelihood guidance and vocational recommendation platform designed for beneficiaries, field officers, and district-level administrators to discover suitable skill pathways, local livelihood opportunities, and training options aligned with NSQF standards.

---

## Overview

This project combines:

- A FastAPI backend for recommendation logic, beneficiary data management, and voice interactions
- A React + Vite frontend for district dashboards and beneficiary-facing workflows
- Multilingual voice support for low-literacy and field-based usage
- Deterministic recommendation scoring driven by verified NSQF and district opportunity datasets

The system is built to support PM-AJAY beneficiaries by recommending skill-linked livelihood pathways that are practical, region-specific, and actionable.

---

## Key Features

- Beneficiary profile intake and recommendation generation
- NSQF-aligned skill pathways and skill gap analysis
- Local opportunity mapping with wage and self-employment routes
- Voice-first interaction for multilingual assistance
- Training center and intervention tracking
- Admin dashboard for district-level monitoring and analytics
- Deterministic model logic to reduce hallucination risks

---

## Repository Structure

```text
SIH-2026/
├── backend/
│   ├── app/
│   │   ├── data/
│   │   │   ├── local_opportunities.json
│   │   │   ├── nsqf_catalog.json
│   │   │   └── seed.py
│   │   ├── models/
│   │   │   ├── beneficiary.py
│   │   │   ├── ground_intervention.py
│   │   │   ├── nsqf_job_role.py
│   │   │   ├── recommendation.py
│   │   │   ├── training_center.py
│   │   │   └── __init__.py
│   │   ├── routers/
│   │   │   ├── admin.py
│   │   │   ├── beneficiaries.py
│   │   │   ├── recommendations.py
│   │   │   └── voice.py
│   │   ├── schemas/
│   │   │   ├── beneficiary.py
│   │   │   ├── recommendation.py
│   │   │   ├── voice.py
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   ├── ai_agent.py
│   │   │   ├── recommendation_engine.py
│   │   │   └── skill_gap_engine.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   └── __init__.py
│   ├── .env.example
│   ├── requirements.txt
│   ├── test_engine.py
│   └── livelihood.db (generated locally)
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
├── .gitignore
├── test_tts.mp3
├── README.md
└── LICENSE (if added later)
```

---

## Tech Stack

- Backend: Python, FastAPI, SQLAlchemy, Pydantic
- AI/LLM Layer: Groq / OpenAI / Gemini-ready integration
- Voice: gTTS and conversational voice pipeline support
- Frontend: React, Vite, JavaScript
- Data Layer: JSON-backed catalog + SQLite for local MVP

---

## Local Development Setup

### 1. Backend Setup

Open PowerShell in the project root and run:

```powershell
cd backend

# Create a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt

# Copy the example environment file
Copy-Item .env.example .env

# Open .env and add your API key(s), especially GROQ_API_KEY
# Example:
# GROQ_API_KEY=your_key_here

# Run recommendation verification checks
python test_engine.py

# Start the backend server
uvicorn app.main:app --reload
```

After starting the server:

- API base: http://127.0.0.1:8000
- Swagger docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/api/health

### 2. Frontend Setup

Open a second terminal and run:

```powershell
cd frontend
npm install
npm run dev
```

After startup:

- Frontend app: http://localhost:5173

---

## Environment Variables

The backend loads environment variables from `backend/.env`.

Required for a basic MVP flow:

```env
DATABASE_URL=sqlite:///./livelihood.db
GROQ_API_KEY=
GEMINI_API_KEY=
OPENAI_API_KEY=
```

> Keep API keys local and do not commit `.env` files to Git.

---

## Design Principles

1. Deterministic recommendations powered by verified NSQF and local opportunity data
2. Clear action-oriented pathways for wage employment and self-employment
3. Voice-first access for low-literacy and on-ground deployment scenarios
4. Secure handling of keys and local environment configuration
5. District-relevant, scheme-aligned livelihood planning for PM-AJAY beneficiaries

---

## Team Contribution

| Member | Focus Area | Responsibilities |
|---|---|---|
| Hardik & Shubh | Core Technical Implementation | Backend, frontend, voice pipeline, recommendation engine, API integration |
| Kesha & Sheetal | Defense & Evaluation Prep | Technical defense, hallucination prevention, dataset validation, judge Q&A |
| Garvit & Chetan | PPT & Domain Research | Problem framing, metrics, slide deck, field-roadmap and project narrative |

---

## License

This project is intended for academic, hackathon, and demo use within the SIH 2026 context. Add a license file if you plan to publish it publicly or share it beyond the competition environment.

---

## Notes

This repository is structured as a local MVP and is ready to be extended with production-grade database integration, real beneficiary onboarding APIs, and deeper field-deployment workflows.
