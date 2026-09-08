from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.db.database import get_db
from app.auth import get_current_user
from app.ai.vision import analyze_damage_image
from app.ai.fraud import predict_fraud
from app.ai.settlement import predict_settlement
import json
import os
import shutil

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ClaimCreate(BaseModel):
    claim_type: str
    description: str
    damage_severity: str = ""
    estimated_amount: str = ""
    affected_parts: str = ""
    documentation_needed: str = ""
    rejection_risks: str = ""
    fraud_risk_score: float = 0
    fraud_label: str = "unknown"
    predicted_settlement: str = ""
    settlement_confidence: float = 0
    requires_investigation: int = 0

@router.post("/analyze")
async def analyze_claim(image: UploadFile = File(...)):
    contents = await image.read()
    vision_result = analyze_damage_image(contents)
    
    dummy_features = [2, 1, 1, 0, 1, 5000, 3000, 15000, 2020]
    fraud_result = predict_fraud(dummy_features)
    settlement_result = predict_settlement(dummy_features)
    
    return {
        **vision_result,
        **fraud_result,
        **settlement_result,
        "status": "analyzed"
    }

@router.post("/")
async def create_claim(claim: ClaimCreate, user: dict = Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO claims (user_id, claim_type, description, damage_severity, estimated_amount,
        affected_parts, documentation_needed, rejection_risks, fraud_risk_score, fraud_label,
        predicted_settlement, settlement_confidence, requires_investigation, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        int(user["sub"]), claim.claim_type, claim.description, claim.damage_severity,
        claim.estimated_amount, claim.affected_parts, claim.documentation_needed,
        claim.rejection_risks, claim.fraud_risk_score, claim.fraud_label,
        claim.predicted_settlement, claim.settlement_confidence, claim.requires_investigation, "pending"
    ))
    conn.commit()
    claim_id = cur.lastrowid
    conn.close()
    return {"id": claim_id, "status": "created"}

@router.get("/")
async def list_claims(user: dict = Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM claims WHERE user_id = ? ORDER BY created_at DESC", (int(user["sub"]),))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

@router.get("/all")
async def list_all_claims(user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT c.*, u.name as user_name, u.email as user_email FROM claims c JOIN users u ON c.user_id = u.id ORDER BY c.created_at DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

@router.put("/{claim_id}/status")
async def update_claim_status(claim_id: int, status: str = Form(...), user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE claims SET status = ? WHERE id = ?", (status, claim_id))
    conn.commit()
    conn.close()
    return {"status": "updated"}