from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine, get_db
from app.models import User

DEFAULT_USERNAME = "learner"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when the server starts: create tables + add a default learner
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        existing = db.scalar(select(User).where(User.username == DEFAULT_USERNAME))
        if existing is None:
            db.add(User(username=DEFAULT_USERNAME, xp=120, streak=3, hearts=5))
            db.commit()
    yield


app = FastAPI(title="Duolingo Clone API", lifespan=lifespan)

# Lets the website (port 3000) talk to the backend (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/me")
def me(db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == DEFAULT_USERNAME))
    if user is None:
        raise HTTPException(status_code=404, detail="Default learner not found")
    return {
        "id": user.id,
        "username": user.username,
        "xp": user.xp,
        "streak": user.streak,
        "hearts": user.hearts,
    }