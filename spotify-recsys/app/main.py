"""FastAPI application entry point — routes, startup, and middleware."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import Base, engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create all database tables on startup."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Spotify RecSys", lifespan=lifespan)


@app.get("/health")
def health(db: Session = Depends(get_db)) -> dict:
    """Return API status and database connectivity. No auth required."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception:
        return {"status": "degraded", "db": "unreachable"}

