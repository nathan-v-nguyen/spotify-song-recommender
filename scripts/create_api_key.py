"""Script to create a new API key and insert it into the database."""

import hashlib
import secrets
import sys
from app.database import SessionLocal
from app.models import ApiKey


def assign_group(key: str) -> str:
    """Deterministically assign A/B group based on key hash."""
    hash_int = int(hashlib.md5(key.encode()).hexdigest(), 16)
    return "A" if hash_int % 2 == 0 else "B"


def create_api_key() -> None:
    """Generate a new API key and save it to the database."""
    key = secrets.token_hex(32)
    group = assign_group(key)

    db = SessionLocal()
    try:
        api_key = ApiKey(key=key, experiment_group=group)
        db.add(api_key)
        db.commit()
        print(f"API Key: {key}")
        print(f"Experiment group: {group}")
        print("Save this key — it won't be shown again.")
    except Exception as e:
      print(f"Failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_api_key()