# Project Spec: Spotify Mood RecSys

**Author:** Nathan Nguyen  
**Type:** Personal portfolio project  
**Primary audience:** FAANG recruiters and ML engineering hiring managers  
**Definition of done:** Live deployed URL on Render that anyone can hit  
**Most important quality:** Code quality — clean, readable, well tested  
**Claude Code usage:** Claude Code writes boilerplate, Nathan writes core logic  

---

## 1. Product Definition

### What is this?

A production-grade music recommendation API that accepts either a seed track or a natural language mood description and returns 10 personalized song recommendations — each with a plain English explanation of why it fits.

The system runs a live A/B experiment comparing two ranking strategies, logs every request, collects user feedback, and exposes real-time experiment metrics. Everything is containerized, tested, and deployed.

### What problem does it solve?

**For users:** Existing music discovery tools require you to already know what you want. You can't tell Spotify "I want something for a late night drive feeling nostalgic" and get back music that actually fits that feeling. This system bridges natural language and audio features using an LLM.

**For Nathan's career:** Demonstrates end-to-end ML engineering skills to FAANG hiring managers — specifically the retrieval → ranking pipeline, experiment infrastructure, LLM integration in production, and the ability to ship a real deployed system.

### Who is it for?

| User | What they do with it |
|---|---|
| FAANG recruiters | View the live URL, read the README, assess engineering maturity |
| ML engineering hiring managers | Evaluate architecture decisions, experiment design, code quality |
| Nathan (builder) | Learn production ML engineering patterns by building them |
| General users | Type a mood, get song recommendations, rate them |

### Jobs to be done

- **As a user**, I want to describe how I'm feeling in plain English and get songs that match that feeling, so I don't have to know the technical name for what I want.
- **As a user**, I want to understand why each song was recommended, so I can trust the system.
- **As a user**, I want to rate recommendations so the system can learn what works.
- **As a recruiter**, I want to see a live deployed URL and a clean README so I can evaluate the project in under 5 minutes.
- **As a hiring manager**, I want to see production-quality code with tests, CI, and thoughtful architecture decisions documented.

---

## 2. What the Product Does

### Core user flows

**Flow 1 — Mood-based recommendation (primary flow)**
1. User sends a POST request with a natural language mood string and their API key
2. System sends mood to Claude, receives structured audio feature targets as JSON
3. System searches Annoy index and retrieves 500 candidate tracks
4. System assigns user to experiment Group A or B based on API key hash
5. Group A ranks candidates by cosine similarity; Group B uses mood-weighted model
6. Top 10 tracks selected, Claude generates one-sentence explanation per track
7. Request logged to database with group assignment and strategy used
8. Response returned: 10 tracks with name, artist, Spotify ID, explanation, and experiment group badge

**Flow 2 — Seed track recommendation (secondary flow)**
1. User sends a POST request with a Spotify track ID and their API key
2. System looks up track's audio features from database
3. System searches Annoy index for similar tracks
4. Same ranking and logging pipeline as Flow 1
5. Response returned: 10 similar tracks with explanations

**Flow 3 — Feedback submission**
1. User sends a POST request with a recommendation log ID, a track Spotify ID, and a rating (1 or -1)
2. System validates the log ID exists and belongs to a valid request
3. Rating stored in feedback table linked to the recommendation log
4. Response confirms feedback recorded

**Flow 4 — Experiment results (internal/demo)**
1. User sends a GET request to /experiments/results
2. System aggregates recommendation_logs and feedback tables
3. Returns total requests, positive feedback, negative feedback, and feedback rate per strategy
4. Returns winner if one strategy is ahead and flags whether sample size is statistically significant

---

## 3. Feature Requirements

### MVP — must work before anything else is built

| Feature | Requirement |
|---|---|
| Seed track recommendation | POST /recommend/track accepts a Spotify track ID and returns 10 similar tracks |
| Mood recommendation | POST /recommend/mood accepts a natural language string and returns 10 tracks via Claude translation |
| Health check | GET /health returns {"status": "ok"} with no auth required |
| API key auth | All write endpoints reject requests missing a valid X-API-Key header with 401 |
| Docker | Entire app (API + PostgreSQL) starts with a single `docker compose up` command |
| Database | tracks and recommendation_logs tables exist and are populated before any request can succeed |

### v1 — core product functionality

| Feature | Requirement |
|---|---|
| Explainability | Every recommendation includes a one-sentence Claude-generated explanation of why it fits |
| Rate limiting | Max 10 requests per minute per IP; exceeding returns 429 with a clear error message |
| Request logging | Every request writes to recommendation_logs with group, strategy, input, and output |
| Input validation | All endpoints return 422 with a meaningful message on malformed input, never 500 |
| Error handling | 400 for bad requests, 401 for missing auth, 404 for not found, 422 for validation, 429 for rate limit |
| Strategy A ranker | Cosine similarity baseline ranker operational |

### v2 — experiment infrastructure

| Feature | Requirement |
|---|---|
| A/B assignment | API key hashed to deterministically assign Group A or B — same key always same group |
| Strategy B ranker | Mood-weighted scikit-learn ranking model trained and operational |
| Feedback endpoint | POST /feedback accepts log ID, track ID, and rating; stores in feedback table |
| Experiment results | GET /experiments/results returns per-strategy metrics and statistical significance flag |
| Cold start handling | System returns valid recommendations even when user has no prior request history |
| Test suite | 10+ pytest tests covering all endpoints, happy path and at least one error case per endpoint |
| CI pipeline | GitHub Actions runs full test suite on every push to main; failing tests block merge |

