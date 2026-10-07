# CLAUDE.md

## Project Goals

Moodify is a full-stack music recommendation product built on a real ML pipeline: a FastAPI backend that accepts a seed track or natural language mood description and returns 10 personalized song recommendations with explanations, plus an A/B testing framework comparing two ranking strategies (MD5 bucketing, request logging, feedback collection, Streamlit metrics dashboard).

**This project's focus is DS/ML, not SWE.** Nathan is a Data Science major recruiting for Data Science, Data Analyst, and Machine Learning internships for Summer 2027 — most of his existing skills already sit in this track. (An earlier direction pursued SWE internships instead and added a React frontend; that frontend stays as a finished, working demo layer, but is no longer being built out further.) Effort now goes into closing specific ML/DS skill gaps identified from current DS/ML/MLE internship postings, in priority order:

1. **MLOps / experiment tracking** — instrument the existing A/B pipeline with MLflow or Weights & Biases (run tracking, model versioning, metrics)
2. **A real RAG / vector database component** — replace or supplement Annoy with a proper vector database (Pinecone or FAISS) and restructure the Claude mood-translation step as an actual RAG pipeline
3. **A defensible deep learning component** — a learned embedding model (PyTorch) replacing the hand-engineered 9 audio features, so "PyTorch" has a real project behind it
4. **(Stretch) Airflow orchestration** for the data ingestion/feature pipeline

**Primary audience:** DS / Data Analyst / ML internship recruiters and hiring managers  
**Definition of done:** A DS/ML portfolio project demonstrating production ML engineering maturity — real experiment tracking, a RAG-based retrieval component, and a real deep-learning component — built on top of the existing A/B-tested recommendation pipeline and demoable via the existing React frontend  
**Current milestone:** MLOps / experiment tracking (Priority 1 of the list above). See Current Status and Next Steps below

**How to help Nathan on this project:** prioritize teaching the underlying DS/ML/MLOps fundamentals while building, not just producing working code. Explain the *why* behind experiment-tracking, RAG/vector-search, and embedding-model patterns as you go — Nathan dislikes "vibe coding" parts he doesn't understand and needs to be able to defend any architectural decision in a technical interview.

---

## Architecture Overview

FastAPI backend + PostgreSQL database running in Docker. Annoy index for fast similarity search — candidate for replacement/augmentation by a real vector DB, see Project Goals. Claude API for mood translation and explanation generation, with the mood-translation step a candidate for restructuring into an actual RAG pipeline. A React + TypeScript frontend serves as the product-facing demo UI — feature- and styling-complete, frozen, no further frontend work planned. The Streamlit app remains an internal metrics/demo dashboard.

