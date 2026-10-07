# Project Spec: Moodify

**Author:** Nathan Nguyen  
**Type:** Personal portfolio project  
**Primary audience:** Data Science, Data Analyst, and Machine Learning internship recruiters and hiring managers.  
**Definition of done:** A DS/ML portfolio project demonstrating production ML engineering maturity — real experiment tracking, a RAG-based retrieval component, and a real deep-learning component — built on top of the existing A/B-tested recommendation pipeline, demoable via the existing (frozen) React frontend.  
**Most important quality:** Nathan's own understanding of every architectural decision. Working code that Nathan can't explain does not count as done.  
**Claude's role on this project:** Teach the underlying DS/ML/MLOps fundamentals while building — explain the *why* behind experiment-tracking, RAG/vector-search, and embedding-model patterns, not just produce working code. Nathan dislikes "vibe coding" parts he doesn't understand.

---

## 0. Project Pivot — Read This First

**This project has pivoted twice. This section describes the current (second) pivot, which supersedes the first.**

**Pivot 1 (historical):** the ML/recommendation core (retrieval + ranking pipeline, mood translation, A/B bucketing, Streamlit dashboard) was declared functionally done, and the project turned toward becoming a SWE portfolio piece — a React frontend, JWT auth, testing/CI-CD, and a system design write-up, on the reasoning that Nathan's actual strengths pointed toward SWE roles over ML/DS. That work is documented in **Part 3 (Sections 24–28)** below. Of that work, only the **React frontend was actually built** (Section 24) — auth, testing/CI-CD, and the system design write-up were never implemented.

**Pivot 2 (current):** Nathan's actual recruiting goal is Data Science, Data Analyst, and Machine Learning internships for Summer 2027 — most of his existing skills already sit in this track. A gap analysis against current DS/ML/MLE internship postings surfaced specific, concrete gaps: no MLOps/experiment-tracking tooling, no RAG/vector-database work, no applied deep learning project despite PyTorch being listed as a skill. **The project is now oriented back toward DS/ML**, closing those gaps on top of the existing ML core, in this order:

1. **MLOps / experiment tracking** — instrument the existing A/B pipeline with MLflow or Weights & Biases.
2. **RAG / vector database** — replace or supplement Annoy with a proper vector database (Pinecone or FAISS); restructure Claude mood-translation as an actual RAG pipeline.
3. **A defensible deep learning component** — a learned embedding model (PyTorch) replacing the hand-engineered audio features.
4. **(Stretch) Airflow** — orchestrate the data ingestion/feature pipeline.

Detailed requirements for each are in **Part 4 (Sections 29–32)** at the end of this document.

**What this means for the rest of this document:** Sections 1–23 (the ML core) remain accurate as a technical reference. **Part 3 (Sections 24–28) is now historical** — read Section 24 (React frontend) as an accurate record of what was built and is being kept; read Sections 25–28 (auth, testing/CI-CD, system design write-up, real-time stretch) as abandoned plans, not work in progress. Anywhere the rest of this document frames the audience, success metrics, or "not in scope" list around SWE recruiting, **Part 4 and this section take precedence.**

---

## 1. Product Definition

### What is this?

A production-grade music recommendation API that accepts either a seed track or a natural language mood description and returns 10 personalized song recommendations — each with a plain English explanation of why it fits.

The system runs a live A/B experiment comparing two ranking strategies, logs every request, collects user feedback, and exposes real-time experiment metrics. Everything is containerized, tested, and deployed.

### What problem does it solve?

**For users:** Existing music discovery tools require you to already know what you want. You can't tell Spotify "I want something for a late night drive feeling nostalgic" and get back music that actually fits that feeling. This system bridges natural language and audio features using an LLM.

**For Nathan's career:** Demonstrates production ML engineering skills to DS/ML/Data Analyst internship hiring managers — specifically real experiment tracking, a RAG/vector-search component, an applied deep learning component, and the ability to reason about and defend the existing A/B-tested recommendation pipeline. The React frontend (built during an earlier SWE-focused pivot, see Section 0) is a demo layer, not the pitch itself.

### Who is it for?

| User | What they do with it |
|---|---|
| DS/ML/Data Analyst internship recruiters | View the live demo, read the README, assess ML engineering maturity — experimentation rigor, not just a working model |
| DS/ML hiring managers | Evaluate experiment tracking, retrieval/RAG design, applied deep learning work, and whether Nathan can explain his own architecture |
| Nathan (builder) | Close specific DS/ML skill gaps — MLOps tracking, RAG/vector DB, deep learning, orchestration — by building them, not by having them built for him |
| General users | Type a mood, get song recommendations, rate them |

### Jobs to be done

- **As a user**, I want to describe how I'm feeling in plain English and get songs that match that feeling, so I don't have to know the technical name for what I want.
- **As a user**, I want to understand why each song was recommended, so I can trust the system.
- **As a user**, I want to rate recommendations so the system can learn what works.
- **As a recruiter**, I want to see a live demo and a clean README so I can evaluate the project's ML engineering maturity in under 5 minutes.
- **As a hiring manager**, I want to see real experiment tracking, a retrieval design I can ask about, and evidence of applied deep learning, not just a listed skill.

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
1. User types their favorite song's name; the frontend calls GET /search/tracks and shows matching tracks in a dropdown to pick from
2. User selects a track, and the system sends its Spotify track ID with the API key
3. System looks up track's audio features from database
4. System searches Annoy index for similar tracks
5. Same ranking and logging pipeline as Flow 1
6. Response returned: 10 similar tracks with explanations

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