### Later — polish and deployment

| Feature | Requirement |
|---|---|
| Streamlit frontend | Single-page UI with mood input, song cards, explanation text, A/B badge, feedback buttons, live experiment sidebar |
| Render deployment | API live at a public Render URL; Streamlit app live at a separate public URL |
| Catalog stats | GET /catalog/stats returns total track count and audio feature distributions |
| Mood history | Track mood inputs per API key over time; surface patterns back to user |

### Not in scope

| Feature | Reason |
|---|---|
| Spotify user OAuth | Adds significant auth complexity with limited portfolio signal |
| Streaming responses | Premature optimization for a portfolio project at this scale |
| Mobile app | Streamlit frontend is sufficient for demo purposes |
| Real-time model retraining | Models trained offline; online learning is out of scope |
| Payments or subscriptions | Not relevant to portfolio goals |
| Multi-tenancy | Single-tenant system is sufficient |

---

## 4. Technical Requirements

### Performance requirements

| Metric | Target | Notes |
|---|---|---|
| Recommendation response time | Under 2 seconds end-to-end | Includes Claude API call for mood translation and explanations |
| Annoy index search | Under 100ms | For 500 candidate retrieval from 5,000 track catalog |
| Health check response | Under 100ms | No database call required |
| Database write (log) | Non-blocking | Log after response is returned, not before |

### Reliability requirements

- API must return a valid response on every request — never an unhandled exception reaching the user
- All Claude API calls wrapped in try/except with sensible fallback behavior
- If Claude returns malformed JSON for mood translation, fall back to neutral audio feature values
- If Claude fails to generate an explanation, return the track with explanation field set to null — do not fail the whole request
- Database connection failures must return 503 with a clear error message

### Code quality requirements

These are non-negotiable given Nathan's stated priority:

- Every function has a type hint on all parameters and return values
- Every module has a one-line docstring describing its purpose
- No function longer than 40 lines — split into smaller functions if needed
- No raw SQL strings — SQLAlchemy ORM only
- No hardcoded secrets anywhere in the codebase — all from environment variables
- All API errors return JSON with a consistent shape: `{"error": "message", "code": 422}`
- Every endpoint has a corresponding pytest test
- Test coverage must cover happy path and at least one failure case per endpoint
- No commented-out code committed to main

### Security requirements

- API keys stored hashed in the database, not plaintext
- `.env` file never committed — `.gitignore` enforced
- Rate limiting on all endpoints to prevent abuse
- Input validation on all user-supplied strings before passing to Claude
- Claude prompts constructed with user input interpolated safely — no prompt injection risk

---

## 5. Architecture Decisions and Rationale

### Why FastAPI over Flask
FastAPI provides automatic OpenAPI docs, native async support, and Pydantic integration out of the box. For a portfolio project, auto-generated docs at `/docs` let any recruiter or hiring manager explore the API without reading code. Flask would require additional setup for all of this.

### Why Annoy over FAISS
Annoy was built by Spotify for exactly this use case — music similarity search. Using it signals domain awareness. FAISS is more powerful but significantly harder to set up. At catalog sizes under 100,000 tracks, Annoy performance is more than sufficient.

### Why two ranking strategies
A single ranking strategy produces a system. Two strategies with experiment infrastructure produces a portfolio piece that demonstrates understanding of how ML teams actually work — running experiments, measuring outcomes, iterating. This is the difference between a data science project and an ML engineering project.

### Why Claude for mood translation and explanation
Rule-based mood-to-feature mapping (e.g. "sad" → low valence) is brittle and limited. Claude can handle nuanced, compositional mood descriptions ("nostalgic but not sad, like driving home after a good night") and return calibrated feature targets. For explanations, template-based approaches produce robotic text. Claude produces natural, varied explanations that make the demo feel alive.

### Why PostgreSQL over SQLite
SQLite is fine for development but signals a toy project. PostgreSQL is what production systems use. Running it in Docker eliminates setup friction while maintaining production parity. This choice signals production thinking.

### Why Docker for a portfolio project
Because "it works on my machine" is not a portfolio. Docker means any recruiter, hiring manager, or collaborator can run the entire system with one command. It also teaches containerization — a direct gap Nathan identified in his skillset.

---

## 6. API Contract

### Authentication
All write endpoints require header: `X-API-Key: <key>`  
Missing or invalid key returns: `{"error": "Invalid or missing API key", "code": 401}`

### Rate limiting
All endpoints: 10 requests per minute per IP  
Exceeded limit returns: `{"error": "Rate limit exceeded. Try again in 60 seconds.", "code": 429}`

### Endpoints

#### GET /health
No auth required.  
Response 200:
```json
{"status": "ok", "catalog_size": 4823, "index_loaded": true}
```

#### POST /recommend/track
Auth required.  
Request:
```json
{"spotify_id": "4uLU6hMCjMI75M1A2tKUQC", "limit": 10}
```
Response 200:
```json
{
  "recommendations": [
    {
      "spotify_id": "string",
      "name": "string",
      "artist": "string",
      "album": "string",
      "explanation": "string",
      "similarity_score": 0.94
    }
  ],
  "experiment_group": "A",
  "strategy": "cosine_similarity",
  "log_id": 142
}
```
Error 404 if spotify_id not in catalog.

#### POST /recommend/mood
Auth required.  
Request:
```json
{"mood": "late night drive feeling nostalgic", "limit": 10}
```
Response 200: same shape as /recommend/track  
Error 422 if mood string is empty or over 500 characters.

#### POST /feedback
Auth required.  
Request:
```json
{"log_id": 142, "spotify_id": "string", "rating": 1}
```
Rating must be 1 (positive) or -1 (negative).  
Response 200:
```json
{"status": "feedback recorded", "log_id": 142}
```
Error 404 if log_id does not exist.

#### GET /experiments/results
Auth required.  
Response 200:
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
  "statistical_significance": false,
  "note": "Insufficient sample size for statistical significance. Need 200+ feedback events per group."
}
```

#### GET /catalog/stats
Auth required.  
Response 200:
```json
{
  "total_tracks": 4823,
  "feature_distributions": {
    "energy": {"mean": 0.63, "std": 0.21},
    "valence": {"mean": 0.49, "std": 0.24}
  }
}
```

#### GET /track/{spotify_id}
Auth required.  
Response 200: full track object with all audio features.  
Error 404 if not found.

---

## 7. Claude Code Usage Guidelines

### What Claude Code should write
- Boilerplate file scaffolding (imports, class definitions, empty functions with docstrings)
- Repetitive patterns (Pydantic schemas, SQLAlchemy model columns, pytest fixtures)
- Docker and CI configuration files
- Database migration scripts
- Streamlit UI layout code

### What Nathan writes
- Core recommendation logic in recommender.py
- A/B assignment logic in experiment.py
- Claude prompt construction in mood.py and explainer.py
- Strategy A and B ranking logic in ranker.py
- All business logic decisions

### How to start each Claude Code session
1. Open terminal in project root
2. Run `claude` to start Claude Code
3. First message: "Read CLAUDE.md and PROJECT_SPEC.md and tell me where we left off and what we're building today."
4. Claude Code will orient itself and propose the next step

### What to ask Claude Code to do
- "Scaffold the schemas.py file with Pydantic models for all request and response shapes defined in PROJECT_SPEC.md"
- "Write the pytest fixtures for the test suite based on our FastAPI app structure"
- "Write the docker-compose.yml and Dockerfile based on the stack in CLAUDE.md"
- "Write the GitHub Actions CI workflow that runs pytest on push to main"

### What not to ask Claude Code to do
- Do not ask Claude Code to make architecture decisions — those are already made and documented here
- Do not ask Claude Code to choose between ranking strategies — Strategy A and B are defined
- Do not ask Claude Code to write the Claude prompt templates — Nathan writes those

### Session ending ritual
At the end of every Claude Code session, say:
> "Update the Current Status section of CLAUDE.md to reflect everything we completed today. List what's done, what's in progress, and what the next step is."

---

## 8. Definition of Done (Per Feature)

A feature is not done until all of the following are true:

- [ ] The endpoint or function works correctly on the happy path
- [ ] At least one error case is handled with a proper error response
- [ ] A pytest test exists for the happy path
- [ ] A pytest test exists for at least one failure case
- [ ] The code has type hints on all function signatures
- [ ] No hardcoded values — all config from environment variables
- [ ] The feature is documented in the README with an example request and response

The full project is not done until:

- [ ] All MVP and v1 features pass definition of done above
- [ ] `docker compose up` starts the entire system from scratch with no manual steps
- [ ] All tests pass in GitHub Actions CI on a clean run
- [ ] The API is live at a public Render URL
- [ ] The Streamlit frontend is live at a public URL
- [ ] The README has a live demo link, architecture diagram, setup instructions, and example requests
- [ ] The project is pinned on Nathan's GitHub profile

---

## 9. Success Metrics

This is a portfolio project, so success is defined by career outcomes, not user metrics.

| Metric | Target |
|---|---|
| Recruiter response rate | At least 1 interview request directly attributable to this project |
| Time to explain in interview | Can walk through full architecture in under 10 minutes |
| Demo reliability | Zero crashes during a live demo |
| Code review readiness | Any senior engineer can read any file and understand it without asking questions |
| GitHub stars | 10+ stars within first month of publishing |

---

## 10. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Spotify API rate limits block catalog seeding | Medium | High | Seed in batches with exponential backoff; cache results locally |
| Claude API latency pushes response over 2s | Medium | Medium | Batch all 10 explanations in one API call; set timeout and return null explanation on failure |
| Annoy index not loading on Render free tier (memory) | Low | High | Test memory usage locally; use smaller catalog if needed; document minimum memory requirement |
| docker compose works locally but fails on Render | Medium | High | Test Render deployment early — do not leave deployment to the last step |
| A/B groups unbalanced due to API key distribution | Low | Low | Log group assignment; verify roughly 50/50 split after seeding test keys |
| Scope creep delays deployment | High | High | Milestone plan is locked — do not add features until deployed URL exists |

---

---

# Part 2: Engineering Design, Tech Stack, and Architecture

---

## 11. Full Tech Stack

### Pinned Versions and Justifications

| Layer | Library / Tool | Version | Why This Choice |
|---|---|---|---|
| Language | Python | 3.11 | Best async support, `tomllib` built-in, type hint improvements; avoid 3.12+ until ecosystem catches up |
| API framework | FastAPI | 0.111.x | Auto OpenAPI docs at `/docs`, native async, Pydantic v2 integration, standard at FAANG-adjacent startups |
| Request validation | Pydantic | v2 | 10x faster than v1; strict mode catches bad data at the boundary; used natively by FastAPI |
| ASGI server | Uvicorn | 0.29.x | FastAPI's recommended production server; supports `--workers` flag for multi-process on Render |
| ORM | SQLAlchemy | 2.0.x | 2.0 style (not legacy 1.x); async-compatible; type-safe queries; industry standard |
| DB migrations | Alembic | 1.13.x | SQLAlchemy-native; version-controlled schema changes; required for any production system |
| Database | PostgreSQL | 15 | ACID, production standard, full SQL, runs in Docker with zero setup |
| DB driver | psycopg2-binary | 2.9.x | Standard sync PostgreSQL driver; psycopg3 not yet necessary at this scale |
| ANN index | Annoy | 1.17.x | Built by Spotify for music similarity; memory-mapped (efficient on Render free tier); dead-simple API |
| Ranking model — A | numpy (cosine similarity) | 1.26.x | No model needed; pure vector math; Strategy A is the baseline |
| Ranking model — B | LightGBM | 4.3.x | Replaces sklearn GBR; 10-50x faster training; used in production ranking at Meta/TikTok/Google; sklearn-compatible API means near-zero migration cost |
| Model serialization | joblib | 1.4.x | Standard for sklearn-compatible models; LightGBM supports `joblib.dump()` |
| LLM | Anthropic SDK | 0.28.x | `claude-sonnet-4-20250514`; structured JSON output; clean Python SDK |
| Spotify client | spotipy | 2.23.x | Official Spotify Web API wrapper; handles OAuth client credentials flow |
| Rate limiting | slowapi | 0.1.9 | Wraps `limits` library; decorator-based; IP extraction works correctly behind Render's reverse proxy |
| Auth middleware | Custom (FastAPI dependency) | — | Simple API key lookup against `api_keys` table; no third-party auth library needed at this scale |
| Environment config | python-dotenv | 1.0.x | Loads `.env` file; standard pattern; never hardcode secrets |
| Feature processing | numpy, pandas | 1.26, 2.2.x | numpy for vector math; pandas for catalog loading and feature normalization |
| Containerization | Docker + docker-compose | Docker 25+, Compose v2 | `docker compose up` starts entire stack; production parity from day one |
| Testing | pytest | 8.x | Industry standard; fixture-based; integrates with httpx for async FastAPI testing |
| HTTP test client | httpx | 0.27.x | Required for async FastAPI `TestClient`; same API as `requests` |
| CI/CD | GitHub Actions | — | Native GitHub integration; YAML lives in `.github/workflows/`; 2,000 free minutes/month |
| Frontend | Streamlit | 1.35.x | Python-only; 50-line demo app; sufficient for interview demos |
| Deployment | Render | — | Docker-native; free web service + PostgreSQL (90-day free then $7/mo); recruiter-friendly live URL |

---

## 12. System Architecture Overview

The system has three runtime environments:

```
LOCAL DEV                  DOCKER (prod-parity)           RENDER (deployed)
─────────────────────      ──────────────────────────     ──────────────────────
.env (secrets)             docker-compose.yml             render.yaml
python scripts/            ┌─────────────────────┐        ┌─────────────────┐
  seed_catalog.py          │  app container      │        │  web service    │
  build_index.py           │  FastAPI + Uvicorn  │        │  FastAPI image  │
