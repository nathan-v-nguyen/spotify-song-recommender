# Moodify — Project Context for Claude

## Who I Am

- Name: Nathan Nguyen
- Student: Data Science major at UC San Diego, GPA 3.9, graduating June 2027
- Current: NREIP data engineering internship (SQL pipelines, Azure SQL)
- Goal: Software Engineering internship at a startup, with consumer tech companies like Meta/TikTok as stretch targets — **not** an ML/DS role
- Experience: Python, Flask, FastAPI, SQL, PostgreSQL, Google Cloud Run, Firestore, scikit-learn, pandas, numpy
- Gaps I'm closing with this project now: a real React frontend, user auth (JWT/sessions), testing + CI/CD, a system design write-up, and — as a stretch — a real-time/concurrent feature

---

## Project Evolution — Why the Pivot

This project started as a two-stage retrieval-ranking recommendation pipeline, and that ML core is now done: Annoy-based retrieval, cosine-similarity ranking, Claude-based mood translation and explanation generation, and a deterministic A/B testing framework (MD5 bucketing, request logging, feedback collection, Streamlit metrics dashboard).

I originally leaned toward an "ML" career identity because I'm good at math and it seemed like the obvious path. After reflecting on it, my actual strengths and interests point toward product/application software engineering: I do my best work on well-scoped, correctness-driven problems, I want to build things that end up in front of real users, and open-ended data cleaning and ambiguous ML experimentation is draining rather than energizing for me.

**So the ML/recommendation core is done and is not the focus going forward.** The goal now is to turn Moodify into a complete SWE product by closing specific skill gaps, in this priority order:

1. A real React frontend (currently API-only plus a Streamlit dashboard — no real product UI)
2. User accounts and auth (JWT/sessions), with saved history and feedback tied to real users
3. Testing (pytest unit + integration) and CI/CD (GitHub Actions: test on push, auto-deploy on merge)
4. A system design write-up explaining architecture decisions and tradeoffs
5. (Stretch) A real-time/concurrent feature — a systems-engineering signal this project otherwise lacks

Full detail on each of these lives in `docs/project_spec.md`, Part 3 (Sections 24–28).

**How I want Claude to help:** prioritize teaching the underlying SWE fundamentals while building — not just producing working code. I dislike "vibe coding" parts I don't understand, so explain the *why* behind frontend/auth/testing patterns as we go. Treat this as a resume/interview-defensible project: I should be able to confidently explain any architectural decision in a technical interview.

---

## What This Project Is

A full-stack music recommendation product with three things that made the ML core unique, plus a product layer now being built on top of it:

1. **Natural language mood input** — user types "late night drive feeling nostalgic", Claude translates it into audio feature targets, system returns matching songs
2. **Explainability** — every recommendation includes a plain English explanation of why it fits the mood
3. **A/B testing framework** — two ranking strategies run in parallel, every request is logged, live metrics compare which strategy performs better (backend infrastructure exists; see Current Status)

The ML pipeline above is the backdrop, not the pitch. The pitch, going forward, is a complete SWE product: a real React frontend, real user accounts and auth, a tested and CI/CD'd backend, and an architecture Nathan can defend in an interview — built to demonstrate software engineering skill to SWE internship interviewers, not ML engineering skill to ML hiring managers.

---

## Career Context

**Target role:** Software Engineering Intern — startups, product/application engineering  
**Stretch target companies:** Meta, TikTok, and other consumer tech companies (as stretch, not primary targets)  
**Why this project now:** the ML/recommendation core is done. What's left — frontend, auth, testing, CI/CD, systems design — is exactly the SWE skill set this project didn't previously demonstrate, and exactly what SWE internship interviewers actually probe for.

---

## Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| Frontend (legacy) | Streamlit | Internal metrics/demo dashboard — no longer the product-facing UI |
| Frontend (product) | React + Vite + TypeScript | Real product UI — current top priority, in progress (mood flow working end-to-end); see Project Evolution above |
| Auth | JWT (PyJWT) + passlib/bcrypt | User accounts, sessions, saved history — see project_spec.md Section 25 |
| API framework | FastAPI | Main API layer |
| Validation | Pydantic | Request/response schemas |
| Rate limiting | slowapi | Max 10 req/min per IP |
| Auth | Custom middleware | API key validation |
| ML — similarity | Annoy | ANN index for fast track retrieval |
| ML — ranking | numpy | Strategy A ranker (cosine similarity); Strategy B not built |
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
│   ├── main.py              # FastAPI app, all route definitions (A/B group hardcoded to "A")
│   ├── models.py            # SQLAlchemy database models (tables)
│   ├── schemas.py           # Pydantic request/response shapes
│   ├── database.py          # DB engine, session factory, Base, get_db
│   ├── auth.py              # API key validation middleware
│   ├── limiter.py           # Rate limiting setup
│   ├── recommender.py       # Core recommendation logic (retrieval)
│   ├── ranker.py            # Strategy A ranker (cosine similarity); Strategy B not built
│   ├── mood.py              # Claude mood → audio feature targets
│   ├── explainer.py         # Claude explanation generation per track
│   └── utils.py             # empty placeholder — no current use
├── scripts/
│   ├── seed_catalog.py      # Load tracks from Kaggle CSV, populate DB
│   ├── build_index.py       # Build and save Annoy index from DB
│   ├── create_api_key.py    # Generate an API key and assign its A/B group
│   └── test_recommender.py  # Manual smoke test for recommender.py (not a pytest test)
├── models/                  # Committed so Render can load them at startup
│   ├── annoy_index.ann      # Saved Annoy index
│   ├── scaler.pkl           # Fitted MinMaxScaler
│   └── track_id_map.json    # Annoy position → spotify_id list
│                            # (ranker_b.pkl — Strategy B model — not built)
├── data/                    # dataset.csv — Kaggle catalog for seed_catalog.py (gitignored, local-only)
├── frontend/
│   └── app.py               # Streamlit demo app
├── alembic/                 # Migration environment and versions
├── tests/
│   ├── test_health.py       # Health check tests
│   └── test_recommend.py    # Tests for recommendation endpoints
├── .env                     # Secrets — never commit this
├── .gitignore
├── alembic.ini
├── render.yaml              # Render Blueprint (API + Postgres)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt

Planned, not yet created (see Next steps below):
  app/experiment.py          # A/B assignment + metrics — currently inlined in main.py, not extracted
  frontend-react/            # React product UI — Priority 1, not yet scaffolded
  .github/workflows/ci.yml   # GitHub Actions CI — Priority 3, not yet created
  tests/test_experiment.py, tests/test_mood.py  # part of the Priority 3 test suite
