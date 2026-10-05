# FoodWise AI – Smart Food Waste Reduction & Meal Planner

AI/ML internship project aligned with **UN SDG 12: Responsible Consumption and Production**.

FoodWise helps users track food items, estimate expiry/waste risk using a machine-learning model, and get practical meal suggestions from ingredients that should be used soon.

## Main features
- Responsive navbar and mobile-first dashboard
- Add and track food inventory
- ML-based expiry/waste risk prediction
- Risk score with Low / Medium / High classification
- Smart recipe suggestions from available ingredients
- Waste analytics dashboard
- SQLite persistence
- FastAPI REST API
- React + Vite frontend
- Render-ready deployment configuration

## Tech stack
- Frontend: React, Vite, CSS
- Backend: Python, FastAPI, Uvicorn
- ML: scikit-learn RandomForestClassifier
- Database: SQLite

## Run locally

### Backend
```bash
cd backend
python -m venv venv
# Windows: venv\\Scripts\\activate
# Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
python train_model.py
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal, normally `http://localhost:5173`.

The frontend expects the API at `http://localhost:8000`. Create `frontend/.env` if needed:
```env
VITE_API_URL=http://localhost:8000
```

## Deploy
A `render.yaml` blueprint is included. The easiest setup is to deploy the backend and frontend as two Render services. See `DEPLOYMENT.md` for steps.

## Project identity
- Project: FoodWise AI
- Developer: Shahid Anwar
- Internship use: AI/ML project portfolio
- SDG: Goal 12 – Responsible Consumption and Production
- Date: 05/10/2026
