from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from app.db.database import get_db
from app.auth import get_current_user
from app.ai.chatbot import chat
import uuid

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    session_id: str = ""

@router.post("/message")
async def send_message(request: ChatRequest, user: dict = Depends(get_current_user)):
    session_id = request.session_id or str(uuid.uuid4())
    messages = [{"role": m.role, "content": m.content} for m in request.messages]
    
    response_text = chat(messages)
    
    conn = get_db()
    cur = conn.cursor()
    if messages:
        cur.execute("INSERT INTO chat_history (user_id, session_id, role, content) VALUES (?, ?, ?, ?)",
                    (int(user["sub"]), session_id, "user", messages[-1]["content"]))
    cur.execute("INSERT INTO chat_history (user_id, session_id, role, content) VALUES (?, ?, ?, ?)",
                (int(user["sub"]), session_id, "assistant", response_text))
    conn.commit()
    conn.close()
    
    return {"response": response_text, "session_id": session_id}

@router.get("/history")
async def get_history(session_id: str = "", user: dict = Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor()
    if session_id:
        cur.execute("SELECT * FROM chat_history WHERE user_id = ? AND session_id = ? ORDER BY created_at",
                    (int(user["sub"]), session_id))
    else:
        cur.execute("SELECT * FROM chat_history WHERE user_id = ? ORDER BY created_at DESC LIMIT 50",
                    (int(user["sub"]),))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows