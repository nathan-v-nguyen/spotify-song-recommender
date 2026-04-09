# Spotify Mood RecSys — Project Context for Claude Code

## Who I Am

- Name: Nathan Nguyen
- Student: Data Science major at UC San Diego, GPA 3.9, graduating June 2027
- Current: NREIP data engineering internship (SQL pipelines, Azure SQL)
- Goal: ML Engineer role at a FAANG or FAANG-adjacent company in social/consumer tech
- Experience: Python, Flask, FastAPI, SQL, PostgreSQL, Google Cloud Run, Firestore, scikit-learn, pandas, numpy
- Gaps I'm closing with this project: Docker, CI/CD, production APIs, ANN indexing, A/B testing infrastructure

---

## What This Project Is

A production-grade music recommendation API with three things that make it unique:

1. **Natural language mood input** — user types "late night drive feeling nostalgic", Claude translates it into audio feature targets, system returns matching songs
2. **Explainability** — every recommendation includes a plain English explanation of why it fits the mood
3. **A/B testing framework** — two ranking strategies run in parallel, every request is logged, live metrics compare which strategy performs better

This is not a tutorial project. It is built to demonstrate ML engineering skills to interviewers — production API patterns, experiment infrastructure, LLM integration, Docker, CI/CD, deployment.

---

## Career Context

**Target role:** ML Engineer — Social/Consumer Tech  
**Target companies:** Meta, Google, TikTok, Snap, FAANG-adjacent  
**Why this project:** Feed ranking and recommendation systems are the core ML problem at every consumer tech company. This project demonstrates I understand the retrieval → ranking pipeline, can build production systems, and think about infrastructure not just models.

---

## Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| Frontend | Streamlit | Demo UI for interviews |
| API framework | FastAPI | Main API layer |
| Validation | Pydantic | Request/response schemas |
| Rate limiting | slowapi | Max 10 req/min per IP |
| Auth | Custom middleware | API key validation |
| ML — similarity | Annoy | ANN index for fast track retrieval |
| ML — ranking | scikit-learn | Strategy A and B rankers |
| LLM | Anthropic SDK (claude-sonnet-4-20250514) | Mood translation + explanations |
| Feature processing | numpy, pandas | Audio feature vectors |
| Database | PostgreSQL 15 | Main data store |
| ORM | SQLAlchemy | Database models and queries |
| Migrations | Alembic | Schema version control |
| Spotify client | spotipy | Spotify API wrapper |
| Containerization | Docker + docker-compose | Run everything with one command |
| Testing | pytest + httpx | API and unit tests |
| CI/CD | GitHub Actions | Run tests on every push |
| Deployment | Render | Free cloud hosting |

---

## Project File Structure

