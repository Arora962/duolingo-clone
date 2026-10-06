"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import AUTO_SEED, CORS_ORIGINS, ENABLE_DEV_ENDPOINTS
from app.database import Base, engine
from app.routers import hearts, leaderboard, lessons, me, path
from app.routers import dev
from app.seed import seed
from app.schemas.health import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create the frozen schema and optionally run the seed."""
    Base.metadata.create_all(bind=engine)
    if AUTO_SEED:
        seed()
    yield


app = FastAPI(
    title="Duolingo Clone API",
    version="1.0.0",
    lifespan=lifespan,
)

static_dir = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

origins = [item.strip() for item in CORS_ORIGINS.split(",") if item.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(me.router, prefix="/api")
app.include_router(path.router, prefix="/api")
app.include_router(lessons.router, prefix="/api")
app.include_router(hearts.router, prefix="/api")
app.include_router(leaderboard.router, prefix="/api")

if ENABLE_DEV_ENDPOINTS:
    app.include_router(dev.router, prefix="/api")


@app.get(
    "/api/health",
    response_model=HealthResponse,
    response_model_exclude_none=False,
    summary="Health check",
)
def health() -> dict[str, str]:
    """Return a simple health status."""
    return {"status": "ok"}