| Feature | Status | Requirement |
|---|---|---|
| Seed track recommendation | ✅ Done | POST /recommend/track accepts a Spotify track ID and returns 10 similar tracks |
| Mood recommendation | ✅ Done | POST /recommend/mood accepts a natural language string and returns 10 tracks via Claude translation |
| Health check | ✅ Done | GET /health returns {"status": "ok"} with no auth required |
| API key auth | ✅ Done | All write endpoints reject requests missing a valid X-API-Key header with 401 |
| Docker | ✅ Done | Entire app (API + PostgreSQL) starts with a single `docker compose up` command |
| Database | ✅ Done | tracks and recommendation_logs tables exist and are populated before any request can succeed |

### v1 — core product functionality

| Feature | Status | Requirement |
|---|---|---|
| Explainability | ✅ Done | Every recommendation includes a one-sentence Claude-generated explanation of why it fits |
| Rate limiting | ✅ Done | Max 10 requests per minute per IP; exceeding returns 429 with a clear error message |
| Request logging | ✅ Done | Every request writes to recommendation_logs with group, strategy, input, and output |
| Input validation | ✅ Done | All endpoints return 422 with a meaningful message on malformed input, never 500 |
| Error handling | ✅ Done | 400 for bad requests, 401 for missing auth, 404 for not found, 422 for validation, 429 for rate limit |
| Strategy A ranker | ✅ Done | Cosine similarity baseline ranker operational |

### v2 — experiment infrastructure (backlog — not currently prioritized)

The ML/recommendation core is considered functionally done. These items are technically incomplete but are **not being actively pursued** — see Section 0. They're left here as an accurate backlog, not a plan.

| Feature | Status | Requirement |
|---|---|---|
| A/B assignment | ⬜ Not started | API key hashed to deterministically assign Group A or B — same key always same group |
| Strategy B ranker | ⬜ Not started | Mood-weighted LightGBM ranking model trained and operational |
| Feedback endpoint | ⬜ Not started | POST /feedback accepts log ID, track ID, and rating; stores in feedback table |
| Experiment results | ⬜ Not started | GET /experiments/results returns per-strategy metrics and statistical significance flag |
| Cold start handling | ⬜ Not started | System returns valid recommendations even when user has no prior request history |

**Test suite and CI pipeline are no longer "ML v2" items — they've moved to Part 3 (Section 26) as a top-level SWE priority**, scoped to the whole app (backend + frontend + auth), not just the recommendation endpoints.

### Later — polish and deployment

**Note:** the Streamlit frontend below is being superseded, not extended. It stays live as the metrics/demo dashboard, but the product's real UI going forward is the React frontend in Part 3 (Section 24) — see Section 0.

| Feature | Status | Requirement |
|---|---|---|
| Streamlit frontend | ✅ Done (superseded as primary UI) | Single-page demo (Moodify) with mood/track toggle, song cards with similarity bars and Claude explanations, hover-reveal Spotify links. Track mode uses a song-name search box → dropdown of matches → Find Music, backed by GET /search/tracks. Runs with `streamlit run frontend/app.py`. Kept as an internal metrics dashboard going forward, not the product-facing UI. |
| Track search / autocomplete | ✅ Done | GET /search/tracks matches a song name against track name or artist (ILIKE, popularity-ordered, top 10) so users pick their favorite song by name instead of pasting a Spotify ID |
| Render deployment | 🟡 In progress | Repo prepped: render.yaml (API + Postgres), Dockerfile honors $PORT, database.py handles Render's postgres:// scheme, models/ artifacts committed, frontend reads API_BASE/API_KEY from secrets. Remaining: provision on Render, seed prod DB, set secrets, deploy frontend to Streamlit Cloud. See Section 21 runbook. |
| Catalog stats | ⬜ Not started | GET /catalog/stats returns total track count and audio feature distributions |
| Mood history | ⬜ Not started | Track mood inputs per API key over time; surface patterns back to user |

### Not in scope

| Feature | Reason |
|---|---|
| Spotify user OAuth | Different from the app's own user auth (Section 25) — adds Spotify-side complexity with no SWE-signal benefit over building auth ourselves |
| Mobile app | React web frontend is sufficient for demo purposes |
| Real-time model retraining | Models trained offline; online learning is out of scope — the "real-time" stretch goal (Section 28) is about concurrency/systems engineering, not ML |
| Payments or subscriptions | Not relevant to portfolio goals |
| Multi-tenancy | Single-tenant system is sufficient |
| Further ranking model work (Strategy B tuning, deeper A/B statistical infra) | Not scheduled ahead of the Part 4 DS/ML roadmap (MLOps tracking, RAG/vector DB, deep learning, Airflow) — may be revisited after |

Note: streaming responses are no longer categorically out of scope — see the real-time stretch goal in Section 28.

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

#### GET /search/tracks
No auth required. Rate limited to 30 requests per minute per IP.  
Query params: `q` (required, 1–100 chars) — partial song name or artist.  
Matches `q` against track name or artist (case-insensitive), ordered by popularity, capped at 10.  
Response 200:
```json
{
  "results": [
    {
      "spotify_id": "4u7EnebtmKWzUH433cf5Qv",
      "name": "Bohemian Rhapsody - Remastered 2011",
      "artist": "Queen",
      "album": "A Night At The Opera (2011 Remaster)"
    }
  ]
}
```
Error 422 if `q` is empty or over 100 characters.

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
{"mood_string": "late night drive feeling nostalgic", "limit": 10}
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

