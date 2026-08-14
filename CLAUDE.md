# CLAUDE.md

## Project Goals

Moodify is a full-stack music recommendation product. The ML/recommendation core is done: a FastAPI backend that accepts a seed track or natural language mood description and returns 10 personalized song recommendations with explanations, plus an A/B testing framework comparing two ranking strategies (MD5 bucketing, request logging, feedback collection, Streamlit metrics dashboard).

**That ML core is no longer the focus.** Nathan is a Data Science major recruiting for Software Engineering internships, not ML/DS roles. The project is now being turned into a complete SWE product by closing specific skill gaps, in priority order: (1) a real React frontend, (2) user accounts and auth (JWT/sessions) with saved history, (3) testing (pytest) and CI/CD (GitHub Actions), (4) a system design write-up, (5) stretch — a real-time/concurrent feature. Full detail: `docs/project_spec.md` Part 3 (Sections 24–28), and `docs/overview.md`.

**Primary audience:** SWE internship recruiters and hiring managers at startups — Meta/TikTok-style consumer tech as stretch targets, not ML engineering hiring managers  
**Definition of done:** A complete full-stack product — React frontend, auth, tested and CI/CD'd backend — live on Render, plus a defensible system design write-up  
**Current milestone:** React frontend (Priority 1) — see Current Status and Next Steps below

**How to help Nathan on this project:** prioritize teaching the underlying SWE fundamentals while building, not just producing working code. Explain the *why* behind frontend/auth/testing patterns as you go — Nathan dislikes "vibe coding" parts he doesn't understand and needs to be able to defend any architectural decision in a technical interview.

---

## Architecture Overview

FastAPI backend + PostgreSQL database running in Docker. Annoy index for fast similarity search. Claude API for mood translation and explanation generation. A React frontend (Priority 1, not yet started) will become the product-facing UI going forward; the existing Streamlit app is currently the only UI and is being repositioned as an internal metrics/demo dashboard.

```
spotify-song-recommender/
├── app/
│   ├── main.py              # FastAPI app, all routes (A/B group currently hardcoded to "A")
│   ├── models.py            # SQLAlchemy table definitions
│   ├── schemas.py           # Pydantic request/response models
│   ├── database.py          # Engine, SessionLocal, Base, get_db
│   ├── auth.py              # API key validation
│   ├── limiter.py           # Rate limiting
│   ├── recommender.py       # Retrieval logic (Annoy index)
│   ├── ranker.py            # Strategy A ranking (cosine similarity); Strategy B not built
│   ├── mood.py              # Claude mood → audio features
│   ├── explainer.py         # Claude explanation generation
│   └── utils.py             # empty placeholder — no current use
├── scripts/
│   ├── seed_catalog.py      # Populate tracks table from Kaggle CSV
│   ├── build_index.py       # Build and save Annoy index
│   ├── create_api_key.py    # Generate an API key and assign its A/B group
│   └── test_recommender.py  # Manual smoke test for recommender.py (not a pytest test)
├── models/                  # Committed: annoy_index.ann, scaler.pkl, track_id_map.json (ranker_b.pkl not built)
├── data/                    # dataset.csv — Kaggle catalog for seed_catalog.py (gitignored, local-only)
├── frontend/                # Streamlit dashboard (legacy, kept as internal metrics view — app.py)
├── alembic/                 # Migration environment and versions
├── tests/                   # pytest — test_health.py, test_recommend.py only; full suite is Priority 3
├── .env                     # Never commit
├── alembic.ini
├── render.yaml              # Render Blueprint (API + Postgres)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt

Planned, not yet created (see Next Steps / ML v2 backlog below):
  app/experiment.py          # A/B assignment + metrics — logic currently inlined in main.py, not extracted
  frontend-react/            # React product UI — Priority 1, not yet scaffolded
  .github/workflows/ci.yml   # GitHub Actions CI — Priority 3, not yet created
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
| Ranking | numpy (Strategy A); LightGBM Strategy B not built — deprioritized, see Current Status |
| LLM | Anthropic SDK — claude-sonnet-4-20250514 |
| Spotify client | spotipy |
| Rate limiting | slowapi |
| Testing | pytest + httpx |
| CI | GitHub Actions |
| Frontend (product UI) | React + Vite — Priority 1, not yet scaffolded |
| Frontend (legacy dashboard) | Streamlit |
| Auth | JWT (PyJWT) + passlib/bcrypt — Priority 2, not yet built |
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
- `app/ranker.py` — complete: Strategy A cosine similarity ranker. `ranker_a(query_vector, candidate_ids, db, n=10)` fetches candidate Track objects from DB, scales raw features with saved MinMaxScaler, computes cosine similarity via numpy unit-vector dot product, returns top n `(Track, float)` tuples sorted descending.
- `app/schemas.py` — complete: `TrackRecommendationRequest` (spotify_id, limit with ge=1/le=50), `TrackRecommendation` (single track with from_attributes=True for ORM compatibility), `RecommendationResponse` (full envelope with recommendations list, experiment_group, strategy, log_id).
- `app/main.py` — updated: `POST /recommend/track` wired end-to-end. Seed track lookup with 404 on missing spotify_id, full retrieval → ranking pipeline, returns `RecommendationResponse`. Rate limited and auth protected. Tested and verified with live request.
- `scripts/create_api_key.py` — complete: generates cryptographically secure key with `secrets.token_hex(32)`, deterministically assigns A/B group via MD5 hash (consistent with request-time assignment), inserts into `api_keys` table via ORM.
- `app/mood.py` — complete: sends mood string to Claude, parses JSON response into audio feature dict, returns neutral fallback on any failure.
- `app/explainer.py` — complete: batches all 10 tracks in one Claude call, returns list of explanation strings (null on failure).
- `POST /recommend/mood` in `app/main.py` — complete: validates mood input, calls `mood.py` → `get_candidates` → `ranker_a` → `explainer.py`, returns `RecommendationResponse` with explanations.
- `recommendation_logs` insert — complete: both `/recommend/track` and `/recommend/mood` write to `recommendation_logs` and return real `log_id`.
- `frontend/app.py` (Streamlit, "Moodify") — complete: mood/track toggle, song cards with similarity bars and Claude explanations, hover-reveal Spotify links and A/B badges, `GET /search/tracks` autocomplete backing track search. Now the internal metrics/demo dashboard, not the product-facing UI going forward.
- `GET /search/tracks` — complete: autocomplete on track name/artist, ILIKE + popularity order, top 10, no auth, 30 req/min.
- Render deployment prep — complete (repo-side): `render.yaml` Blueprint, Dockerfile honors `$PORT`, `database.py` normalizes `postgres://`, `models/` artifacts committed. Remaining (manual): provision on Render, seed prod DB, set `ANTHROPIC_API_KEY`. Runbook in `docs/project_spec.md` Section 21.

**ML v2 backlog (accurate gap, deliberately not prioritized — see Project Goals):**
- `POST /feedback`, `GET /experiments/results` — not built
- Strategy B (LightGBM ranker) — not built
- A/B assignment — both endpoints hardcode `experiment_group="A"`; not wired to the API-key hash yet

**In progress:**
- Nothing

**Next steps (current priority, in order — full detail in `docs/project_spec.md` Part 3):**
1. React frontend — scaffold `frontend-react/` (Vite), rebuild the mood/track search + results flow as real components, replacing Streamlit as the product-facing UI
2. Auth & user accounts — JWT access/refresh tokens, bcrypt password hashing, `users` table, `/auth/*` endpoints, `user_id` on `recommendation_logs`/`feedback`
3. Testing + CI/CD — expand `tests/` beyond `test_health.py`/`test_recommend.py` to a full pytest suite (backend + auth), wire GitHub Actions to run on push and auto-deploy to Render on merge
4. System design write-up — `docs/SYSTEM_DESIGN.md` covering architecture, explicit tradeoffs, scaling, and known limitations
5. (Stretch) Real-time/concurrent feature — streamed explanations, live experiment metrics, or documented load/concurrency testing

---

## Documentation

- [Overview](docs/overview.md) — full project context, career goals, background
- [Project Spec](docs/project_spec.md) — detailed requirements, API contract, architecture decisions; Part 3 (Sections 24–28) is the current SWE roadmap
- Update files in docs folder after major milestones and major additions to the project
