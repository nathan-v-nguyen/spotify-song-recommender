"""API key validation — injects authenticated API key as a FastAPI dependency."""

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ApiKey


def require_api_key(
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: Session = Depends(get_db),
) -> ApiKey:
    """Validate X-API-Key header against the api_keys table. Raises 401 if invalid."""
    record = db.query(ApiKey).filter(ApiKey.key == x_api_key).first()
    if not record:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return record
