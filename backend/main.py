from pathlib import Path
from datetime import date, timedelta
import pickle
import sqlite3
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / "foodwise.db"
MODEL_PATH = BASE / "food_risk_model.pkl"

app = FastAPI(title="FoodWise AI API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

FOOD_TIPS = {
    "Milk": "Keep refrigerated and use soon after opening.",
    "Bread": "Freeze extra slices if you will not use them soon.",
    "Tomato": "Store ripe tomatoes at room temperature away from sunlight.",
    "Banana": "Separate very ripe bananas and use them in smoothies or baking.",
    "Spinach": "Keep dry with a paper towel and use early in the week.",
    "Chicken": "Keep chilled and cook before the use-by date.",
    "Rice": "Store cooked rice covered in the refrigerator and use promptly.",
    "Apple": "Store in a cool place; use softer apples for smoothies or cooking.",
}

RECIPES = [
    {"name": "Vegetable Fried Rice", "ingredients": ["Rice", "Carrot", "Peas", "Onion"], "time": "20 min"},
    {"name": "Spinach Omelette", "ingredients": ["Spinach", "Egg", "Onion"], "time": "12 min"},
    {"name": "Banana Smoothie", "ingredients": ["Banana", "Milk"], "time": "5 min"},
    {"name": "Tomato Pasta", "ingredients": ["Tomato", "Pasta", "Onion"], "time": "25 min"},
    {"name": "Chicken Rice Bowl", "ingredients": ["Chicken", "Rice", "Carrot"], "time": "30 min"},
]

class FoodCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    category: str = "Other"
    quantity_kg: float = Field(gt=0, le=100)
    expiry_date: date
    storage_temp_c: float = Field(default=5, ge=-10, le=40)

class PredictionRequest(BaseModel):
    days_until_expiry: int = Field(ge=0, le=60)
    quantity_kg: float = Field(gt=0, le=100)
    storage_temp_c: float = Field(ge=-10, le=40)
    days_since_purchase: int = Field(ge=0, le=60)


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS foods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        quantity_kg REAL NOT NULL,
        expiry_date TEXT NOT NULL,
        storage_temp_c REAL NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    return conn


def get_model():
    if not MODEL_PATH.exists():
        from train_model import model as _  # noqa: F401
    with MODEL_PATH.open("rb") as f:
        return pickle.load(f)

model = get_model()

@app.get("/api/health")
def health():
    return {"status": "ok", "project": "FoodWise AI"}

@app.get("/api/foods")
def foods():
    conn = db()
    rows = conn.execute("SELECT * FROM foods ORDER BY expiry_date ASC, id DESC").fetchall()
    conn.close()
    today = date.today()
    result = []
    for r in rows:
        item = dict(r)
        days = (date.fromisoformat(item["expiry_date"]) - today).days
        pred = predict_values(days, item["quantity_kg"], item["storage_temp_c"], max(0, (today - date.fromisoformat(item["created_at"][:10])).days))
        item.update(pred)
        result.append(item)
    return result

@app.post("/api/foods")
def add_food(food: FoodCreate):
    if food.expiry_date < date.today():
        raise HTTPException(400, "Expiry date cannot be in the past.")
    conn = db()
    cur = conn.execute(
        "INSERT INTO foods(name, category, quantity_kg, expiry_date, storage_temp_c) VALUES (?, ?, ?, ?, ?)",
        (food.name, food.category, food.quantity_kg, food.expiry_date.isoformat(), food.storage_temp_c),
    )
    conn.commit()
    conn.close()
    return {"id": cur.lastrowid, "message": "Food item added successfully."}

@app.delete("/api/foods/{food_id}")
def delete_food(food_id: int):
    conn = db()
    cur = conn.execute("DELETE FROM foods WHERE id=?", (food_id,))
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        raise HTTPException(404, "Food item not found")
    return {"message": "Food item removed."}

@app.post("/api/predict")
def predict(req: PredictionRequest):
    return predict_values(req.days_until_expiry, req.quantity_kg, req.storage_temp_c, req.days_since_purchase)


def predict_values(days, quantity, temp, since_purchase):
    proba = float(model.predict_proba([[days, quantity, temp, since_purchase]])[0][1])
    score = round(proba * 100, 1)
    if score >= 70:
        level = "High"
        action = "Use this item first or freeze/cook it today."
    elif score >= 40:
        level = "Medium"
        action = "Plan a meal with this item within the next few days."
    else:
        level = "Low"
        action = "Keep monitoring the item and store it correctly."
    return {"risk_score": score, "risk_level": level, "recommended_action": action}

@app.get("/api/recipes")
def recipes(ingredients: Optional[str] = None):
    if not ingredients:
        return RECIPES
    available = {x.strip().lower() for x in ingredients.split(",") if x.strip()}
    scored = []
    for recipe in RECIPES:
        matches = sum(i.lower() in available for i in recipe["ingredients"])
        scored.append((matches, recipe))
    return [r for _, r in sorted(scored, key=lambda x: x[0], reverse=True)]

@app.get("/api/stats")
def stats():
    conn = db()
    rows = conn.execute("SELECT quantity_kg, expiry_date FROM foods").fetchall()
    conn.close()
    today = date.today()
    total = sum(float(r["quantity_kg"]) for r in rows)
    urgent = sum(1 for r in rows if (date.fromisoformat(r["expiry_date"]) - today).days <= 2)
    safe = max(0, len(rows) - urgent)
    return {"items": len(rows), "tracked_kg": round(total, 2), "urgent_items": urgent, "safe_items": safe, "estimated_saved_kg": round(total * 0.18, 2)}
