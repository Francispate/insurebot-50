from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db.database import init_db
from app.api import auth, claims, policies, chatbot, admin

app = FastAPI(title="Insurance Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

app.include_router(auth.router,     prefix="/auth",    tags=["Auth"])
app.include_router(claims.router,   prefix="/claims",  tags=["Claims"])
app.include_router(policies.router, prefix="/policies",tags=["Policies"])
app.include_router(chatbot.router,  prefix="/chat",    tags=["Chatbot"])
app.include_router(admin.router,    prefix="/admin",   tags=["Admin"])

@app.get("/")
def root():
    return {"status": "Insurance Platform API Running"}