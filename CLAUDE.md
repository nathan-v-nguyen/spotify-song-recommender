# CLAUDE.md

## Project Goals

A production-grade music recommendation API that accepts a seed track or natural language mood description and returns 10 personalized song recommendations with explanations. Includes an A/B testing framework comparing two ranking strategies.

**Primary audience:** FAANG recruiters and ML engineering hiring managers  
**Definition of done:** Live deployed URL on Render  
**Current milestone:** MVP — seed track recommendation and mood-based recommendation working end to end

---

## Architecture Overview

FastAPI backend + PostgreSQL database running in Docker. Annoy index for fast similarity search. Claude API for mood translation and explanation generation. Streamlit frontend for demo.

```
spotify-song-recommender/
├── app/
│   ├── main.py              # FastAPI app, all routes
│   ├── models.py            # SQLAlchemy table definitions
│   ├── schemas.py           # Pydantic request/response models
│   ├── database.py          # Engine, SessionLocal, Base, get_db
│   ├── auth.py              # API key validation
│   ├── limiter.py           # Rate limiting
│   ├── recommender.py       # Retrieval logic (Annoy index)
│   ├── ranker.py            # Strategy A and B ranking
│   ├── experiment.py        # A/B assignment and metrics
│   ├── mood.py              # Claude mood → audio features
│   └── explainer.py        # Claude explanation generation
├── scripts/
│   ├── seed_catalog.py      # Populate tracks table from Spotify API
│   └── build_index.py       # Build and save Annoy index
├── models/                  # Saved Annoy index and ranker B model
├── frontend/
│   └── app.py               # Streamlit demo
├── tests/
├── .github/workflows/ci.yml
├── .env                     # Never commit
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| API | FastAPI + Uvicorn |
| Validation | Pydantic v2 |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Database | PostgreSQL 15 (Docker) |
| Similarity search | Annoy |
| Ranking | numpy (Strategy A), LightGBM (Strategy B) |
| LLM | Anthropic SDK — claude-sonnet-4-20250514 |
| Spotify client | spotipy |
| Rate limiting | slowapi |
| Testing | pytest + httpx |
| CI | GitHub Actions |
| Frontend | Streamlit |
| Deployment | Render |

---

## Design & Code Style

**Code quality is the top priority.**

- Every function has type hints on all parameters and return values
- Every module has a one-line docstring describing its purpose
- No function longer than 40 lines — split if needed
- No raw SQL — SQLAlchemy ORM only
- No hardcoded secrets — all from environment variables via `python-dotenv`
- All API errors return consistent JSON: `{"error": "message", "code": 422}`
- No commented-out code committed to main

**API patterns:**
- Auth header: `X-API-Key`
- Rate limit: 10 requests per minute per IP
- Errors: 401 missing key, 404 not found, 422 validation, 429 rate limit, 503 DB down

---

## Constraints & Policies

**Security — MUST follow:**
- NEVER expose API keys to the client — server-side only
- ALWAYS use environment variables for secrets
- NEVER commit `.env` to git
- Validate and sanitize all user input before passing to Claude

**Dependencies:**
- Do not add libraries not already in `requirements.txt` without asking
- Use SQLAlchemy ORM — never raw SQL strings
- Mock all Anthropic and Spotify API calls in tests — no real API calls in CI

---

## Repository Etiquette

**Branching:**
- Always create a feature branch before starting major changes
- Never commit directly to `main`
- Branch naming: `feature/description` or `fix/description`

**Git workflow:**
1. `git checkout -b feature/your-feature-name`
2. Develop and commit on the feature branch
3. Test locally before pushing — `docker compose up` must work cleanly
4. `git push -u origin feature/your-feature-name`
5. Create a PR to merge into `main`

**Commits:**
- Write clear commit messages describing the change
- Keep commits focused on a single change
- Never force push to `main`

---

## Local Dev Commands

```bash
# Start database only
docker compose up db

# Start full stack
docker compose up

# Run alembic outside Docker (use localhost not db)
DATABASE_URL=postgresql://postgres:password@localhost:5432/recsys alembic upgrade head

# Run tests
pytest tests/ -v

# Activate venv
source venv/bin/activate
```

**Important:** Homebrew PostgreSQL conflicts with Docker on port 5432. Stop it before working:
```bash
brew services stop postgresql@15
```

---

## Current Status

**Completed:**
- Project folder structure
- Docker + PostgreSQL running
- `app/database.py` — complete
- `app/models.py` — complete (Track, RecommendationLog, Feedback, ApiKey)
- Alembic initialized — first migration applied, all 4 tables verified in PostgreSQL
- `docker-compose.yml`, `Dockerfile`, `requirements.txt` — complete
- `.env` configured with all secrets
- GitHub repo created
- `app/main.py` — complete: FastAPI app with lifespan startup (`Base.metadata.create_all`), `GET /health` with DB connectivity check, rate limiter wired in, catch-all 500 handler
- `app/limiter.py` — complete: slowapi Limiter keyed by client IP, 10 req/min per route
- `app/auth.py` — complete: `require_api_key` dependency validates `X-API-Key` header against `api_keys` table, returns `ApiKey` record for A/B group access

- `scripts/seed_catalog.py` — complete: loads tracks from Kaggle CSV dataset (Spotify audio features API deprecated in 2024), deduplicates on `spotify_id`, writes to `tracks` table. Includes `popularity` as an additional feature.
- `scripts/build_index.py` — complete: loads 89,740 tracks from DB, normalizes 9 audio features with `MinMaxScaler` (saved to `models/scaler.pkl`), builds Annoy index with 50 trees using `angular` distance, saves index to `models/annoy_index.ann` and position → spotify_id list to `models/track_id_map.json`. Verified with sanity check — nearest neighbor queries return valid spotify_ids with expected low distances.

- `app/recommender.py` — complete: loads Annoy index, scaler, and id map at module level (once at startup). Exposes `track_to_vector(track) -> list[float]` to extract features from a Track ORM object, and `get_candidates(query_vector, n=500) -> list[str]` to normalize a raw feature vector and return nearest spotify_ids. Verified with manual smoke test — returns valid candidates with seed track as its own nearest neighbor.

**In progress:**
- Nothing

**Next steps (MVP pipeline, in order):**
1. Write `app/ranker.py` — Strategy A: fetch 500 candidate tracks from DB, compute cosine similarity against query vector using numpy, sort descending, return top 10 `Track` objects
2. Write `app/schemas.py` — Pydantic request/response models for `POST /recommend/track`
3. Wire `POST /recommend/track` in `app/main.py` — look up seed track, call `track_to_vector` → `get_candidates` → `rank_strategy_a`, log to `recommendation_logs`, return top 10

---

## Documentation

- [Overview](docs/overview.md) — full project context, career goals, background
- [Project Spec](docs/PROJECT_SPEC.md) — detailed requirements, API contract, architecture decisions
- Update files in docs folder after major milestones and major additions to the project