models/ (local files)      │  port 8000          │        │  port 8000      │
                           └────────┬────────────┘        └────────┬────────┘
                                    │ SQLAlchemy                    │ DATABASE_URL
                           ┌────────▼────────────┐        ┌────────▼────────┐
                           │  db container       │        │  Render Postgres │
                           │  PostgreSQL 15      │        │  managed DB      │
                           │  port 5432          │        └─────────────────┘
                           └─────────────────────┘
```

### External Services (called at runtime)
- **Anthropic API** — mood translation and explanation generation; called on every `/recommend/mood` request
- **Spotify Web API** — called only during offline seeding (`scripts/seed_catalog.py`); not called at request time

---

## 13. Component Architecture

Every file in `app/` has a single responsibility. Dependencies flow in one direction — no circular imports.

```
Request
  │
  ▼
main.py              ← route definitions, mounts all routers, calls Base.metadata.create_all()
  │
  ├── auth.py        ← FastAPI dependency: validates X-API-Key header against api_keys table
  ├── limiter.py     ← slowapi Limiter instance, shared across all routes
  │
  ├── recommender.py ← loads Annoy index, builds query vector, returns top-N candidate track IDs
  │     └── uses: annoy index (models/annoy_index.ann), database session
  │
  ├── ranker.py      ← Strategy A (cosine similarity) and Strategy B (LightGBM); returns ranked list
  │     └── uses: numpy (A), lightgbm model (models/ranker_b.pkl) (B)
  │
  ├── experiment.py  ← deterministic A/B assignment by API key hash; metrics aggregation queries
  │     └── uses: hashlib (assignment), SQLAlchemy (metrics)
  │
  ├── mood.py        ← sends mood string to Claude, parses JSON response into audio feature dict
  │     └── uses: anthropic SDK
  │
  ├── explainer.py   ← batches 10 tracks into one Claude call, returns list of explanation strings
  │     └── uses: anthropic SDK
  │
  ├── models.py      ← SQLAlchemy ORM table definitions (Track, RecommendationLog, Feedback, ApiKey)
  ├── schemas.py     ← Pydantic request and response models for all endpoints
  └── database.py    ← engine, SessionLocal, Base, get_db dependency