This is a portfolio project for DS/ML/Data Analyst internship recruiting (see Section 0), so success is defined by career outcomes and interview-defensibility, not raw model performance alone.

| Metric | Target |
|---|---|
| Recruiter response rate | At least 1 DS/ML/Data Analyst internship interview request directly attributable to this project |
| Architecture defensibility | Nathan can confidently explain any decision — retrieval design, experiment tracking, the embedding model — in a technical interview, not just that it works |
| Time to explain in interview | Can walk through the full ML architecture, including the RAG and deep learning components, in under 10 minutes |
| Demo reliability | Zero crashes during a live demo |
| Code review readiness | Any DS/ML hiring manager can read any file and understand it without asking questions |
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
| Ranking model — B | LightGBM | 4.3.x | **NOT built / not in requirements.txt — ML v2 backlog.** Intended choice: replaces sklearn GBR; 10-50x faster training; used in production ranking at Meta/TikTok/Google; sklearn-compatible API means near-zero migration cost |
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
| Frontend (legacy dashboard) | Streamlit | 1.35.x | Python-only; kept as an internal metrics/demo dashboard, no longer the product-facing UI |
| Frontend (product UI) | React | 18.x | Real component-based UI, built during the earlier SWE-focused pivot (Section 0); complete and frozen, kept as the demo layer |
| Frontend tooling | Vite | 5.x | Fast dev server and build |
| Frontend HTTP client | fetch | — | Talks to the FastAPI backend |
| Experiment tracking | MLflow or Weights & Biases | — | **Not built — Part 4 Priority 1.** Instruments the existing A/B pipeline with run tracking, model versioning, and metrics |
| Vector search / RAG | Pinecone or FAISS | — | **Not built — Part 4 Priority 2.** Replaces/augments Annoy; restructures mood translation as an actual RAG pipeline |
| Deep learning | PyTorch | — | **Not built — Part 4 Priority 3.** Learned embedding model replacing the hand-engineered audio features |
| Orchestration | Airflow | — | **Not built — Part 4 stretch.** Orchestrates the data ingestion/feature pipeline |
| Deployment | Render | — | Docker-native; free web service + PostgreSQL (90-day free then $7/mo); recruiter-friendly live URL |

**Dropped (see Section 0):** JWT auth (PyJWT + passlib/bcrypt), GitHub Actions CI/CD. These were part of the abandoned SWE-focused pivot and were never implemented — no code depends on them.

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
  ├── ranker.py      ← Strategy A (cosine similarity). Strategy B (LightGBM) NOT built.
  │     └── uses: numpy (A). ranker_b.pkl does not exist yet.
  │
  ├── experiment.py  ← [PLANNED, NOT YET CREATED] deterministic A/B assignment + metrics.
  │     └── Today: no such module. Group is hardcoded to "A" inline in main.py;
  │         no metrics aggregation exists. This is the intended target design.
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

  (also present: app/utils.py — currently an empty placeholder with no use.)
```

> **Status note:** this diagram is the target component layout. As of now `experiment.py`
> does not exist (A/B assignment is inlined and hardcoded to `"A"` in `main.py`), and
> `ranker.py` implements Strategy A only. See Section 3 and Section 0 for why these are
> intentional backlog items rather than active work.

---

## 14. Data Flow — Request Lifecycle

> **Status note:** this is the intended lifecycle. Steps attributed to `experiment.py`
> (group assignment, step 5) are not yet implemented as written — there is no `experiment.py`,
> the group is hardcoded to `"A"` in `main.py`, and only Strategy A runs. Request logging
> (step 9) *is* implemented, but inline in `main.py` rather than in a separate module.

### Flow A: POST /recommend/mood (primary flow, full detail)

```
1. HTTP POST arrives at Uvicorn
   └── Headers: X-API-Key, Content-Type: application/json
   └── Body: {"mood_string": "late night drive feeling nostalgic", "limit": 10}

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

**Status: Complete. Verified against 89,740 tracks.**

