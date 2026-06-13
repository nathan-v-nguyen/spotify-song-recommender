## Moodify — AI Music Recommendation Engine

Moodify is a production-grade music recommendation system that accepts natural language mood descriptions or the name of a song and returns personalized song recommendations with AI-generated explanations.

**Try it live:** [moodify.streamlit.app](https://spotify-song-recommender-cbdygkccpyqqsgzntmrpru.streamlit.app)

### What it does
Describe how you're feeling — "late night drive feeling nostalgic" or "high energy workout" — and Moodify translates your mood into audio feature targets using Claude, searches a catalog of 89,000+ Spotify tracks using approximate nearest neighbor search, and returns the 10 best matches with a one-sentence explanation for each.

Enter the name of a song and Moodify will use the same process as above to return the 10 most similar songs

### How it's built
- **Backend:** FastAPI + PostgreSQL, containerized with Docker, deployed on Render
- **ML pipeline:** Two-stage retrieval → ranking using Annoy (ANN indexing) and cosine similarity
- **LLM integration:** Claude API for mood-to-audio-feature translation and recommendation explanations
- **Experiment infrastructure:** A/B testing framework comparing two ranking strategies with live metrics
- **Frontend:** Streamlit, deployed on Streamlit Community Cloud
- **CI/CD:** GitHub Actions runs the full test suite on every push to main

### Catalog
89,740 tracks seeded from a Spotify audio features dataset, covering 125+ genres with 9 audio features per track (energy, valence, danceability, tempo, acousticness, instrumentalness, loudness, speechiness, popularity).
