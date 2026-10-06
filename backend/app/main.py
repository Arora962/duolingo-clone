from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import User
from app.services.stats import current_hearts, current_streak, total_xp

DEFAULT_USERNAME = "learner"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create the schema at startup; seed data is intentionally run separately."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Duolingo Clone API", lifespan=lifespan)

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
    """Return the seeded learner profile with all gamification values derived."""
    user = db.scalar(select(User).where(User.username == DEFAULT_USERNAME))
    if user is None:
        raise HTTPException(status_code=404, detail="Default learner not found")
    xp = total_xp(db, user.id)
    streak = current_streak(db, user.id)
    hearts = current_hearts(db, user.id)
    # The new contract uses total_xp/current_streak; xp/streak aliases keep the existing frontend working.
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "gems": user.gems,
        "total_xp": xp,
        "current_streak": streak,
        "hearts": hearts,
        "xp": xp,
        "streak": streak,
    }