```
spotify-song-recommender/
├── app/
│   ├── main.py              # FastAPI app, all route definitions
│   ├── models.py            # SQLAlchemy database models (tables)
│   ├── schemas.py           # Pydantic request/response shapes
│   ├── database.py          # DB engine, session factory, Base, get_db
│   ├── auth.py              # API key validation middleware
│   ├── limiter.py           # Rate limiting setup
│   ├── recommender.py       # Core recommendation logic (retrieval)
│   ├── ranker.py            # Strategy A and B ranking models
│   ├── experiment.py        # A/B assignment and metrics calculation
│   ├── mood.py              # Claude mood → audio feature targets
│   └── explainer.py         # Claude explanation generation per track
├── scripts/
│   ├── seed_catalog.py      # Pull tracks from Spotify API, populate DB
│   └── build_index.py       # Build and save Annoy index from DB
├── models/
│   ├── annoy_index.ann      # Saved Annoy index (generated, not committed)
│   └── ranker_b.pkl         # Saved Strategy B sklearn model (generated)
├── frontend/
│   └── app.py               # Streamlit demo app
├── tests/
│   ├── test_recommend.py    # Tests for recommendation endpoints
│   ├── test_experiment.py   # Tests for A/B assignment and metrics
│   ├── test_mood.py         # Tests for mood translation endpoint
│   └── test_health.py       # Health check tests
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI pipeline
├── .env                     # Secrets — never commit this
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Database Schema

### tracks table
Stores every song in the catalog with Spotify audio features.

```python
id              Integer, primary key, auto-increment
spotify_id      String, unique, indexed, not null
name            String, not null
artist          String, not null
album           String
energy          Float        # 0.0–1.0, intensity and activity
valence         Float        # 0.0–1.0, musical positivity
danceability    Float        # 0.0–1.0, how suitable for dancing
tempo           Float        # BPM
acousticness    Float        # 0.0–1.0, acoustic vs electric
instrumentalness Float       # 0.0–1.0, predicts no vocals
loudness        Float        # dB, typically -60 to 0
speechiness     Float        # 0.0–1.0, spoken word presence
created_at      DateTime, server default now()
```

### recommendation_logs table
Logs every request for monitoring and A/B experiment data.

```python
id              Integer, primary key, auto-increment
request_type    String       # "track" or "mood"
input_data      String       # what the user sent
experiment_group String      # "A" or "B"
strategy_used   String       # "cosine_similarity" or "mood_weighted"
recommendations String       # JSON array of returned spotify_ids
created_at      DateTime, server default now()
```

### feedback table
Thumbs up/down tied to specific recommendation logs.

```python
id              Integer, primary key, auto-increment
log_id          Integer, foreign key → recommendation_logs.id
spotify_id      String       # which track was rated
rating          Integer      # 1 = thumbs up, -1 = thumbs down
created_at      DateTime, server default now()
```

### api_keys table
Stores valid API keys and their experiment group assignment.

```python
id              Integer, primary key, auto-increment
key             String, unique, indexed
experiment_group String      # "A" or "B", assigned at key creation
created_at      DateTime, server default now()
```

---

## API Endpoints

```
GET  /health                     → system health check, no auth required
POST /recommend/track            → seed track in, top 10 similar tracks out
POST /recommend/mood             → natural language mood → top 10 tracks with explanations
GET  /recommend/explain/{id}     → explanation for a specific recommendation log
POST /feedback                   → thumbs up/down on a specific track recommendation
GET  /experiments/results        → live A/B metrics comparing Strategy A vs B
GET  /catalog/stats              → total tracks, audio feature distributions
GET  /track/{spotify_id}         → details on a specific track
```

All write endpoints require `X-API-Key` header. Rate limited to 10 requests per minute per IP.

---

## How the Recommendation Pipeline Works

### Offline (run once to set up)
1. `scripts/seed_catalog.py` — calls Spotify API, pulls 2,000–5,000 tracks across genres and moods, stores audio features in `tracks` table
2. `scripts/build_index.py` — loads all audio feature vectors from DB, builds Annoy index, saves to `models/annoy_index.ann`
3. Train Strategy B model — fit a weighted ranking model on audio features, save to `models/ranker_b.pkl`

### Online (every user request)
1. Request arrives at FastAPI → rate limiter checks → auth validates API key
2. If mood endpoint: send mood text to Claude → get back structured audio feature targets as JSON
3. Convert input to query vector (8 audio features)
4. Search Annoy index → retrieve top 500 candidate tracks
5. Hash API key → assign user to Group A or Group B deterministically
6. Group A: rank 500 candidates by cosine similarity (Strategy A)
7. Group B: rank 500 candidates using mood-weighted sklearn model (Strategy B)
8. Top 10 tracks selected
9. For each track: call Claude to generate one-sentence explanation
10. Log full request to `recommendation_logs` table
11. Return top 10 tracks with explanations and experiment group metadata

---

## The A/B Testing Framework

### Assignment
```python
import hashlib
group = "A" if int(hashlib.md5(api_key.encode()).hexdigest(), 16) % 2 == 0 else "B"
```
Same API key always gets same group. Deterministic, no randomness at request time.

### Strategy A — Cosine similarity
Rank candidates by vector distance to query. Pure math, no model. Baseline.

### Strategy B — Mood-weighted ranking
sklearn model (start with GradientBoostingRegressor or LinearRegression) that weights audio features differently based on mood context. Trained on labeled mood-feature pairs.

### Metrics endpoint response shape
```json
{
  "strategy_a": {
    "total_requests": 142,
    "positive_feedback": 89,
    "negative_feedback": 23,
    "feedback_rate": 0.79
  },
  "strategy_b": {
    "total_requests": 138,
    "positive_feedback": 98,
    "negative_feedback": 19,
    "feedback_rate": 0.84
  },
  "winner": "strategy_b",
  "statistical_significance": false
}
```

---

## Claude API Usage

Model: `claude-sonnet-4-20250514`  
Two uses:

### 1. Mood → audio feature targets (mood.py)
Send the user's natural language mood, get back structured JSON with target audio feature values.

Expected response shape:
```json
{
  "energy": 0.35,
  "valence": 0.25,
  "danceability": 0.40,
  "tempo": 85.0,
  "acousticness": 0.60,
  "instrumentalness": 0.20,
  "loudness": -12.0,
  "speechiness": 0.05
}
```

Always prompt Claude to respond with JSON only, no preamble. Parse with try/except — if Claude returns invalid JSON, fall back to neutral feature values.

### 2. Explanation generation (explainer.py)
For each recommended track, send mood description + track audio features, get back one sentence explaining why the track fits.

Keep explanations under 30 words. Batch all 10 tracks in one API call using a list in the prompt — don't make 10 separate calls.

---

## Environment Variables (.env)

```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
ANTHROPIC_API_KEY=your_key
DATABASE_URL=postgresql://postgres:password@db:5432/recsys
API_KEY=supersecretkey123
```

Note: `DATABASE_URL` uses `@db` as host when running inside Docker. Use `@localhost` when running outside Docker for local testing.

---

## Docker Setup

### docker-compose.yml services
- `db` — PostgreSQL 15, port 5432, volume for data persistence
- `app` — FastAPI app, port 8000, depends on db, mounts project directory

### Key commands
```bash
docker compose up db          # start database only
docker compose up             # start everything
docker compose up --build     # rebuild image and start
docker compose logs app       # see app logs
docker compose down           # stop everything
```

### Verify database is running
```bash
docker ps                     # should show db container as "Up"
docker compose logs db        # look for "ready to accept connections"
```

---

## Milestone Plan

### MVP (build first — nothing else until this works)
- database.py and models.py complete and verified
- tracks and recommendation_logs tables created in PostgreSQL
- seed_catalog.py pulls real tracks from Spotify API into DB
- Annoy index built from catalog
- POST /recommend/track works end to end
- GET /health works
- API key auth on protected endpoints
- Entire app runs with docker compose up

### v1
- POST /recommend/mood with Claude mood translation
- Explanation on every recommendation
- Rate limiting
- Request logging to DB
- Proper error handling (400, 401, 404, 422, 429)
- Strategy A cosine similarity ranker

### v2
- A/B testing framework complete
- POST /feedback endpoint
- GET /experiments/results with live metrics
- Cold start handling
- pytest suite (10+ tests)
- GitHub Actions CI

### Later
- Streamlit frontend deployed
- Render deployment (live public URL)
- GET /catalog/stats
- Mood history and drift detection

### Not in scope
- Real Spotify user OAuth
- Streaming responses
- Mobile app
- Real-time model retraining
- Payments

---

## Current Status

Completed:
- Spotify developer app created (Client ID and Secret obtained)
- Project folder structure created
- Docker Desktop installed and running
- docker-compose.yml written and validated
- Dockerfile written
- requirements.txt written
- .env file configured
- PostgreSQL running in Docker (verified with docker compose up db)
- app/database.py — complete (engine, SessionLocal, Base, get_db)
- app/models.py — complete (Track, RecommendationLog, Feedback, ApiKey)
- Alembic initialized — first migration applied, all 4 tables verified in PostgreSQL
- app/main.py — complete: FastAPI app with lifespan startup, GET /health with DB connectivity check, rate limiter wired in, catch-all 500 handler
- app/limiter.py — complete: slowapi Limiter keyed by client IP, 10 req/min per route
- app/auth.py — complete: require_api_key dependency validates X-API-Key header against api_keys table, returns ApiKey record for A/B group access

In progress:
- scripts/seed_catalog.py — not started

Next steps:
- Write scripts/seed_catalog.py — pull 2,000–5,000 tracks from Spotify API, store audio features in tracks table
- Write scripts/build_index.py — build and save Annoy index from catalog
- Then write app/recommender.py and POST /recommend/track

---

## Key Concepts to Know

**Embeddings** — a list of numbers representing a song's audio characteristics. Spotify provides 8 audio features per track. These 8 numbers are the embedding. Similar songs have similar numbers.

**ANN (Approximate Nearest Neighbor)** — fast similarity search. Instead of comparing a query vector against all 5,000 songs exactly, Annoy finds the ~500 closest songs approximately in milliseconds. Built by Spotify. Used via the `annoy` Python library.

**Retrieval → Ranking** — two stage pipeline. Retrieval (fast, approximate): narrow 5,000 songs to 500 candidates using Annoy. Ranking (slower, precise): score those 500 carefully and pick top 10.

**A/B testing** — run two strategies simultaneously on different users, measure which performs better via feedback. Assignment must be deterministic (same user always same group).

**Cold start** — what happens when a new user has no history. Handle by falling back to mood-only recommendation without personalization.

---

## Code Style Preferences

- Keep files single-responsibility — one clear purpose per file
- Use type hints on all function signatures
- Pydantic models for all request and response shapes
- SQLAlchemy ORM for all database operations — no raw SQL strings
- Load all secrets from environment variables via python-dotenv — never hardcode
- All API errors should return meaningful messages, never raw 500s
- Write try/except around all Claude API calls with sensible fallbacks
- Comment architectural decisions, not obvious code