```

---

## 14. Data Flow — Request Lifecycle

### Flow A: POST /recommend/mood (primary flow, full detail)

```
1. HTTP POST arrives at Uvicorn
   └── Headers: X-API-Key, Content-Type: application/json
   └── Body: {"mood": "late night drive feeling nostalgic", "limit": 10}

2. FastAPI middleware stack
   ├── slowapi rate limiter — checks IP against 10 req/min limit
   │     └── 429 if exceeded
   └── auth dependency — queries api_keys table for X-API-Key value
         └── 401 if missing or not found

3. mood.py — translate mood to audio features
   ├── Build system + user prompt (see Section 17 for exact prompts)
   ├── POST to Anthropic API (claude-sonnet-4-20250514)
   ├── Parse JSON response → dict of 8 audio feature floats
   └── On failure (bad JSON, timeout): return neutral fallback values
         {energy: 0.5, valence: 0.5, danceability: 0.5, tempo: 120.0,
          acousticness: 0.5, instrumentalness: 0.0, loudness: -8.0, speechiness: 0.05}

4. recommender.py — candidate retrieval
   ├── Normalize query vector (same normalization as index build step)
   ├── Query Annoy index: get_nns_by_vector(query_vector, n=500)
   └── Return list of 500 internal Annoy IDs → map to spotify_ids via in-memory dict

5. experiment.py — group assignment
   ├── group = "A" if int(hashlib.md5(api_key.encode()).hexdigest(), 16) % 2 == 0 else "B"
   └── Same API key always resolves to same group — no randomness at request time

6. ranker.py — rank 500 candidates to top 10
   ├── Group A: compute cosine similarity between query vector and each candidate vector
   │     └── sort descending, return top 10 spotify_ids
   └── Group B: LightGBM model scores each candidate
         └── features: [energy_delta, valence_delta, danceability_delta,
                        tempo_normalized, acousticness, instrumentalness, loudness_normalized, speechiness]
         └── sort by predicted score descending, return top 10 spotify_ids

7. Database lookup — hydrate top 10 track objects
   └── SELECT * FROM tracks WHERE spotify_id IN (...) — single query

8. explainer.py — generate explanations (single Claude call)
   ├── Build prompt with mood string + all 10 track names, artists, and audio features
   ├── POST to Anthropic API
   ├── Parse response: expect JSON array of 10 explanation strings
   └── On failure: set explanation = null for all 10 tracks, do not fail request

9. experiment.py — log request to DB
   ├── INSERT INTO recommendation_logs (request_type, input_data, experiment_group,
   │     strategy_used, recommendations, created_at)
   └── This write happens AFTER response is assembled — never blocks the response

10. Return response
    └── 200 OK, JSON body with recommendations array, experiment_group, strategy, log_id
