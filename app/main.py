"""FastAPI application entry point — routes, startup, and middleware."""

import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, Request, HTTPException, Query
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session
from sqlalchemy import text, or_

from app.database import Base, engine, get_db
from app.limiter import limiter

from app.models import Track, ApiKey, RecommendationLog
from app.recommender import track_to_vector, get_candidates
from app.ranker import ranker_a
from app.schemas import TrackRecommendation, TrackRecommendationRequest, MoodRecommendationRequest, RecommendationResponse, TrackSearchResult, TrackSearchResponse
from app.auth import require_api_key
from app.mood import translate_mood
from app.explainer import explain_recommendations



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


def _log_request(
    db: Session,
    request_type: str,
    input_data: str,
    experiment_group: str,
    strategy_used: str,
    spotify_ids: list[str],
) -> int:
    """Insert a recommendation_log row and return its generated id."""
    log = RecommendationLog(
        request_type=request_type,
        input_data=input_data,
        experiment_group=experiment_group,
        strategy_used=strategy_used,
        recommendations=json.dumps(spotify_ids),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log.id


@app.get("/health")
@limiter.limit("10/minute")
def health(request: Request, db: Session = Depends(get_db)) -> dict:
    """Return API status and database connectivity. No auth required."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception:
        return {"status": "degraded", "db": "unreachable"}


@app.get("/search/tracks")
@limiter.limit("30/minute")
def search_tracks(
    request: Request,
    q: str = Query(min_length=1, max_length=100),
    db: Session = Depends(get_db),
) -> TrackSearchResponse:
    """Autocomplete catalog search — return up to 10 tracks whose name or artist matches q."""
    pattern = f"%{q.strip()}%"
    matches = (
        db.query(Track)
        .filter(or_(Track.name.ilike(pattern), Track.artist.ilike(pattern)))
        .order_by(Track.popularity.desc().nullslast())
        .limit(10)
        .all()
    )
    return TrackSearchResponse(
        results=[TrackSearchResult.model_validate(track) for track in matches]
    )


@app.post("/recommend/track")
@limiter.limit("10/minute")
def recommend_track(
    body: TrackRecommendationRequest,
    request: Request,
    db: Session = Depends(get_db),
    api_key: ApiKey = Depends(require_api_key)
) -> RecommendationResponse:
    track = db.query(Track).filter(Track.spotify_id == body.spotify_id).first()

    if not track:
        raise HTTPException(status_code=404, detail= {"error": "Track not found in catalog", "code": 404})
    
    query_vector = track_to_vector(track)
    candidates = get_candidates(query_vector)
    ranked_candidates = ranker_a(query_vector, candidates, db)
    
    recommendations = [
        TrackRecommendation(
            spotify_id=song[0].spotify_id,
            name=song[0].name,
            artist=song[0].artist,
            album=song[0].album,
            explanation=None,
            similarity_score=float(song[1]),
        )
        for song in ranked_candidates
    ]
    log_id = _log_request(
        db=db,
        request_type="track",
        input_data=body.spotify_id,
        experiment_group="A",
        strategy_used="cosine_similarity",
        spotify_ids=[r.spotify_id for r in recommendations],
    )
    return RecommendationResponse(
        recommendations=recommendations,
        experiment_group="A",
        strategy="cosine_similarity",
        log_id=log_id,
    )

@app.post("/recommend/mood")
@limiter.limit("10/minute")
def recommend_mood(
    body: MoodRecommendationRequest,
    request: Request,
    db: Session = Depends(get_db),
    api_key: ApiKey = Depends(require_api_key)
) -> RecommendationResponse:
    query_vector = list(translate_mood(body.mood_string).values()) + [75] # popularity score
    candidates = get_candidates(query_vector)
    recommendations = ranker_a(query_vector, candidates, db)
    tracks = [x[0] for x in recommendations]
    scores = [x[1] for x in recommendations]
    explanations = explain_recommendations(body.mood_string, tracks)
    recs = [
        TrackRecommendation(
            spotify_id=track.spotify_id,
            name=track.name,
            artist=track.artist,
            album=track.album,
            explanation=explanations[i],
            similarity_score=float(scores[i]),
        )
        for i, track in enumerate(tracks)
    ]
    log_id = _log_request(
        db=db,
        request_type="mood",
        input_data=body.mood_string,
        experiment_group="A",
        strategy_used="cosine_similarity",
        spotify_ids=[r.spotify_id for r in recs],
    )
    return RecommendationResponse(
        recommendations=recs,
        experiment_group="A",
        strategy="cosine_similarity",
        log_id=log_id,
    )


