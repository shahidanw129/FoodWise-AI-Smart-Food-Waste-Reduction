"""Train a small, reproducible ML model for FoodWise expiry-risk prediction."""
from pathlib import Path
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier

BASE = Path(__file__).resolve().parent
MODEL_PATH = BASE / "food_risk_model.pkl"

# Features: days_until_expiry, quantity_kg, storage_temp_c, days_since_purchase
rng = np.random.default_rng(42)
n = 1800
days_expiry = rng.integers(0, 15, n)
quantity = np.round(rng.uniform(0.1, 5.0, n), 2)
storage_temp = np.round(rng.uniform(2, 12, n), 1)
days_purchase = rng.integers(0, 15, n)

# Synthetic labels designed around realistic food-waste risk factors.
risk_signal = (
    (10 - days_expiry) * 0.55
    + quantity * 0.25
    + np.maximum(storage_temp - 5, 0) * 0.45
    + days_purchase * 0.20
    + rng.normal(0, 1.2, n)
)
y = (risk_signal > 5.4).astype(int)
X = np.column_stack([days_expiry, quantity, storage_temp, days_purchase])

model = RandomForestClassifier(n_estimators=160, max_depth=8, random_state=42, class_weight="balanced")
model.fit(X, y)
with MODEL_PATH.open("wb") as f:
    pickle.dump(model, f)
print(f"Saved model to {MODEL_PATH}")