```
spotify-song-recommender/
├── app/
│   ├── main.py              # FastAPI app, all routes (A/B group currently hardcoded to "A"); CORSMiddleware added for the Vite dev origin
│   ├── models.py            # SQLAlchemy table definitions
│   ├── schemas.py           # Pydantic request/response models
│   ├── database.py          # Engine, SessionLocal, Base, get_db
│   ├── auth.py              # API key validation
│   ├── limiter.py           # Rate limiting
│   ├── recommender.py       # Retrieval logic (Annoy index)
│   ├── ranker.py            # ranker_a: cosine on 9 features (live in API); ranker_b: cosine on 8 features + popularity boost (eval-only, not wired into the API)
│   ├── mood.py              # Claude mood → audio features
│   ├── explainer.py         # Claude explanation generation
│   └── utils.py             # empty placeholder — no current use
├── scripts/
│   ├── seed_catalog.py      # Populate tracks table from Kaggle CSV
│   ├── build_index.py       # Build and save Annoy index
│   ├── create_api_key.py    # Generate an API key and assign its A/B group
│   ├── test_recommender.py  # Manual smoke test for recommender.py (not a pytest test)
│   ├── eval_queries.py      # Fixed evaluation set: 6 MoodQuery + 6 TrackQuery frozen dataclasses (the run-comparison test set)
│   └── evaluate_pipeline.py # Offline eval harness + MLflow run logging: avg similarity, latency, avg popularity over the eval set (run: python3 -m scripts.evaluate_pipeline)
├── models/                  # Committed: annoy_index.ann, scaler.pkl, track_id_map.json (ranker_b.pkl not built)
├── data/                    # dataset.csv — Kaggle catalog for seed_catalog.py (gitignored, local-only)
├── frontend/                # Streamlit dashboard (legacy, kept as internal metrics view — app.py)
├── frontend-react/          # React + TypeScript product UI (Vite, CSS Modules) — complete, frozen
│   ├── .env                 # VITE_API_KEY — dev-only, gitignored (see Current Status re: known gap, not being resolved)
│   ├── index.html           # Google Fonts <link> (Fraunces / Karla / JetBrains Mono), page title, meta
│   ├── public/favicon.svg   # custom mark (dark tile, sage record rings, green spindle)
│   └── src/
│       ├── App.tsx          # mode/songs/strategy/hasSearched/isLoading/error state, handleSearch, composes everything below
│       ├── App.module.css   # page shell + the dark "console" panel that groups the controls
│       ├── index.css        # design tokens (colour/type/motion), reset, sage page ground + grain overlay
│       └── components/      # every component has a matching .module.css
│           ├── Heading.tsx
│           ├── ModeToggle.tsx
│           ├── SearchForm.tsx
│           ├── SongCard.tsx
│           └── ResultsList.tsx
├── alembic/                 # Migration environment and versions
├── tests/                   # pytest — test_health.py, test_recommend.py only; not currently being expanded
├── .env                     # Never commit
├── alembic.ini
├── render.yaml              # Render Blueprint (API + Postgres)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt

Planned, not yet created (see Next Steps / ML v2 backlog below):
  app/experiment.py          # A/B assignment + metrics — logic currently inlined in main.py, not extracted
  config object              # one place for n_trees / candidate pool / popularity weight (currently literals in evaluate_pipeline.py) — Priority 1 cleanup
  vector DB / RAG component  # Pinecone or FAISS, replacing/augmenting Annoy — Priority 2
  learned embedding model    # PyTorch, replacing the hand-engineered audio features — Priority 3
  Airflow DAG                # orchestrating the data ingestion/feature pipeline — stretch
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
| Similarity search | Annoy — candidate for replacement/augmentation by a vector DB, see Project Goals |
| Ranking | numpy (`ranker_a` live; `ranker_b` popularity-boost ranker, eval-only); LightGBM ranker not built — not currently scheduled, see Current Status |
| LLM | Anthropic SDK — claude-sonnet-4-20250514 |
| Spotify client | spotipy |
| Rate limiting | slowapi |
| Testing | pytest + httpx |
| Frontend (product UI) | React + Vite + TypeScript, CSS Modules — complete, frozen (no further work planned) |
| Frontend (legacy dashboard) | Streamlit |
| Experiment tracking | MLflow 3.16.1 (chosen over W&B: open source, self-hosted, generalist DS association) — Priority 1, live: runs logged to local SQLite (`mlflow.db`) + `mlruns/` artifacts |
| Vector search / RAG | Pinecone or FAISS — Priority 2, not yet built |
| Deep learning | PyTorch — learned embedding model — Priority 3, not yet built |
| Orchestration (stretch) | Airflow — Priority 4, not yet built |
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

**Frontend styling conventions (`frontend-react/`):**
- One `.module.css` per component, colocated. No global class names except the design tokens in `index.css`.
- Never hardcode a colour, font, radius, or easing curve in a component stylesheet — use the `:root` custom properties from `index.css` (`--sage`, `--ink-panel`, `--cream`, `--green`, `--font-display`, `--radius`, `--ease`, …).
- Green (`--green`) is the only accent and means *signal* — active state, similarity, primary action, external link. Don't spend it on decoration.
- Layout that positions siblings belongs to the parent that composes them, not inside the children.
- Animate `transform`/`opacity`, not `width`/`height`/`top`. Pass per-item values (index, percentage) into CSS as custom properties and keep the animation itself in the stylesheet.
- Every interactive element must be a real `<button>`/`<a>` and reachable by keyboard; rely on the global `:focus-visible` ring rather than removing outlines.
- Every animation must be covered by the `prefers-reduced-motion` block in `index.css`.

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

# Run alembic or any script outside Docker (venv active). .env points DATABASE_URL at
# localhost; docker-compose.yml overrides it to the `db` host for the app container.
alembic upgrade head
python3 -m scripts.evaluate_pipeline   # logs one MLflow run; edit RUN_NAME/RANKER/POPULARITY_WEIGHT in __main__ first, commit before running

# MLflow UI — run from the project root (mlflow.db is relative to cwd), then open http://localhost:5000
# Use the "Model training" toggle (top-left), not GenAI, then Runs tab → tick runs → Compare
mlflow ui

# Permanently purge soft-deleted experiments/runs (UI delete is soft and keeps the name reserved)
mlflow gc --backend-store-uri sqlite:///mlflow.db --tracking-uri sqlite:///mlflow.db

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
- `frontend-react/` — scaffolded with Vite + React + TypeScript; styling via CSS Modules (one `.module.css` per component, e.g. `ModeToggle.module.css`).
- `Heading`, `ModeToggle`, `SearchForm`, `SongCard`, `ResultsList` — built and composed in `App.tsx`. Built static-first (hardcoded fake data, no state), then wired with real state per component below.
- `mode` state (`"mood" | "track"`) — lives in `App` (lifted up, since both `ModeToggle` and `SearchForm` need it), passed down as a prop; `ModeToggle` calls `setMode` via a prop on click rather than owning any state itself.
- `query` state — controlled input (`value` + `onChange`) local to `SearchForm`; `handleSubmit` calls `onSearch(mode, query)`, a callback passed down from `App` (named `handleSearch` there, per the `onX`/`handleX` naming convention).
- Real API integration — `App.tsx`'s `handleSearch` is async: builds the correct endpoint (`/recommend/mood` vs `/recommend/track`) and body (`mood_string` vs `spotify_id`) from `mode`, fetches with the `X-API-Key` header, and updates `songs` state from the response's `recommendations` array. Verified working end-to-end — live recommendations render in `ResultsList`.
- `app/main.py` — added `CORSMiddleware` (`allow_origins=["http://localhost:5173"]`) so the Vite dev server's requests aren't blocked; without it the browser's automatic `OPTIONS` preflight got a 405 (no OPTIONS route existed) and the real POST never ran.
- `.gitignore` — added `frontend-react/node_modules/`.
- **Known gap, not being resolved:** the frontend authenticates to `/recommend/*` using a dev API key read from `frontend-react/.env` (`VITE_API_KEY`, gitignored). This is a real, called-out violation of the "never expose API keys client-side" rule above, acceptable only because this is local-only dev traffic on a frozen demo frontend. Auth work to fix this properly is out of scope after the DS/ML pivot (see Project Goals) — if this frontend is ever put in front of real users, this needs revisiting first.
- `isLoading`/`error` state — added to `App`'s `handleSearch` (`setIsLoading`/`setError` around a `try/catch/finally`, with `error` reset at the start of every call so a stale message can't linger into a new attempt) and threaded down to `SearchForm` as props. `SearchForm` shows "Loading..." and disables the submit button while a request is in flight, and renders the error message inline.
- Track-search autocomplete — `SearchForm` has a debounced `useEffect` (`[query, mode]` dependency array, 300ms `setTimeout` + `clearTimeout` cleanup) that calls `GET /search/tracks` while in track mode and renders a clickable suggestion dropdown. Selecting a suggestion sets the displayed text (`query`) and the actual `spotify_id` to submit (`selectedTrackId`) as two separate pieces of state, since what's shown to the user isn't what the API needs. `handleSubmit` validates before submitting in track mode — "Please choose from the dropdown" if suggestions exist but none was picked, "Song not found" if nothing matched. This is the first real use of `useEffect` in the project; the mood-flow submit fetch correctly still doesn't use one, since it's triggered by an event, not a changing value to sync with.
- Input clearing — `SearchForm` resets `query` and `selectedTrackId` after a successful submit.
- **Full styling pass — complete.** Design direction: a record sleeve. Sage-green "sleeve stock" page ground (carried over from the Streamlit build) with dark ink panels printed on top and Spotify green as the single accent, reserved for signal (active mode, meter fill, submit, Spotify link). Typography is Fraunces (variable display serif, `opsz`/`SOFT`/`WONK` axes) for the wordmark and track titles, Karla for body, JetBrains Mono for numerics and kickers — loaded via a `<link>` with `preconnect` in `index.html` rather than a CSS `@import`, so the font request starts during parse instead of waiting on the stylesheet.
- Design tokens — all colour, type, radius, and easing values live as CSS custom properties on `:root` in `index.css`; no component hardcodes a colour. This is what makes a future theme swap (or a dark/light toggle) a one-file change.
- Page ground — sage base plus two `radial-gradient`s for depth, and a fixed film-grain overlay drawn by an inline SVG `feTurbulence` data URI (`body::before`, `mix-blend-mode: overlay`) — texture with zero extra network requests.
- Layout ownership — `App.module.css` owns the page column and the `.console` panel that visually groups `ModeToggle` + `SearchForm`. The grouping box lives in `App` (the composer) rather than inside either child, so neither component assumes anything about what it's rendered next to.
- `ModeToggle` — segmented control with a pill "thumb" that slides between the two options. Driven entirely by CSS: the container carries `data-mode={mode}` and the stylesheet does `transform: translateX(100%)` on the thumb, so there's no measuring DOM nodes in JS. Buttons carry `aria-pressed`.
- `SearchForm` — input and submit share one pill "field" that lights up together via `:focus-within`; placeholder and helper text now switch per mode; the submit button shows an inline spinner and reads "Finding" while a request is in flight. Autocomplete rows are real `<button>`s inside the `<li>`s (previously an `onClick` on the `<li>`, which was mouse-only and unreachable by keyboard). The status line has a reserved `min-height` so an appearing error doesn't shove the results down.
- `SongCard` — rebuilt as a numbered tracklist row (mono rank, Fraunces title, artist, similarity meter, Claude explanation as an italic liner note). Album + "Open in Spotify" reveal on hover/focus using `grid-template-rows: 0fr → 1fr`, which animates to the content's natural height — no guessed `max-height` to overflow, unlike the Streamlit version. The meter animates with `transform: scaleX()` rather than `width`, so it stays on the compositor instead of forcing layout every frame.
- Staggered entrance — `ResultsList` passes each row's index down as a CSS custom property (`--i`), and the stylesheet computes `animation-delay: calc(var(--i) * 45ms)`. The animation stays entirely in CSS; React only supplies the index.
- `ResultsList` — gained a section header (`TRACKLIST` + track count + strategy), a shimmer skeleton for the loading state that matches the real row rhythm so the layout doesn't jump, and two distinct empty states ("your tracklist is empty" before any search vs. "nothing came back" after one). `App` now tracks `strategy` and `hasSearched` to support these; the hardcoded `fakeSongs` seed data was removed so a fresh page shows the real empty state.
- Accessibility/motion — one global `:focus-visible` ring (keyboard-only, not on mouse click), `role="meter"` with `aria-valuenow` on the similarity bar, and a `prefers-reduced-motion` block that drops all animation while keeping layout intact.
- Two behaviour fixes made during the pass (both pre-existing, both in `SearchForm`): (a) editing the input after picking a suggestion now clears `selectedTrackId`, which previously left the form submitting the *old* track's `spotify_id` while displaying different text; (b) the debounced effect no longer calls `setSuggestions` in its body — dropdown visibility is derived at render time (`showSuggestions`) instead. That removed a cascading re-render (flagged by `eslint-plugin-react-hooks`' `set-state-in-effect`, which was failing `npm run lint`) and also stopped the dropdown from reopening 300ms after every selection.
- Dead code removed — `src/App.css` (unused Vite scaffold boilerplate, never imported).
- Verified: `npm run build` (tsc + vite) and `npm run lint` both pass clean.

**MLOps groundwork (Priority 1) — complete so far:**
- Run definition — a "run" is one distinct pipeline configuration, not one API request. Real knobs today: Annoy `n_trees` (50, build-time), features included in the 9-feature vector, popularity target (hardcoded 75 in the mood flow), candidate pool size (`n=500` in `get_candidates`, query-time). These are still scattered magic numbers; consolidating them into one config object is a prerequisite for clean `log_param` calls.
- `scripts/eval_queries.py` — fixed evaluation set so runs are comparable: 6 mood strings and 6 seed tracks (spotify_ids), chosen to cover the valence/energy quadrants (happy/energetic, calm/content, sad, angry/tense) plus high speechiness and high instrumentalness/acousticness.
- `scripts/evaluate_pipeline.py` — `evaluate_mood_queries` / `evaluate_track_queries` return a frozen `EvalMetrics` (average_similarity, average_latency, average_popularity); shared averaging lives in `calc_eval_metrics`. Latency is timed with `time.perf_counter()` around `get_candidates` + `ranker_a` only (excludes the Claude `translate_mood` call and the seed DB lookup). Runs end-to-end. Baseline (before popularity metric): similarity ≈ 0.997 (mood) / 0.993 (track), latency ≈ 0.069–0.070 s.
- Metric caveats (know these for interviews): average top-10 cosine similarity saturates near 1.0 (non-negative scaled features, candidates pre-selected by the same angular geometry) and isn't comparable across runs that change the feature set; latency is noisy run to run; average popularity is the hypothesis-matched metric for the planned popularity change. Track mode uses the seed's own popularity in the query vector while mood mode hardcodes 75 — a known confound.
- Env — `.env` `DATABASE_URL` points at `@localhost` so scripts run outside Docker; `docker-compose.yml` overrides it to the `db` host for the app container. `mlflow==3.16.1` added to `requirements.txt` (2.19.0 conflicts with `pandas==3.0.2`).
- MLflow wired in `evaluate_pipeline.py` `__main__` — one run per pipeline configuration (mood and track evaluations share a run; metrics prefixed `mood_`/`track_`). Params: `n_trees`, `popularity_target` (`"N/A"` for ranker B, which ignores it), `candidate_pool_size`, `index_hash`, `ranker`, `popularity_weight`. Metrics: the 6 values. Artifacts: `scaler.pkl` and `eval_queries.py` every run; `annoy_index.ann` only when its SHA-256 hash (`file_hash`) hasn't been stored by an earlier run (`index_already_logged` via `mlflow.search_runs`; search happens before `start_run` so a run can't match itself). MLflow 3.x default backend is SQLite `mlflow.db`; both it and `mlruns/` are gitignored. Run `mlflow ui` and the script from the project root.
- `ranker_b` (`app/ranker.py`) — cosine similarity on the first 8 scaled features (popularity sliced off *before* unit-normalizing), ranks by `similarity + popularity_weight * scaled_popularity`, returns pure cosine similarity. Retrieval still uses the 9-feature Annoy index, so candidates are still popularity-influenced (a later run could rebuild on 8 features). `evaluate_*` take a `ranker` callable; `functools.partial` binds the weight.
- Results (6 mood + 6 track queries; single measurement, directional only):
  - `baseline` (ranker_a): mood sim 0.997 / latency 0.079 s / popularity 73; track sim 0.993 / 0.063 s / popularity 50.67.
  - `boost-w0.05` (ranker_b): mood sim 0.995 / 0.072 s / popularity 81.8; track sim 0.992 / 0.030 s / popularity 63.07.
  - Reading: popularity +9 (mood) / +12 (track) for ≈0.001–0.002 similarity — cheap because candidate cosine scores sit in a very narrow band (~0.99), which also means even small weights reweight heavily. Baseline mood popularity (73) sat just under the 75 target because popularity was inside the similarity vector; the boost removes that ceiling (target → "more is better"). Similarity isn't strictly comparable between runs (8 vs 9 features). Track latency halving is likely warm-up/cache noise, not a real win.
- Open caveats: `translate_mood` calls Claude live each run, so mood feature vectors may drift between runs (check by rerunning baseline; cache translated vectors in the eval set if they do). Experiment-design workflow learned: commit before each run (MLflow records params, not code); never log a `partial` object as a param (its repr contains a memory address).

**ML v2 backlog (accurate gap, not currently scheduled ahead of the roadmap below):**
- `POST /feedback`, `GET /experiments/results` — not built
- Strategy B (LightGBM ranker) — not built (the name `ranker_b` is now used by the popularity-boost ranker, which is eval-only and not an A/B arm)
- A/B assignment — both endpoints hardcode `experiment_group="A"`; not wired to the API-key hash yet

**In progress:**
- Nothing actively in progress. The React frontend is feature- and styling-complete and frozen — no further frontend work planned. The JWT auth work that was briefly started (users table design, `/auth/*` contracts) was abandoned when the project pivoted back to DS/ML; none of that was implemented and none of it carries forward.
- MLOps / experiment tracking (Priority 1) is mostly done: two comparable runs (`baseline`, `boost-w0.05`) are logged and compared in the MLflow UI, with params, metrics, and artifacts captured (definition of done met). Remaining: a popularity-weight sweep, a config object for the literal params, and optional cleanups (type hint on the `ranker` argument, trailing whitespace, aggregation could be inlined; `evaluate_*` slightly exceed the 40-line guideline — relaxed for this script).
- RAG/vector DB, deep learning component, and Airflow have not yet been started.

**Next steps (current priority, in order):**
1. MLOps / experiment tracking — finish up: (a) sweep `popularity_weight` (e.g. 0.02, 0.1, 0.2) as separate runs and read the popularity-vs-similarity tradeoff curve in the MLflow compare view; (b) check whether mood translations drift between runs (rerun baseline) and cache them if so; (c) consolidate the literal params (`n_trees`, candidate pool, popularity target/weight) into one config object; (d) optionally log per-query values to see which query drives each metric. Tracking belongs in offline scripts, not the live request path
2. RAG / vector database — replace or supplement Annoy with a proper vector database (Pinecone or FAISS); restructure the Claude mood-translation step (`app/mood.py`) as an actual retrieval-augmented pipeline
3. Deep learning component — a learned embedding model (PyTorch) replacing the hand-engineered 9 audio features, giving a real project behind "PyTorch" rather than a listed-but-unproven skill
4. (Stretch) Airflow — orchestrate the data ingestion/feature pipeline (`scripts/seed_catalog.py` → `scripts/build_index.py`) instead of running it manually

---

## Documentation

- [Overview](docs/overview.md) — full project context, career goals, background
- [Project Spec](docs/project_spec.md) — detailed requirements, API contract, architecture decisions; Part 3 (Sections 24–28) documents the earlier SWE-focused roadmap (React frontend built during that phase and kept; auth/testing-CI-CD/system-design-writeup sections describe abandoned work, not a plan) — see Section 0 in that file for the current DS/ML direction
- Update files in docs folder after major milestones and major additions to the project
