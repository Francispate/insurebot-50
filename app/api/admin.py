from fastapi import APIRouter, Depends
from app.db.database import get_db
from app.auth import get_current_user

router = APIRouter()

@router.get("/stats")
async def get_stats(user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as total FROM users")
    total_users = cur.fetchone()["total"]
    
    cur.execute("SELECT COUNT(*) as total FROM claims")
    total_claims = cur.fetchone()["total"]
    
    cur.execute("SELECT COUNT(*) as total FROM claims WHERE status = 'pending'")
    pending = cur.fetchone()["total"]
    
    cur.execute("SELECT COUNT(*) as total FROM claims WHERE requires_investigation = 1")
    high_risk = cur.fetchone()["total"]
    
    cur.execute("SELECT claim_type, COUNT(*) as count FROM claims GROUP BY claim_type")
    claims_by_type = [dict(r) for r in cur.fetchall()]
    
    cur.execute("SELECT fraud_label, COUNT(*) as count FROM claims GROUP BY fraud_label")
    fraud_dist = [dict(r) for r in cur.fetchall()]
    
    conn.close()
    return {
        "total_users": total_users,
        "total_claims": total_claims,
        "pending": pending,
        "high_risk": high_risk,
        "claims_by_type": claims_by_type,
        "fraud_distribution": fraud_dist
    }

@router.get("/users")
async def list_users(user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, role, country, created_at FROM users ORDER BY created_at DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

@router.put("/users/{user_id}/role")
async def update_user_role(user_id: int, role: str, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
    conn.commit()
    conn.close()
    return {"status": "updated"}