```
Algorithm:
1. load_tracks(): query all tracks from DB, return parallel lists —
   spotify_ids: list[str] and feature_rows: list[list[float]]
   Feature order (9 features): energy, valence, danceability, tempo,
   acousticness, instrumentalness, loudness, speechiness, popularity

2. normalize_features(): fit sklearn MinMaxScaler on full (n_tracks, 9) matrix
   - Scales every feature to [0, 1] using global min/max across catalog
   - Saves fitted scaler to models/scaler.pkl via joblib.dump()
   - IMPORTANT: same scaler must be applied to query vectors at request time

3. build_index(): build Annoy index from normalized matrix
   - Initialize AnnoyIndex(f=9, metric='angular')
     ('angular' distance == cosine similarity)
   - For each row i: index.add_item(i, normalized_vector)
   - index.build(n_trees=50) — 50 trees balances recall vs memory at this scale
   - index.save('models/annoy_index.ann')
   - Save spotify_ids list as 'models/track_id_map.json'
     (list index == Annoy position, enables O(1) lookup: track_ids[i])

Output files (in models/):
  annoy_index.ann     — 60MB, the Annoy index
  track_id_map.json   — 2.2MB, ordered list of spotify_ids by Annoy position
  scaler.pkl          — 1KB, fitted MinMaxScaler

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
    environment:
      DATABASE_URL: postgresql://postgres:password@db:5432/recsys   # overrides .env's @localhost inside Docker's network
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

### Services

| Service | Platform | Plan | Notes |
|---|---|---|---|
| `spotify-recsys-api` | Render Web Service | Free | Docker deployment; binds Render's `$PORT`; provisioned via `render.yaml` Blueprint |
| `spotify-recsys-db` | Render PostgreSQL | Free (90 days) | Managed Postgres; `DATABASE_URL` auto-wired into the API service |
| Streamlit frontend | Streamlit Community Cloud | Free | Deployed from `frontend/app.py`; `API_BASE` + `API_KEY` set in the app's Secrets UI |

### render.yaml (Infrastructure as Code)

The committed `render.yaml` provisions the API + Postgres. Only secrets the API needs **at runtime** are `DATABASE_URL` (auto) and `ANTHROPIC_API_KEY` (manual). Spotify credentials are NOT needed at runtime — they're only used by `scripts/seed_catalog.py`, which is run locally during seeding.

```yaml
services:
  - type: web
    name: spotify-recsys-api
    runtime: docker
    dockerfilePath: ./Dockerfile
    plan: free
    healthCheckPath: /health
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: spotify-recsys-db
          property: connectionString
      - key: ANTHROPIC_API_KEY
        sync: false     # set manually in Render dashboard — never in yaml

databases:
  - name: spotify-recsys-db
    plan: free
    databaseName: recsys
    user: postgres
```

### Deployment Runbook

**Prerequisites baked into the repo:**
- `models/` artifacts (annoy_index.ann, scaler.pkl, track_id_map.json) are committed so the API can load them at startup. `app/recommender.py` loads them at import time — without them the service crashes on boot.
- `app/database.py` normalizes Render's `postgres://` scheme to `postgresql://` for SQLAlchemy 2.0.
- The Dockerfile CMD honors `$PORT`; the FastAPI lifespan runs `Base.metadata.create_all`, so table schema is created on first boot (no separate migration step required on Render).

**Steps:**
```
1. Push to GitHub. Render dashboard → New → Blueprint → connect repo.
   Render reads render.yaml and provisions the API + Postgres.

2. Wait for the database to finish, then copy its EXTERNAL connection string.

3. Seed the prod DB from your local machine (catalog is not in the repo):
     export DATABASE_URL="<render external connection string>"
     alembic upgrade head             # create schema (or rely on lifespan create_all)
     python scripts/seed_catalog.py   # load ~90k tracks from the local Kaggle CSV
     python scripts/create_api_key.py # COPY the printed key — the frontend needs it

4. In the Render web service → Environment, set ANTHROPIC_API_KEY. Redeploy.

5. Deploy the frontend on Streamlit Community Cloud (point at frontend/app.py).
   In the app's Secrets, set:
     API_BASE = "https://<your-service>.onrender.com"
     API_KEY  = "<key from step 3>"
```

**After deploy — verify:**
```
[ ] GET /health returns {"status": "ok", "db": "connected"}
[ ] POST /recommend/mood and /recommend/track work end to end with the real API key
[ ] Track search autocomplete returns results in the Streamlit UI
[ ] Render logs show no startup errors (esp. no missing models/ files)
```

**Free-tier caveats (document in README):**
- The API spins down after ~15 min idle → first request cold-starts (~50s). Hit `/health` to warm it before a live demo.
- **Render free PostgreSQL expires 90 days after creation.** Record the creation date and expiry date in the README; re-provision or upgrade before it lapses or the live demo will break.

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

---

---

# Part 3: SWE Product Roadmap (Historical — Superseded, See Section 0)

**This part is no longer current.** It documents the first pivot, toward SWE internship recruiting. Of the five items below, only **Section 24 (React frontend) was actually built** — it's kept as the demo layer for the current DS/ML-focused project. **Sections 25–28 (auth, testing/CI-CD, system design write-up, real-time stretch) were never implemented and are not planned** — left here as a record of what was considered at the time, not a roadmap. The current roadmap is **Part 4 (Sections 29–32)**.

---

## 24. React Frontend Architecture

**Priority 1.** The product currently has an API and a Streamlit dashboard — not a real frontend. This is the single highest-leverage gap: "I built a data app in Streamlit" and "I built a React frontend against my own REST API" test completely different skills to a SWE interviewer.

> **Status note (current):** `frontend-react/` is built, wired, and styled (Vite + React + TypeScript, CSS Modules). Components: `Heading`, `ModeToggle`, `SearchForm`, `SongCard`, `ResultsList`, composed in `App`.
>
> **Data flow.** `mode` is lifted to `App` and passed down; `SearchForm` owns a controlled `query` input; `App`'s `handleSearch` calls the real `/recommend/mood` / `/recommend/track` endpoints and holds `songs`, `strategy`, `hasSearched`, `isLoading`, and `error`. Track mode adds a debounced `useEffect` (300ms, cleaned up via `clearTimeout`) against `GET /search/tracks`, rendering an autocomplete dropdown; selecting a match stores the displayed text and the real `spotify_id` as two separate pieces of state, and `handleSubmit` validates that a track was actually chosen before submitting. Dropdown visibility is *derived at render time* rather than set from inside the effect — the effect's only job is fetching, which avoids a cascading re-render (`react-hooks/set-state-in-effect`) and stops the dropdown reopening after a selection. This required adding `CORSMiddleware` to `app/main.py` (the browser's `OPTIONS` preflight was getting a 405 without it).
>
> **Design.** The Streamlit visual identity was kept and rebuilt properly: a sage-green "sleeve stock" page ground with dark ink panels printed on top, Spotify green as the single accent reserved for signal. Type is Fraunces (variable display serif) / Karla / JetBrains Mono, loaded with `preconnect` + `<link>` in `index.html`. All colour, type, radius, and easing values are CSS custom properties on `:root` in `index.css`; no component hardcodes a colour. Results render as a numbered tracklist with a similarity meter and the Claude explanation as an italic liner note, with album + Spotify link revealed on hover via `grid-template-rows: 0fr → 1fr`. Loading is a shimmer skeleton matching the real row rhythm; there are distinct empty states for "before any search" and "search returned nothing". Motion is CSS-only — the staggered row entrance takes each index in as a `--i` custom property — animates `transform`/`opacity` only, and is fully disabled under `prefers-reduced-motion`. `npm run build` and `npm run lint` both pass clean.
>
> **Not yet done:** routing (`react-router`), and the login / history pages and auth-aware nav — all blocked on Section 25 landing first. The styling has not yet been reviewed in a browser by Nathan.
>
> The current API-key auth is being called from the browser via a `VITE_API_KEY` env var, dev-only and gitignored — a known, explicitly temporary violation of "never expose API keys client-side" (Section 4 Security requirements), resolved once Section 25 (JWT auth) gives the frontend a per-user session token instead of a static shared key.

### Why React + Vite, not Next.js
Next.js adds SSR, file-based routing, and server components — real skills, but a different layer than what's being tested for an intern-level SWE role. Plain React + Vite keeps the focus on component architecture, hooks, and client/server data flow. Next.js is a reasonable follow-up later, not a requirement now.

### Why built-in state (useState/useContext), not Redux
The app's state surface is small: current query, recommendation results, auth session, saved history. Redux here would be over-engineering. Knowing *when not* to reach for a state library is itself an interview-relevant signal.

### Why plain fetch, not React Query (initially)
Understand the manual loading/error/success state machine by hand before reaching for a library that hides it. Revisiting with React Query later, once the manual pattern is understood, is a reasonable stretch — it's also a common interview topic in its own right.

### Routing
`react-router` — needed once there's a login page, a results page, and a history page.

### Pages / components
- ~~Mood/track search (rebuild of the current Streamlit flow: SearchBar, SongCard list, ExplanationText)~~ — **done**: `Heading`, `ModeToggle`, `SearchForm` (with autocomplete), `ResultsList`, `SongCard`
- ~~Recommendation results (song title/artist, similarity score, Claude explanation)~~ — **done**; feedback buttons still pending `POST /feedback`, which is in the ML v2 backlog
- Login / sign up — pending Section 25
- History page — past recommendations tied to the logged-in user — pending Section 25
- Nav bar reflecting auth state — pending Section 25

### Styling approach (and why)
CSS Modules, one file per component, over a utility framework (Tailwind) or a CSS-in-JS library. Modules give real style scoping with zero runtime and zero build config beyond what Vite already does, and they keep the CSS readable as CSS — which matters for a project whose point is being able to explain its own decisions. The design system is a set of custom properties on `:root`, so re-theming is a one-file change. Tailwind is a defensible alternative and a common one in industry; the tradeoff to be able to name is that it moves styling into the markup and trades readable stylesheets for faster iteration.

**Definition of done:** React frontend fully replaces Streamlit as the product-facing entry point, deployed and calling the existing FastAPI endpoints plus the new auth endpoints. Nathan can explain the component structure, state flow, and at least one rendering/performance decision without notes.

**Progress against that:** the search + results experience is complete and styled; deployment and the auth-dependent pages remain. Decisions worth being able to defend cold: lifting `mode` to `App` vs. keeping it local; why the mood submit is *not* a `useEffect` but the autocomplete is; why dropdown visibility is derived rather than stored; why the row stagger is `--i` + CSS rather than a JS animation loop; why the meter animates `transform: scaleX()` instead of `width`.

---

## 25. Authentication & User Accounts

> **Status: abandoned, never implemented — see Section 0.** Kept below as a record of the design that was discussed, not a plan.

**Priority 2.** Current auth is a single shared `X-API-Key` per API consumer — it identifies a *client*, not a *user*. There's no login, no session, no per-user history. Real user auth is a baseline expectation for any consumer product pitch.

### Why JWT, not server-side sessions
No additional infrastructure (e.g. Redis) is justified at this scale, and JWTs are the more commonly-asked-about pattern for a stateless API in interviews. Known tradeoff to be able to name: JWTs can't be revoked before expiry without an extra revocation list — acceptable here, and worth stating as a limitation in the system design write-up (Section 27).

### Token design
Access token (short-lived, e.g. 15 min) + refresh token (longer-lived, e.g. 7 days). Refresh token stored in an httpOnly cookie rather than localStorage, to reduce XSS exposure. Be able to explain why one token isn't enough, and why httpOnly cookie over localStorage.

### Password storage
Hashed with bcrypt via `passlib`. Never store or log plaintext passwords.

### Schema changes
- New `users` table: `id`, `email` (unique), `hashed_password`, `created_at`.
- `recommendation_logs` and `feedback` gain a nullable `user_id` foreign key — nullable so the existing anonymous/API-key-only flow keeps working; logged-in requests attach the real user.

### New endpoints
`POST /auth/signup`, `POST /auth/login`, `POST /auth/refresh`, `GET /auth/me`, `GET /users/me/history`.

### Why the existing `X-API-Key` auth isn't being replaced
The API key models *which client/experiment group*; the JWT models *which human is logged in*. These answer different questions and are deliberately not merged — be able to explain that distinction rather than presenting it as leftover complexity.

**Definition of done:** a user can sign up, log in, get recommendations while authenticated, view their own history, and log out. Nathan can explain the JWT/refresh-token flow, the hashing choice, and the httpOnly-cookie tradeoff without notes.

---

## 26. Testing & CI/CD

> **Status: abandoned, never implemented — see Section 0.**

**Priority 3.** A "production-grade" pitch with zero automated tests and no CI is not credible in a SWE interview. This closes that gap for the whole app — frontend and auth included, not just the recommendation endpoints.

### Backend testing
- **Unit tests:** schema validation, JWT encode/decode helpers, password hashing, the MD5-based A/B assignment function, `ranker_a` cosine similarity math.
- **Integration tests** (httpx + FastAPI `TestClient`): full request/response cycles for `/auth/*`, `/recommend/track`, `/recommend/mood` — happy path plus at least one failure case per endpoint (matches the existing Definition of Done in Section 8). Anthropic and Spotify calls mocked — no real API calls in CI.

### Frontend testing (stretch within this milestone, not blocking)
A handful of component tests with Vitest + React Testing Library for the highest-value components (SearchBar, SongCard) — enough to demonstrate frontend testing literacy, not full coverage.

### CI
`.github/workflows/ci.yml` runs pytest on every push and PR to `main`, with a Postgres service container (as already scoped in Section 20), and fails the build on any test failure.

### CD
On merge to `main`, after CI passes, auto-deploy to Render. Render supports auto-deploy on push natively once connected to the GitHub repo — the "CD" work here is mostly configuration (enable auto-deploy, gate it with branch protection + required status checks), not custom deploy scripting. Important distinction to understand: a required status check is what actually *blocks* a bad merge — the Render config alone does not.

**Definition of done:** `pytest tests/ -v` passes locally and in CI; GitHub Actions runs on every push; `main` is protected so failing CI blocks merge; merging to `main` triggers a live deploy with no manual steps.

---

## 27. System Design Write-Up

> **Status: abandoned, never implemented — see Section 0.**

**Priority 4.** This is the artifact most likely to get read in an interview loop or take-home review before any code does — proof Nathan can reason about tradeoffs, not just implement a spec someone else wrote.

### Required content (`docs/SYSTEM_DESIGN.md`)
- A one-paragraph system summary and request-flow diagram — the polished, interview-facing version of Section 14.
- Explicit tradeoff statements, each in the form "we chose X over Y because Z, and the cost of that choice is W," covering at minimum: FastAPI vs Flask, Annoy vs FAISS, PostgreSQL vs SQLite, JWT vs server-side sessions, React+Vite vs Next.js, and synchronous request/response vs the real-time stretch feature (Section 28).
- A scaling discussion: what breaks first at 100x traffic (the Annoy index is read-only and memory-mapped, so it scales fine; the Postgres and Render free tiers would not) and what the next step would be.
- A "what I'd do differently" section naming at least 2–3 real limitations (JWT revocation, no Strategy B in production, single-region deployment) — naming real limitations is itself a strong interview signal.

**Definition of done:** a single polished document Nathan can hand to an interviewer or read from live, written in his own words after Claude explains each tradeoff — consistent with the "Claude teaches, Nathan writes the core reasoning" pattern in Section 7.

---

## 28. Stretch — Real-Time / Concurrent Feature

> **Status: abandoned, never implemented — see Section 0.**

**Priority 5, sequenced after Sections 24–27, not in parallel.** Nothing in the current system is concurrent or real-time — every request is a synchronous request/response cycle. Systems/concurrency is a distinct signal from "I can build CRUD endpoints," and it's a common probe at consumer/social-product startups.

Pick one, don't build all:

- **Streamed recommendation explanations** — stream each of the 10 Claude explanations back to the client as it's generated (SSE or WebSocket) instead of waiting for the full batch. Directly revisits the existing "batch all 10 in one call" decision in `explainer.py` (Section 17) and produces a concrete streaming-vs-batching tradeoff story.
- **Live experiment metrics** — push updated A/B metrics to the dashboard via WebSocket as feedback arrives, instead of polling `/experiments/results`.
- **Concurrency under load (lower-scope option)** — load-test the API (`locust` or `hey`), then tune and document concurrency behavior (Uvicorn workers, async DB session handling), producing real numbers for the Section 27 scaling discussion instead of speculation.

---

---

# Part 4: DS/ML Roadmap (Current Priority — See Section 0)

**This is what's actually being worked on now.** Sections 1–23 describe the ML/recommendation core, which is done and stays as the foundation. Part 3 (Sections 24–28) is historical. This part describes the four things (three plus one stretch) that close the specific DS/ML skill gaps identified from current internship postings — see Section 0 for why.

---

## 29. MLOps / Experiment Tracking

**Priority 1.** The project already runs a real experiment (Strategy A vs. Strategy B, MD5 bucketing, `recommendation_logs` + `feedback`) — but nothing about it is tracked the way an ML team would track it. There's no run history, no model versioning, no metrics dashboard beyond the ad-hoc `/experiments/results` design. This is the fastest, lowest-lift gap to close because the experimentation infrastructure already exists; this just formalizes it.

### Why MLflow or Weights & Biases, not a hand-rolled logging table
`recommendation_logs` already logs *requests*. What it doesn't do is track *runs* — a distinct concept: each time the ranking logic, the feature set, or the mood-translation prompt changes, that's a new run worth comparing against prior ones on the same metrics. Hand-rolling this (more columns on `recommendation_logs`) reinvents a wheel that recruiters specifically look for by name. MLflow is self-hostable and free (no vendor lock-in for a portfolio project); Weights & Biases has a nicer hosted dashboard UI that's easier to screenshot for a resume/README. Either is defensible — pick one and be able to say why.

### What gets tracked
- **Runs:** one per meaningfully different configuration (e.g. "Strategy A baseline," "Strategy A + popularity reweighted," any future Strategy B attempt).
- **Parameters logged per run:** ranking strategy used, feature set/weights, Annoy `n_trees`, candidate pool size (currently 500).
- **Metrics logged per run:** feedback rate (from the existing `feedback` table), request latency, and whatever the A/B significance check (Section 18) produces.
- **Artifacts:** the actual model/scaler files (`models/scaler.pkl`, `models/annoy_index.ann`) versioned per run, so "which index was live when this feedback came in" is answerable later.

### Decisions made so far (implementation status)
- **Tool: MLflow** (open source, self-hosted, generalist-DS association). W&B is hosted with a more polished UI but a more ML-research flavor. Pinned `mlflow==3.16.1` — 2.19.0 requires `pandas<3`, conflicting with `pandas==3.0.2`; the core API (`start_run`, `log_param`, `log_metric`, `log_artifact`) is the same in 2.x and 3.x.
- **Run definition:** a run is one distinct pipeline configuration, not a request. Real knobs: Annoy `n_trees` (50, build-time), features included in the 9-feature vector, popularity target (75, hardcoded in the mood flow), candidate pool size (`n=500`, query-time). No config object exists yet; consolidating these is a prerequisite for clean `log_param`.
- **Fixed eval set** (`scripts/eval_queries.py`): 6 `MoodQuery` + 6 `TrackQuery` frozen dataclasses, chosen for coverage of the valence/energy quadrants plus speechiness and instrumentalness/acousticness. The exact set is logged as an artifact per run for reproducibility.
- **Metrics** (`scripts/evaluate_pipeline.py`, built and running): average top-10 cosine similarity, latency (`time.perf_counter()` around `get_candidates` + `ranker_a` only — excludes the Claude call and seed lookup), average popularity of the top 10 — each for mood and track queries, returned as a frozen `EvalMetrics`. Caveats: similarity saturates near 1.0 and is not comparable across feature-set changes; latency is noisy; average popularity is the hypothesis-matched metric for the planned popularity change. Track mode uses the seed's own popularity in its query vector while mood mode hardcodes 75 (a known confound).
- **MLflow wiring (done):** in `evaluate_pipeline.py` `__main__`; one run per configuration, mood and track evaluations in the same run with `mood_`/`track_` metric prefixes (a run is a pipeline configuration, not a query type — separate runs would force manual pairing when comparing configurations). Params: `n_trees`, `popularity_target` (`"N/A"` for ranker B), `candidate_pool_size`, `index_hash`, `ranker` (stable label — never a `partial` repr, which embeds a memory address), `popularity_weight`. Artifacts: `scaler.pkl` and `eval_queries.py` every run; `annoy_index.ann` only when its SHA-256 hash hasn't been stored by an earlier run (`mlflow.search_runs` on `params.index_hash`, searched *before* `start_run` so a run can't match itself; `models/` is also in git, a second source of truth). Backend: MLflow 3.x default SQLite `mlflow.db` + `mlruns/` artifacts, both gitignored; run `mlflow ui` and the script from the project root. UI delete is a soft delete that keeps the experiment name reserved; purge with `mlflow gc` (needs both `--backend-store-uri` and `--tracking-uri`). Commit before each run — MLflow records params, not code.
- **Run 2 (done): popularity decoupled and used as a boost.** Chose boost over filter (soft preference, no hard cutoff leaving too few candidates). `ranker_b` in `app/ranker.py` slices popularity off the scaled vectors *before* unit-normalizing, computes cosine on the first 8 features, ranks by `similarity + popularity_weight × scaled_popularity`, and returns the pure cosine similarity. Eval-only; not wired into the API. Retrieval is unchanged (9-feature Annoy index), so this isolates a ranking-only change; rebuilding the index on 8 features would be a separate later run.
- **Results (6 mood + 6 track queries, single measurement):** `baseline` (ranker_a) — mood similarity 0.997 / latency 0.079 s / popularity 73; track 0.993 / 0.063 s / 50.67. `boost-w0.05` (ranker_b) — mood 0.995 / 0.072 s / 81.8; track 0.992 / 0.030 s / 63.07. Popularity +9 (mood) / +12 (track) for ~0.001–0.002 similarity. Reading: cheap because candidate cosine scores occupy a very narrow band (~0.99), so even small weights reweight heavily; the baseline's mood popularity (73) sat just under the 75 target because popularity was inside the similarity vector, and the boost removes that ceiling. Caveats: similarity is not strictly comparable across 8- vs 9-feature runs; the track latency drop is likely warm-up noise; small n and no variance estimate; `translate_mood` calls Claude live each run so mood vectors may drift between runs (rerun baseline to check; cache translated vectors in the eval set if needed).
- **Definition of done: met** — two distinct runs logged and comparable side by side in the MLflow UI with params, metrics, and artifacts captured.
- **Remaining:** sweep `popularity_weight` (0.02 / 0.1 / 0.2) as separate runs and read the popularity-vs-similarity curve; check mood-translation drift; consolidate the literal params into one config object; optionally log per-query values.

### Integration points
This sits alongside the existing pipeline, not inside the request path — tracking calls happen in the offline scripts (`scripts/build_index.py`, a future retraining script) and optionally as a lightweight log call in `main.py` when a request completes, not blocking the response (same non-blocking-write principle already used for `recommendation_logs`).

**Definition of done:** at least two distinct runs logged and comparable side-by-side in the MLflow/W&B UI, with parameters, metrics, and the underlying model artifact all captured per run. Nathan can explain what a "run" is, why it's different from a request log, and walk through the UI live.

---

## 30. RAG / Vector Database

**Priority 2.** The single most repeated ask across current DS/ML/MLE postings. Today, `mood.py` uses Claude as a one-shot feature translator (mood string → 8 floats) with no retrieval step at all, and Annoy performs pure vector similarity search with no notion of semantic/text-based retrieval. Neither is a RAG pipeline in the sense the postings mean.

### What changes
Restructure the mood flow so Claude's mood translation is grounded in retrieved context rather than working from the mood string alone: embed track metadata (name, artist, and/or a generated text description of its audio-feature profile) into a vector database, retrieve semantically relevant tracks/context for a given mood string, and feed that retrieved context into the Claude call that produces the final feature targets or the ranked shortlist. This is a real retrieval-augmented pattern, not just a rename of the existing Annoy step.

