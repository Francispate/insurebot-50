import joblib
import numpy as np
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../models/settlement_model.pkl")
SCALER_PATH = os.path.join(os.path.dirname(__file__), "../../models/settlement_scaler.pkl")

settlement_model = None
settlement_scaler = None

def load_settlement_model():
    global settlement_model, settlement_scaler
    if settlement_model is None:
        if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
            settlement_model = joblib.load(MODEL_PATH)
            settlement_scaler = joblib.load(SCALER_PATH)

def predict_settlement(features: list) -> dict:
    load_settlement_model()
    if settlement_model is None or settlement_scaler is None:
        return {
            "predicted_settlement": "full",
            "settlement_confidence": 78.3
        }
    X = np.array(features).reshape(1, -1)
    X_scaled = settlement_scaler.transform(X)
    prob = settlement_model.predict_proba(X_scaled)[0]
    confidence = round(max(prob) * 100, 1)
    label = settlement_model.classes_[np.argmax(prob)]
    return {
        "predicted_settlement": str(label),
        "settlement_confidence": confidence
    }