```

---

## Database Schema

### tracks table
Stores every song in the catalog with audio features sourced from a Kaggle dataset (Spotify deprecated their audio features API in 2024).

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
popularity      Integer      # 0–100, Spotify popularity score
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

Implemented (live in `app/main.py`):
```
GET  /health                     → system health check, no auth required
GET  /search/tracks              → autocomplete: song name → up to 10 matching tracks, no auth required
POST /recommend/track            → seed track in, top 10 similar tracks out
POST /recommend/mood             → natural language mood → top 10 tracks with explanations
```

Planned / not yet built (design contract in project_spec.md Section 6):
```
GET  /recommend/explain/{id}     → explanation for a specific recommendation log
POST /feedback                   → thumbs up/down on a specific track recommendation   (ML v2 backlog)
GET  /experiments/results        → live A/B metrics comparing Strategy A vs B           (ML v2 backlog)
GET  /catalog/stats              → total tracks, audio feature distributions
GET  /track/{spotify_id}         → details on a specific track
```

All write endpoints require `X-API-Key` header. Rate limited to 10 requests per minute per IP (`/search/tracks` allows 30/min to support typing).

---

## How the Recommendation Pipeline Works

### Offline (run once to set up)
1. `scripts/seed_catalog.py` — loads tracks from Kaggle CSV dataset (Spotify audio features API deprecated in 2024), stores audio features + popularity in `tracks` table
2. `scripts/build_index.py` — loads all audio feature vectors from DB, builds Annoy index, saves to `models/annoy_index.ann`
3. Train Strategy B model — fit a weighted ranking model on audio features, save to `models/ranker_b.pkl` *(not built — ML v2 backlog)*

### Online (every user request)
> **Current reality:** steps 5–7 are the intended design but are *not yet wired* — `experiment_group` is hardcoded to `"A"` in `main.py` and every request runs Strategy A. Strategy B and real A/B assignment are ML v2 backlog (see Current Status).

1. Request arrives at FastAPI → rate limiter checks → auth validates API key
2. If mood endpoint: send mood text to Claude → get back structured audio feature targets as JSON
3. Convert input to query vector (9 audio features: 8 original + popularity)
4. Search Annoy index → retrieve top 500 candidate tracks
5. Hash API key → assign user to Group A or Group B deterministically *(not yet wired — hardcoded to A)*
6. Group A: rank 500 candidates by cosine similarity (Strategy A)
7. Group B: rank 500 candidates using mood-weighted model (Strategy B) *(not built)*
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
- scripts/seed_catalog.py — complete: loads tracks from Kaggle CSV (Spotify audio features API deprecated 2024), deduplicates on spotify_id, writes to tracks table with popularity as an additional feature. 89,740 tracks loaded.
- scripts/build_index.py — complete: fits MinMaxScaler on 9-feature matrix (energy, valence, danceability, tempo, acousticness, instrumentalness, loudness, speechiness, popularity), builds Annoy index (50 trees, angular distance), saves 3 artifacts to models/: annoy_index.ann (60MB), track_id_map.json (2.2MB), scaler.pkl (1KB). Verified — nearest neighbor queries return valid spotify_ids.
- app/recommender.py — complete: loads Annoy index, MinMaxScaler, and track_id_map at module level. `track_to_vector(track)` extracts 9 raw features from a Track ORM object. `get_candidates(query_vector, n=500)` normalizes via saved scaler and returns nearest spotify_ids. Verified with smoke test.
- app/ranker.py — complete: Strategy A cosine similarity ranker. `ranker_a(query_vector, candidate_ids, db, n=10)` fetches candidate Track objects from DB, scales raw feature vectors with saved MinMaxScaler, computes cosine similarity via numpy unit-vector dot product, returns top n `(Track, float)` tuples sorted by score descending.
- app/schemas.py — complete: `TrackRecommendationRequest` (spotify_id, limit with ge=1/le=50 validation), `TrackRecommendation` (single track response with from_attributes=True for ORM compatibility), `RecommendationResponse` (full envelope with recommendations list, experiment_group, strategy, log_id).
- app/main.py — updated: `POST /recommend/track` wired end-to-end. Seed track lookup with 404 on missing spotify_id, full retrieval → ranking pipeline, returns `RecommendationResponse`. Rate limited and auth protected. Tested and verified with live request.
- scripts/create_api_key.py — complete: generates cryptographically secure key with `secrets.token_hex(32)`, deterministically assigns A/B group using MD5 hash (consistent with request-time assignment), inserts into api_keys table via ORM.
- app/mood.py — complete: sends mood string to Claude (claude-sonnet-4-20250514), parses JSON response into 8-feature audio feature dict, returns neutral fallback values on any Claude failure or JSON parse error.
- app/explainer.py — complete: batches all 10 tracks in a single Claude call, returns list of explanation strings ordered to match input tracks, returns list of nulls on any failure without failing the request.
- app/main.py — updated: `POST /recommend/mood` wired end-to-end. Validates mood input (1–500 chars), calls mood.py → get_candidates → ranker_a → explainer.py, returns RecommendationResponse with explanations. Rate limited and auth protected.
- recommendation_logs insert — complete: both `/recommend/track` and `/recommend/mood` write a RecommendationLog row and return the real generated log_id in the response envelope.
- frontend/app.py (Moodify) — complete: Streamlit single-page demo app. Dark minimal UI with olive green background (#6B8F71), Mood/Track mode toggle (st.radio styled as pills), text input, Find Music button, 10 song cards with similarity score bars and Claude explanations, hover-reveal Spotify links and A/B badges. Runs with `streamlit run frontend/app.py`.
- GET /search/tracks — complete: autocomplete endpoint. Case-insensitive ILIKE match on track name OR artist, ordered by popularity descending, capped at 10 results. No auth, rate limited 30/min. Backs the Track-mode search box in the frontend.
- frontend/app.py Track mode — updated: replaced the raw Spotify-ID field with a search-box → dropdown → Find Music flow. User types a song name, matches populate a styled selectbox as "Song — Artist", and the selected track's spotify_id is sent to /recommend/track. Search results cached with st.cache_data (5-min TTL). Track input wrapped in st.container(border=True) so it matches the mood form's white box. Note: Streamlit reruns on Enter/blur, not per keystroke, so the dropdown refreshes after typing + Enter rather than as a live typeahead.
- Render deployment prep — complete (repo-side): render.yaml Blueprint (API web service + free Postgres, DATABASE_URL auto-wired, ANTHROPIC_API_KEY as manual secret); Dockerfile CMD honors Render's $PORT; app/database.py normalizes postgres:// → postgresql:// and fails clearly if DATABASE_URL is unset; models/ artifacts un-ignored and committed so the API loads them at startup; frontend reads API_BASE/API_KEY from Streamlit secrets with localhost fallback. Remaining (manual): provision on Render, seed the prod DB from local, set ANTHROPIC_API_KEY, deploy frontend to Streamlit Community Cloud. Full runbook in PROJECT_SPEC Section 21.

In progress:
- Nothing

**ML v2 backlog (not currently prioritized):** POST /feedback endpoint, GET /experiments/results, Strategy B LightGBM ranker, A/B assignment wired to real group (currently hardcoded to "A"). These are accurate gaps in the ML core but are deliberately not being worked on — see Project Evolution above. Full detail in `docs/project_spec.md` Section 3.

**Next steps (current priority, in order) — see `docs/project_spec.md` Part 3 for full detail on each:**
1. React frontend (Section 24) — replace Streamlit as the product-facing UI: auth pages, mood/track search, results view, history page
2. Auth & user accounts (Section 25) — JWT access/refresh tokens, bcrypt password hashing, `users` table, `/auth/*` endpoints, nullable `user_id` on `recommendation_logs` and `feedback`
3. Testing + CI/CD (Section 26) — pytest unit + integration tests (backend), component tests (frontend, stretch), GitHub Actions running tests on push and auto-deploying on merge to main
4. System design write-up (Section 27) — `docs/SYSTEM_DESIGN.md` covering architecture, explicit tradeoffs, scaling discussion, and known limitations
5. (Stretch) Real-time/concurrent feature (Section 28) — streamed explanations, live experiment metrics, or documented concurrency/load testing

---

## Key Concepts to Know

**Embeddings** — a list of numbers representing a song's audio characteristics. Spotify provides 8 audio features per track. These 8 numbers are the embedding. Similar songs have similar numbers.

**ANN (Approximate Nearest Neighbor)** — fast similarity search. Instead of comparing a query vector against all 5,000 songs exactly, Annoy finds the ~500 closest songs approximately in milliseconds. Built by Spotify. Used via the `annoy` Python library.

**Retrieval → Ranking** — two stage pipeline. Retrieval (fast, approximate): narrow 5,000 songs to 500 candidates using Annoy. Ranking (slower, precise): score those 500 carefully and pick top 10.

**A/B testing** — run two strategies simultaneously on different users, measure which performs better via feedback. Assignment must be deterministic (same user always same group).

**Cold start** — what happens when a new user has no history. Handle by falling back to mood-only recommendation without personalization.

**JWT (JSON Web Token)** — a signed, stateless token proving who a user is without the server storing session state. An access token (short-lived) authorizes requests; a refresh token (longer-lived, httpOnly cookie) is used to get a new access token without re-logging-in. See project_spec.md Section 25.

**CI (Continuous Integration)** — automatically running the test suite on every push, so broken code is caught before it merges, not after it deploys.

**CD (Continuous Deployment)** — automatically deploying to production after CI passes on a merge to main. The thing that actually blocks a bad merge is a required status check via branch protection, not the deploy config itself.

**Concurrency vs parallelism** — concurrency is structuring a program to handle multiple in-flight operations (e.g. many requests, or streaming a response while other work continues); parallelism is literally running things at the same time on multiple cores. The Section 28 stretch goal is about concurrency (async I/O, streaming), not parallel computation.

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
- Frontend: functional components + hooks only, one component per file, keep components presentational where possible (data fetching in a small api client module, not scattered inline)
- Every new backend endpoint ships with a pytest test in the same PR — not added later