from fastapi import APIRouter, UploadFile, File, Form, Depends
from pydantic import BaseModel
from app.db.database import get_db
from app.auth import get_current_user
from app.ai.policy_analyzer import extract_pdf_text, analyze_policy_text
from app.ai.web_search import search_insurance_info
from app.ai.advisor import get_preclaim_advice
import os

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class PolicyAnalyzeRequest(BaseModel):
    policy_text: str = ""

class PreClaimRequest(BaseModel):
    claim_type: str
    description: str
    policy_details: str = ""

@router.post("/analyze")
async def analyze_policy(file: UploadFile = File(None), policy_text: str = Form(""), user: dict = Depends(get_current_user)):
    text = policy_text
    if file:
        contents = await file.read()
        text = extract_pdf_text(contents)
        file_path = os.path.join(UPLOAD_DIR, f"policy_{user['sub']}_{file.filename}")
        with open(file_path, "wb") as f:
            f.write(contents)
    
    result = analyze_policy_text(text)
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO user_policies (user_id, policy_name, pdf_path, policy_summary, what_covered, what_not_covered, hidden_benefits, dangerous_clauses, overall_rating)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        int(user["sub"]), file.filename if file else "Text Policy", file_path if file else "",
        result.get("policy_summary", ""), json.dumps(result.get("what_is_covered", [])),
        json.dumps(result.get("what_is_NOT_covered", [])), json.dumps(result.get("hidden_benefits", [])),
        json.dumps(result.get("dangerous_clauses", [])), result.get("overall_rating", 0)
    ))
    conn.commit()
    conn.close()
    return result

@router.post("/advice")
async def get_advice(req: PreClaimRequest, user: dict = Depends(get_current_user)):
    advice = get_preclaim_advice(req.claim_type, req.description, req.policy_details)
    search_results = search_insurance_info(f"{req.claim_type} claim requirements India")
    return {"advice": advice, "search_results": search_results}

@router.get("/")
async def list_policies(user: dict = Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_policies WHERE user_id = ? ORDER BY created_at DESC", (int(user["sub"]),))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows