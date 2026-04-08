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
spotify-recsys/
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

**In progress:**
- `app/main.py` — not started

**Next step:**
Write `app/main.py` — minimal FastAPI app that starts up, calls `Base.metadata.create_all()`, and serves `GET /health`. Verify with `docker compose up app` then `curl http://localhost:8000/health`.

---

## Documentation

- [Overview](docs/overview.md) — full project context, career goals, background
- [Project Spec](docs/PROJECT_SPEC.md) — detailed requirements, API contract, architecture decisions
- Update files in docs folder after major milestones and major additions to the project
