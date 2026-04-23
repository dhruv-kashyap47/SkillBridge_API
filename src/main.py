import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from .database import engine, Base
from .routes import auth, batches, sessions, attendance, monitoring


app = FastAPI(title="SkillBridge – Attendance Management System")


origins = os.getenv("ALLOWED_ORIGINS")

if origins:
    origins = [o.strip() for o in origins.split(",")]
else:
    origins = ["http://localhost:3000", "http://127.0.0.1:3000"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(batches.router)
app.include_router(sessions.router)
app.include_router(attendance.router)
app.include_router(monitoring.router)


frontend_path = Path(__file__).parent.parent / "frontend"

if frontend_path.exists():
    app.mount("/app", StaticFiles(directory=str(frontend_path), html=True), name="frontend")


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return RedirectResponse(url="/app/")


@app.get("/health")
def health():
    return {"status": "ok"}
