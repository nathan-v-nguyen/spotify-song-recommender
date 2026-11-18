# Moodify — Mood-Based Music Recommendation with Experiment Tracking

> TODO (one sentence, your words): what Moodify is and the one thing you want a recruiter to remember. Suggestion: lead with the result, e.g. a two-stage retrieval-and-ranking pipeline over 89,740 tracks, tuned and evaluated with MLflow.

## Demo

> TODO: link to your demo video (YouTube unlisted or Loom), then a GIF under it.
> Video plan (60–90 s): one mood search and one track search in the React UI, then the MLflow compare view.

[Watch the demo video](TODO-link)

![Moodify demo](docs/images/demo.gif)

## What it does

Describe how you're feeling — "late night drive feeling nostalgic" or "high energy workout" — and Moodify translates your mood into audio feature targets using Claude, searches a catalog of 89,000+ Spotify tracks using approximate nearest neighbor search, and returns the 10 best matches with a one-sentence explanation for each.

Enter the name of a song and Moodify uses the same pipeline to return the 10 most similar songs.

![Moodify results page](docs/images/ui-results.png)

## Architecture

> TODO: add a diagram (draw.io, Excalidraw, or Mermaid) showing the flow below, then explain in your own words *why* it is two stages.

Facts to cover:
- Mood string → Claude translates it into 8 audio features (energy, valence, danceability, tempo, acousticness, instrumentalness, loudness, speechiness); the popularity feature is added as a target.
- Stage 1, retrieval: Annoy (angular distance, 50 trees) returns a pool of candidate tracks from the 9-feature index.
- Stage 2, ranking: cosine similarity over the candidates picks the top 10.
- Claude then writes a one-sentence explanation per track (mood mode).
- FastAPI + PostgreSQL in Docker; React + TypeScript frontend; API-key auth and per-IP rate limiting.

## Experiment tracking and results

> TODO: explain in your own words what a "run" is here and why it differs from a request log.

Facts to cover:
- Fixed evaluation set: 6 mood strings and 6 seed tracks, chosen to cover the valence/energy quadrants plus high speechiness and high instrumentalness/acousticness.
- Metrics per run: average top-10 similarity, latency, and average popularity, for mood and track queries separately.
- Every run is a named, validated configuration (`scripts/run_config.py`) logged to MLflow with its parameters, metrics, and artifacts (scaler, index hash, eval set).
- The question tested: can you trade a little similarity for more popular recommendations, and which lever is better, the ranking weight or the retrieval pool size?

### Popularity weight sweep (candidate pool 500)

| Weight | Mood: popularity / similarity | Track: popularity / similarity |
|---|---|---|
| baseline (no boost) | 59.75 / 0.984 | 50.67 / 0.993 |
| 0.05 | 61.28 / 0.986 | 63.07 / 0.992 |
| 0.1 | 70.88 / 0.979 | 66.25 / 0.989 |
| 0.2 | 77.65 / 0.970 | 68.27 / 0.986 |
| 0.5 | 80.85 / 0.961 | 69.65 / 0.983 |

![Popularity vs similarity, weight sweep](docs/images/mlflow-weight-sweep.png)

> TODO (your words): what the tradeoff curve shows (diminishing returns, knee around 0.1–0.2).

### Candidate pool sweep (weight 0.2)

| Pool size | Mood: popularity / similarity | Track: popularity / similarity |
|---|---|---|
| 500 | 77.65 / 0.970 | 68.27 / 0.986 |
| 1000 | 78.60 / 0.969 | 71.45 / 0.985 |
| 2000 | 79.78 / 0.968 | 73.57 / 0.985 |
| 5000 | 80.87 / 0.968 | 77.62 / 0.984 |

![Candidate pool sweep](docs/images/mlflow-pool-sweep.png)

> TODO (your words): the headline finding. A larger retrieval pool raised popularity more than a larger ranking weight did, at almost no similarity cost, which shows retrieval was the bottleneck. Mention the latency tradeoff, and that latency measurements are noisy (see Limitations).

![MLflow run comparison](docs/images/mlflow-compare.png)

## Engineering lessons

> TODO: write each of these as a short paragraph in your own voice. These are the parts interviewers will ask about.

1. **A silent failure that looked like valid results.** The mood module never loaded `.env`, so every Claude call failed, hit a bare `except`, and returned a neutral fallback vector. All six mood queries were identical. Clues: mood popularity was an exact integer, similarity was identical to 16 digits across runs, and no raw-output lines printed. How you caught it (the drift check showed every spread was exactly 0.0) and what you changed.
2. **Freezing the LLM's output for a fair evaluation.** Claude's translations drift between calls (tempo ±4–10 BPM, loudness up to 1.6 dB), which is about the size of the gaps between candidate scores. You froze the median of 5 translations so runs differ only by what you changed.
3. **Making mislabeled runs impossible.** Hand-editing a script between runs nearly mislabeled runs several times; a validated config object and name-based CLI replaced that.

## Tech stack

FastAPI · PostgreSQL · SQLAlchemy · Alembic · Annoy · NumPy · scikit-learn · Claude API · MLflow · React + TypeScript (Vite) · Streamlit (internal metrics dashboard) · Docker · pytest

## Run it locally

> TODO: verify every command below on a clean checkout before publishing.

```bash
git clone <repo-url> && cd spotify-song-recommender
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# .env needs: DATABASE_URL (postgresql://...@localhost:5432/recsys) and ANTHROPIC_API_KEY
docker compose up db
alembic upgrade head

# download the Kaggle Spotify audio-features dataset to data/dataset.csv (TODO: link the dataset)
python3 -m scripts.seed_catalog

python3 -m scripts.create_api_key
uvicorn app.main:app --reload

# frontend (put the key in frontend-react/.env as VITE_API_KEY)
cd frontend-react && npm install && npm run dev
```

Reproduce the experiments:

```bash
python3 -m scripts.evaluate_pipeline baseline     # --help lists all configs
mlflow ui                                         # then open http://localhost:5000
```

## Limitations

> TODO: keep this section; stating limits plainly builds credibility.

- Results are single measurements on a 12-query evaluation set, with no variance estimate; treat them as directional.
- Latency is noisy (cold starts, single timings), so the pool-size latency curve is not reliable.
- Similarity scores are comparable within a sweep (same features) but not between the 9-feature baseline and the 8-feature boosted ranker.
- The popularity-boost ranker is evaluated offline only; it is not wired into the API.
- The app is not publicly deployed; the demo video shows it running.

## Roadmap (planned, not built)

- Vector database / RAG: replace or supplement Annoy and restructure the mood translation as retrieval-augmented.
- A learned embedding model (PyTorch) to replace the hand-engineered audio features.
- Airflow orchestration of the data ingestion pipeline.
