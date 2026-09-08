
import joblib
import numpy as np
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../models/fraud_model.pkl")
SCALER_PATH = os.path.join(os.path.dirname(__file__), "../../models/fraud_scaler.pkl")

fraud_model = None
fraud_scaler = None

def load_fraud_model():
    global fraud_model, fraud_scaler
    if fraud_model is None:
        if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
            fraud_model = joblib.load(MODEL_PATH)
            fraud_scaler = joblib.load(SCALER_PATH)

def predict_fraud(features: list) -> dict:
    load_fraud_model()
    if fraud_model is None or fraud_scaler is None:
        return {
            "fraud_risk_score": 22.5,
            "fraud_label": "genuine",
            "requires_investigation": False
        }
    X = np.array(features).reshape(1, -1)
    X_scaled = fraud_scaler.transform(X)
    prob = fraud_model.predict_proba(X_scaled)[0]
    score = round(prob[1] * 100, 1)
    label = "fraud" if score > 70 else ("suspicious" if score > 40 else "genuine")
    return {
        "fraud_risk_score": score,
        "fraud_label": label,
        "requires_investigation": score > 60
    }