```

### Flow B: POST /recommend/track (simplified — skips mood translation)

Steps 3 (mood translation) is replaced with a direct DB lookup of the seed track's audio features. Everything else is identical to Flow A.

---

## 15. Database Schema (Full DDL Reference)

All tables defined via SQLAlchemy ORM in `models.py`. Alembic manages version history.

### tracks
```sql
CREATE TABLE tracks (
    id               SERIAL PRIMARY KEY,
    spotify_id       VARCHAR NOT NULL UNIQUE,
    name             VARCHAR NOT NULL,
    artist           VARCHAR NOT NULL,
    album            VARCHAR,
    energy           FLOAT,
    valence          FLOAT,
    danceability     FLOAT,
    tempo            FLOAT,
    acousticness     FLOAT,
    instrumentalness FLOAT,
    loudness         FLOAT,
    speechiness      FLOAT,
    created_at       TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ix_tracks_spotify_id ON tracks (spotify_id);
```

### recommendation_logs
```sql
CREATE TABLE recommendation_logs (
    id               SERIAL PRIMARY KEY,
    request_type     VARCHAR,          -- "track" or "mood"
    input_data       VARCHAR,          -- raw user input (mood string or spotify_id)
    experiment_group VARCHAR,          -- "A" or "B"
    strategy_used    VARCHAR,          -- "cosine_similarity" or "mood_weighted"
    recommendations  VARCHAR,          -- JSON array of spotify_ids: '["id1","id2",...]'
    created_at       TIMESTAMP DEFAULT NOW()
);
```

### feedback
```sql
CREATE TABLE feedback (
    id               SERIAL PRIMARY KEY,
    log_id           INTEGER NOT NULL REFERENCES recommendation_logs(id),
    spotify_id       VARCHAR NOT NULL,
    rating           INTEGER NOT NULL,  -- 1 = thumbs up, -1 = thumbs down
    created_at       TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ix_feedback_log_id ON feedback (log_id);
```

### api_keys
```sql
CREATE TABLE api_keys (
    id               SERIAL PRIMARY KEY,
    key              VARCHAR NOT NULL UNIQUE,
    experiment_group VARCHAR NOT NULL,  -- "A" or "B", set at key creation
    created_at       TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ix_api_keys_key ON api_keys (key);
```

**Schema notes:**
- `api_keys.key` stores the key hashed with `bcrypt` — never plaintext
- `recommendation_logs.recommendations` stores JSON as a VARCHAR string; parse with `json.loads()` at read time — avoids PostgreSQL JSON column complexity for a portfolio project
- All foreign keys are enforced at the database level, not just the ORM level

---

## 16. Offline Pipeline — Setup Scripts

Two scripts must be run once before the API can serve any requests. Both are idempotent.

### scripts/seed_catalog.py

Purpose: populate the `tracks` table with real Spotify audio features.

```
Algorithm:
1. Authenticate with Spotify Web API using client credentials flow (spotipy)
2. For each genre in seed_genres list (20+ genres covering energy/valence space):
   a. Call search API: query="genre:{genre}", type="track", limit=50
   b. Extract track IDs from results
3. Batch track IDs into groups of 100 (Spotify audio features endpoint limit)
4. For each batch: call audio_features(batch) → list of feature dicts
5. For each track with complete features (no None values):
   a. UPSERT into tracks table using spotify_id as conflict key
6. Exponential backoff on 429 responses from Spotify API
7. Log progress every 100 tracks

Target: 2,000–5,000 tracks covering all corners of the audio feature space
Seed genres: pop, rock, hip-hop, jazz, classical, electronic, r&b, country,
             metal, indie, lo-fi, ambient, soul, funk, punk, reggae,
             blues, folk, disco, latin
```

### scripts/build_index.py

Purpose: build and save the Annoy index from the current tracks table.

```
Algorithm:
1. Query all tracks from DB: SELECT spotify_id, energy, valence, danceability,
   tempo, acousticness, instrumentalness, loudness, speechiness FROM tracks
2. Normalize features:
   - tempo: divide by 200.0 to bring into [0, 1] range
   - loudness: (loudness + 60) / 60.0 to bring into [0, 1] range
   - all other features already in [0, 1]
3. Build in-memory mapping: {annoy_int_id → spotify_id}
4. Initialize AnnoyIndex(f=8, metric='angular')
5. For each track: index.add_item(annoy_id, feature_vector)
6. index.build(n_trees=50)  -- 50 trees: good recall vs memory tradeoff at 5K tracks
7. index.save('models/annoy_index.ann')
8. Save id→spotify_id mapping as 'models/track_id_map.json'
9. Log: total tracks indexed, index file size

Note: must re-run whenever new tracks are added to the DB
```

### scripts/train_ranker_b.py (Strategy B only)

Purpose: train and save the LightGBM ranking model.

```
Algorithm:
1. Define labeled mood-feature training pairs (hand-labeled, ~200 examples):
   - Each example: {mood_label, energy_target, valence_target, ...} with a relevance score
2. For each track in catalog: compute feature deltas vs mood target
   - delta_energy = abs(track.energy - target.energy)
   - delta_valence = abs(track.valence - target.valence)
   - (repeat for all 8 features)
3. Label: tracks with smaller total delta get higher relevance scores
4. Train LGBMRanker or LGBMRegressor on (delta features → relevance score)
5. Evaluate: NDCG@10 on held-out mood queries
6. Save: joblib.dump(model, 'models/ranker_b.pkl')

Note: at MVP, can seed with synthetic training data generated from Claude
(ask Claude to score track-mood pairs) — replace with real feedback data in v2
```

---

## 17. LLM Integration Design

### Mood Translation (mood.py)

**Model:** `claude-sonnet-4-20250514`  
**Call pattern:** one call per `/recommend/mood` request  
**Timeout:** 5 seconds — if exceeded, return neutral fallback

```python
SYSTEM_PROMPT = """You are an audio feature translator for a music recommendation system.
The user will describe a mood or feeling. You will respond with ONLY a JSON object
containing exactly these 8 keys with float values in the specified ranges:
- energy: 0.0 to 1.0 (intensity and activity level)
- valence: 0.0 to 1.0 (musical positivity; 0=dark/sad, 1=happy/euphoric)
- danceability: 0.0 to 1.0 (rhythmic suitability for dancing)
- tempo: 60.0 to 200.0 (beats per minute)
- acousticness: 0.0 to 1.0 (acoustic vs electric/produced)
- instrumentalness: 0.0 to 1.0 (0=vocals present, 1=no vocals)
- loudness: -25.0 to 0.0 (dB; -25=very quiet, 0=very loud)
- speechiness: 0.0 to 1.0 (spoken word content)
Respond with JSON only. No explanation. No preamble."""

USER_PROMPT = f"Mood: {mood_string}"
```

**Fallback values** (returned on any Claude failure):
```python
NEUTRAL_FEATURES = {
    "energy": 0.5, "valence": 0.5, "danceability": 0.5,
    "tempo": 120.0, "acousticness": 0.5, "instrumentalness": 0.0,
    "loudness": -8.0, "speechiness": 0.05
}
```

**Parsing:** `json.loads()` inside `try/except json.JSONDecodeError` — fall back to neutral on any parse failure.

---

### Explanation Generation (explainer.py)

**Model:** `claude-sonnet-4-20250514`  
**Call pattern:** one call per recommendation request (batches all 10 tracks)  
**Timeout:** 8 seconds — on failure, set `explanation: null` for all tracks, do not fail the request

```python
SYSTEM_PROMPT = """You are a music recommendation explainer. You will receive a mood description
and a list of 10 songs. For each song, write exactly one sentence (under 30 words) explaining
why it fits the mood. Respond with ONLY a JSON array of 10 strings, one per song, in the same
order as the input list. No preamble."""

USER_PROMPT = f"""Mood: {mood_string}

Songs:
{chr(10).join(f'{i+1}. "{track.name}" by {track.artist} '
              f'(energy={track.energy:.2f}, valence={track.valence:.2f}, '
              f'tempo={track.tempo:.0f} BPM)'
              for i, track in enumerate(tracks))}"""
```

**Parsing:** expect a JSON array of exactly 10 strings. If `len(parsed) != 10` or parse fails, return `[null] * 10`.

---

## 18. A/B Testing Framework Design

### Assignment Algorithm

```python
import hashlib

def assign_group(api_key: str) -> str:
    hash_int = int(hashlib.md5(api_key.encode()).hexdigest(), 16)
    return "A" if hash_int % 2 == 0 else "B"
```

Properties:
- **Deterministic** — same key always gets same group; no database lookup needed
- **Uniform** — MD5 output is uniformly distributed; expect ~50/50 split at scale
- **Stable** — does not change if the DB is wiped or the server restarts

### Strategy Implementations

**Strategy A — Cosine Similarity (ranker.py)**

```python
# query_vector: np.ndarray shape (8,)
# candidate_vectors: np.ndarray shape (N, 8)
def rank_strategy_a(query_vector: np.ndarray, candidate_vectors: np.ndarray) -> np.ndarray:
    query_norm = query_vector / (np.linalg.norm(query_vector) + 1e-9)
    candidate_norms = candidate_vectors / (np.linalg.norm(candidate_vectors, axis=1, keepdims=True) + 1e-9)
    scores = candidate_norms @ query_norm  # dot product of unit vectors = cosine similarity
    return np.argsort(scores)[::-1]        # descending order indices
```

**Strategy B — LightGBM Mood-Weighted Ranker (ranker.py)**

```python
# model loaded once at app startup from models/ranker_b.pkl
def rank_strategy_b(query_vector: np.ndarray, candidate_vectors: np.ndarray,
                    model: lgb.Booster) -> np.ndarray:
    # feature engineering: delta between candidate and query for each audio feature
    deltas = np.abs(candidate_vectors - query_vector)  # shape (N, 8)
    # additional interaction features
    dot_products = candidate_vectors @ query_vector     # shape (N,)
    features = np.column_stack([deltas, dot_products])  # shape (N, 9)
    scores = model.predict(features)                    # shape (N,)
    return np.argsort(scores)[::-1]
```

### Metrics Calculation (experiment.py)

```python
# All computed in a single SQL query — never load full tables into Python
def get_experiment_results(db: Session) -> dict:
    query = """
        SELECT
            rl.experiment_group,
            COUNT(DISTINCT rl.id)                          AS total_requests,
            COUNT(CASE WHEN f.rating = 1  THEN 1 END)      AS positive_feedback,
            COUNT(CASE WHEN f.rating = -1 THEN 1 END)      AS negative_feedback
        FROM recommendation_logs rl
        LEFT JOIN feedback f ON f.log_id = rl.id
        GROUP BY rl.experiment_group
    """
    # feedback_rate = positive / (positive + negative) — only counts rated requests
    # statistical_significance: True if both groups have 200+ feedback events
    #   and two-proportion z-test p-value < 0.05
```

Statistical significance check uses a two-proportion z-test:
- H0: feedback_rate_A == feedback_rate_B
- Flag as significant if p < 0.05 AND each group has ≥ 200 feedback events
- Use `scipy.stats.proportions_ztest` — add `scipy` to requirements.txt

---

## 19. Docker Architecture

### docker-compose.yml structure

```yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: recsys
    ports: ["5432:5432"]
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  app:
    build: .
    ports: ["8000:8000"]
    depends_on:
      db:
        condition: service_healthy     # wait for Postgres to actually accept connections
    env_file: .env
    volumes:
      - ./models:/app/models           # mount generated index and model files
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:
```

### Dockerfile structure

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# install system deps for psycopg2 and LightGBM
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Key decisions:**
- `python:3.11-slim` not `alpine` — LightGBM's C++ bindings have known issues with Alpine's musl libc
- `gcc` and `libpq-dev` required at build time for psycopg2-binary compilation
- `models/` volume mounted so the Annoy index and LightGBM model persist across container restarts without being baked into the image

---

## 20. CI/CD Pipeline

### GitHub Actions — .github/workflows/ci.yml

```
Trigger: push or pull_request to main branch

Jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env: POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
        ports: ["5432:5432"]
        options: --health-cmd pg_isready --health-interval 5s

    steps:
      1. checkout
      2. setup Python 3.11
      3. pip install -r requirements.txt
      4. set env vars from GitHub Secrets (ANTHROPIC_API_KEY, SPOTIFY_CLIENT_ID, etc.)
      5. run alembic upgrade head  (apply migrations to CI Postgres)
      6. pytest tests/ -v --tb=short --cov=app --cov-report=term-missing
      7. fail if any test fails (exit code non-zero blocks merge)
```

**What the test suite covers (minimum 10 tests):**

| Test file | Tests |
|---|---|
| `test_health.py` | GET /health returns 200 with expected keys |
| `test_recommend.py` | POST /recommend/track happy path; 401 without key; 404 unknown spotify_id; POST /recommend/mood happy path; 422 empty mood string; 422 mood over 500 chars |
| `test_experiment.py` | A/B assignment deterministic (same key → same group); 50/50 split across 1000 random keys; GET /experiments/results returns correct shape |
| `test_feedback.py` | POST /feedback happy path; 404 invalid log_id; 422 invalid rating value |

**Note on Claude API in CI:** mood and explainer tests must mock the Anthropic SDK (`unittest.mock.patch`) — do not make real API calls in CI. This prevents flaky tests from network timeouts and avoids burning API credits on every push.

---

## 21. Render Deployment Architecture

### Services on Render

| Service | Type | Plan | Notes |
|---|---|---|---|
| `spotify-recsys-api` | Web Service | Free | Docker deployment; port 8000; auto-deploy on push to main |
| `spotify-recsys-db` | PostgreSQL | Free (90 days) | Managed Postgres; connection string in env var |
| `spotify-recsys-frontend` | Web Service | Free | Streamlit app; separate repo or sub-directory |

### render.yaml (Infrastructure as Code)

```yaml
services:
  - type: web
    name: spotify-recsys-api
    env: docker
    dockerfilePath: ./Dockerfile
    plan: free
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: spotify-recsys-db
          property: connectionString
      - key: ANTHROPIC_API_KEY
        sync: false     # set manually in Render dashboard — never in yaml
      - key: SPOTIFY_CLIENT_ID
        sync: false
      - key: SPOTIFY_CLIENT_SECRET
        sync: false
      - key: API_KEY
        sync: false

databases:
  - name: spotify-recsys-db
    plan: free
    databaseName: recsys
    user: postgres
```

### Deployment Checklist

```
Before first deploy:
[ ] models/annoy_index.ann built and committed (or Render build step runs build_index.py)
[ ] models/ranker_b.pkl trained and committed
[ ] All secrets set in Render dashboard (never in render.yaml)
[ ] DATABASE_URL uses Render's internal connection string (not localhost)
[ ] Alembic migrations run as part of startup: add to CMD in Dockerfile for Render

Startup command for Render (overrides Dockerfile CMD):
  alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1

After deploy:
[ ] GET /health returns 200 with index_loaded: true
[ ] POST /recommend/mood works end to end with real API key
[ ] Render logs show no startup errors
[ ] Note 90-day PostgreSQL expiry date in README
```

---

## 22. Feature Vector Specification

The 8-dimensional audio feature vector is the fundamental unit of the ML system. This spec defines normalization so that the index build step, the retrieval step, and the ranking step all treat features identically.

| Feature | Raw Range | Normalization | Normalized Range | Notes |
|---|---|---|---|---|
| energy | 0.0–1.0 | none | 0.0–1.0 | already normalized |
| valence | 0.0–1.0 | none | 0.0–1.0 | already normalized |
| danceability | 0.0–1.0 | none | 0.0–1.0 | already normalized |
| acousticness | 0.0–1.0 | none | 0.0–1.0 | already normalized |
| instrumentalness | 0.0–1.0 | none | 0.0–1.0 | already normalized |
| speechiness | 0.0–1.0 | none | 0.0–1.0 | already normalized |
| tempo | 60–200 BPM | divide by 200.0 | 0.3–1.0 | prevents BPM from dominating distance metric |
| loudness | -60 to 0 dB | (loudness + 60) / 60.0 | 0.0–1.0 | maps to [0,1]; louder = higher value |

**Feature vector order is fixed:** `[energy, valence, danceability, tempo_norm, acousticness, instrumentalness, loudness_norm, speechiness]`

This order must be identical in:
- `scripts/build_index.py` (when adding items to Annoy)
- `app/recommender.py` (when building query vector)
- `app/ranker.py` (when computing cosine similarity or LightGBM features)

---

## 23. Error Handling Contract

All API errors return this shape — no exceptions:
```json
{"error": "human-readable message", "code": 422}
```

| Scenario | HTTP Status | Error message |
|---|---|---|
| Missing X-API-Key header | 401 | "Invalid or missing API key" |
| Invalid X-API-Key value | 401 | "Invalid or missing API key" |
| Rate limit exceeded | 429 | "Rate limit exceeded. Try again in 60 seconds." |
| Malformed request body | 422 | Pydantic's default field-level error message |
| Empty mood string | 422 | "Mood string cannot be empty" |
| Mood string over 500 chars | 422 | "Mood string exceeds 500 character limit" |
| spotify_id not in catalog | 404 | "Track not found in catalog" |
| log_id does not exist | 404 | "Recommendation log not found" |
| Invalid feedback rating | 422 | "Rating must be 1 (positive) or -1 (negative)" |
| Database unreachable | 503 | "Database unavailable. Try again later." |
| Unhandled exception (catch-all) | 500 | "An unexpected error occurred" |

The catch-all 500 handler must be registered in `main.py` using FastAPI's `@app.exception_handler(Exception)` — this ensures raw Python exceptions never reach the user as unformatted 500s.