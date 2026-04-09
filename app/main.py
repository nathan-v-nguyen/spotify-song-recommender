"""FastAPI application entry point — routes, startup, and middleware."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import Base, engine, get_db
from app.limiter import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create all database tables on startup."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Spotify RecSys", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler so raw Python exceptions never reach the user as unformatted 500s."""
    return JSONResponse(status_code=500, content={"error": "An unexpected error occurred", "code": 500})


@app.get("/health")
@limiter.limit("10/minute")
def health(request: Request, db: Session = Depends(get_db)) -> dict:
    """Return API status and database connectivity. No auth required."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception:
        return {"status": "degraded", "db": "unreachable"}

