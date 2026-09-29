import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
print("HUGGINGFACE_TOKEN loaded:", bool(os.getenv("HUGGINGFACE_TOKEN")))
print("SECRET_KEY loaded:", bool(os.getenv("SECRET_KEY")))
HF_MODEL = os.getenv("HF_MODEL", "Qwen/Qwen2.5-7B-Instruct")
SECRET_KEY = os.getenv("SECRET_KEY")

from app.database import engine, Base
from app import models
from app.config import CORS_ORIGINS
from app.routers import auth, career, matching, resumes

# إنشاء الجداول في قاعدة البيانات
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Career Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(CORS_ORIGINS),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تسجيل الـ Routers
app.include_router(auth.router)
app.include_router(career.router)
app.include_router(resumes.router)
app.include_router(matching.router)

@app.get("/")
def home():
    return {
        "message": "AI Career Platform is running successfully!"
    }