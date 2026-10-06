"""FastAPI application entry point."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.database import Base,engine
from app.routers import me,path,lessons,hearts,leaderboard,dev

@asynccontextmanager
async def lifespan(app:FastAPI):
    Base.metadata.create_all(bind=engine)
    if os.getenv("AUTO_SEED","false").lower()=="true":
        from app.seed import seed
        seed()
    yield

app=FastAPI(title="Duolingo Clone API",version="1.0.0",lifespan=lifespan)
static_dir=Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")
origins=[x.strip() for x in os.getenv("CORS_ORIGINS","http://localhost:3000,http://127.0.0.1:3000").split(",") if x.strip()]
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_methods=["*"],allow_headers=["*"])

app.include_router(me.router,prefix="/api")
app.include_router(path.router,prefix="/api")
app.include_router(lessons.router,prefix="/api")
app.include_router(hearts.router,prefix="/api")
app.include_router(leaderboard.router,prefix="/api")
app.include_router(dev.router,prefix="/api")

@app.get("/api/health",summary="Health check")
def health(): return {"status":"ok"}
