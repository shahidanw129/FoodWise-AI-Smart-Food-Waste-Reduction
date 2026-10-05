# Deployment Guide – Render

## 1. Push to GitHub
Create a repository and push the complete `FoodWise_AI_Project` folder.

## 2. Backend Web Service
- Root directory: `backend`
- Runtime: Python
- Build command: `pip install -r requirements.txt && python train_model.py`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

After deployment, copy the backend URL, for example:
`https://foodwise-api.onrender.com`

## 3. Frontend Static Site
- Root directory: `frontend`
- Build command: `npm install && npm run build`
- Publish directory: `dist`
- Environment variable:
  `VITE_API_URL=https://YOUR-BACKEND-URL.onrender.com`

## 4. CORS
The backend currently allows browser requests for development and deployment. For production, you can restrict `allow_origins` in `backend/main.py` to your frontend domain.