### Why Pinecone vs. FAISS
Pinecone is a managed, hosted vector DB — zero infra to run, free tier, and the more common "resume keyword" since it shows up by name in most RAG-tooling job postings. FAISS is a library, not a service — self-hosted, more control, no ongoing account/quota to manage, and pairs naturally with the fact that Annoy (also self-hosted, in-process) is already the existing pattern in this codebase. Either is defensible; Pinecone leans toward "I can integrate a managed ML service," FAISS leans toward "I understand what a vector DB is doing under the hood." Pick based on which story matters more.

### Relationship to the existing Annoy index
Annoy is Spotify-built and does one thing well: fast approximate nearest-neighbor search over the existing 9-dimensional numeric audio-feature vectors. The new vector DB does a different thing: semantic search over *text* embeddings (mood descriptions, track descriptions). These aren't redundant — worth being able to explain them as two different retrieval mechanisms serving two different stages, not one replacing the other outright, unless the design ends up fully replacing Annoy (a decision to make once the RAG design is concrete).

**Definition of done:** a mood query retrieves relevant context from the vector DB before Claude produces feature targets or a final ranked list, and Nathan can draw the before/after request flow diagram and explain what retrieval step was added and why it improves on pure one-shot translation.

---

## 31. Deep Learning — Learned Embedding Model

