"""Manual smoke test for app/recommender.py — run once to verify, then delete."""

from app.database import SessionLocal
from app.models import Track
from app.recommender import track_to_vector, get_candidates

db = SessionLocal()
try:
    track = db.query(Track).first()
    print(f"Seed: {track.spotify_id} — {track.name} by {track.artist}")

    candidates = get_candidates(track_to_vector(track), n=10)
    print(f"Candidates ({len(candidates)}):")
    for sid in candidates:
        print(f"  {sid}")
finally:
    db.close()