**Priority 3.** The resume lists PyTorch; every project on it is classical ML (cosine similarity, regression-style ranking). This is the credibility gap that shows up the moment an interviewer asks "walk me through a model you built with it" — takes the longest of the four items, but closes the biggest gap.

### What gets built
A learned embedding model (PyTorch) that replaces the hand-engineered 9-feature vector (Section 22) with a learned representation — e.g., a small autoencoder or a two-tower model trained so that tracks which co-occur in positive feedback end up closer together in embedding space than the raw audio features alone would place them.

### Why this, not a bigger/flashier model
The goal is a real, explainable, correctly-evaluated model — not the most complex one. A small autoencoder or two-tower architecture is honestly explainable end-to-end (what goes in, what the loss function optimizes, why the embedding space means what it claims to mean), which matters more for interview defensibility than model size.

### Evaluation
Compare retrieval quality (e.g. NDCG@10, or simpler proxy metrics against the existing feedback data) using the learned embeddings vs. the current hand-engineered vector, on the same candidate pool. A model that isn't measurably compared against the baseline it replaces isn't a finished story.

**Definition of done:** a trained PyTorch model, a documented training process (data, loss, evaluation), and a real comparison number against the hand-engineered baseline it replaces. Nathan can explain the architecture, the loss function, and why the evaluation metric is the right one, without notes.

---

## 32. Stretch — Airflow Orchestration

**Priority 4, after Sections 29–31, not in parallel.** The data pipeline (`scripts/seed_catalog.py` → `scripts/build_index.py`) currently runs manually, in order, by hand. This is the lowest-priority item — orchestration signals production data engineering maturity, but the earlier three items close bigger, more frequently-requested gaps first.

### What gets built
An Airflow DAG that runs the existing scripts as ordered tasks (catalog seeding → index building → optionally the new embedding-model training step from Section 31), with real dependency edges, so the DAG — not a person — decides ordering and re-run behavior on failure.

**Definition of done:** the DAG runs end-to-end in a local Airflow instance, showing the correct task dependency graph, and Nathan can explain what orchestration adds over a shell script that just calls the two scripts in sequence.