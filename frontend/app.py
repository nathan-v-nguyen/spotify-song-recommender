"""Moodify — Streamlit frontend for the music recommendation API."""

import streamlit as st
import requests

# ─── Constants ───────────────────────────────────────────────────────────────
# Read from Streamlit secrets in deployment; fall back to localhost for local dev.
API_BASE = st.secrets.get("API_BASE", "http://localhost:8000")
API_KEY = st.secrets.get("API_KEY", "")

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Moodify", page_icon="🎵", layout="wide")

# ─── Session state defaults ───────────────────────────────────────────────────
for _k, _v in [("mode", "mood"), ("results", None), ("error", None)]:
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ─── API helpers ─────────────────────────────────────────────────────────────
def api_headers() -> dict[str, str]:
    return {"X-API-Key": API_KEY}


def fetch_recommendations(text: str, mode: str) -> dict | None:
    """POST to /recommend/mood or /recommend/track and return JSON, or None on failure."""
    try:
        endpoint = "mood" if mode == "mood" else "track"
        payload = {"mood_string": text} if mode == "mood" else {"spotify_id": text}
        r = requests.post(
            f"{API_BASE}/recommend/{endpoint}",
            json=payload,
            headers=api_headers(),
            timeout=30,
        )
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


@st.cache_data(show_spinner=False, ttl=300)
def search_tracks(query: str) -> list[dict]:
    """GET /search/tracks for autocomplete matches; cached per query, [] on failure."""
    try:
        r = requests.get(
            f"{API_BASE}/search/tracks",
            params={"q": query},
            headers=api_headers(),
            timeout=10,
        )
        return r.json().get("results", []) if r.status_code == 200 else []
    except Exception:
        return []




# ─── HTML renderers ──────────────────────────────────────────────────────────
def render_card(i: int, track: dict, strategy: str) -> str:
    """Return HTML for one recommendation card (hover reveals album + Spotify link)."""
    score_pct = min(100, round(track.get("similarity_score", 0) * 100))
    name = track.get("name", "Unknown")
    artist = track.get("artist", "Unknown")
    album = track.get("album", "") or ""
    expl = track.get("explanation", "") or ""
    sid = track.get("spotify_id", "")
    is_b = "B" in strategy.upper()
    badge_cls = "strategy-b" if is_b else "strategy-a"
    badge_label = "Strategy B" if is_b else "Strategy A"

    expl_html = f'<div class="track-explanation">{expl}</div>' if expl else ""
    album_html = f'<div class="track-album">{album}</div>' if album else ""

    # Single line, no indentation — Streamlit's markdown parser treats lines indented
    # 4+ spaces as code blocks, which would render the raw HTML and break card nesting.
    return (
        f'<div class="song-card">'
        f'<div class="ab-badge {badge_cls}">{badge_label}</div>'
        f'<div class="card-main">'
        f'<span class="track-num">{i:02d}</span>'
        f'<div class="track-info">'
        f'<div class="track-name">{name}</div>'
        f'<div class="track-artist">{artist}</div>'
        f'<div class="score-row">'
        f'<div class="score-bar-bg"><div class="score-bar-fill" style="width:{score_pct}%"></div></div>'
        f'<span class="score-text">{score_pct}%</span>'
        f'</div>'
        f'{expl_html}'
        f'</div>'
        f'</div>'
        f'<div class="card-hover">'
        f'{album_html}'
        f'<a href="https://open.spotify.com/track/{sid}" target="_blank" class="spotify-link">Open in Spotify →</a>'
        f'</div>'
        f'</div>'
    )




# ─── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:ital,wght@0,400;0,500;0,700&family=DM+Sans:wght@400;500;700&display=swap');

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* Page background */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section.main { background: #6B8F71 !important; }

/* Content column */
.block-container {
  padding: 48px 24px 140px !important;
  max-width: 720px !important;
  margin: 0 auto !important;
}

/* Base font */
* { font-family: 'DM Sans', system-ui, sans-serif; }

/* ── Text input ── */
[data-testid="stTextInput"] label { display: none; }
[data-testid="stTextInput"] > div > div {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}
[data-testid="stTextInput"] input {
  background: #1A1A1A !important;
  border: 1px solid #333 !important;
  border-radius: 8px !important;
  color: #fff !important;
  font-size: 15px !important;
  padding: 14px 18px !important;
  caret-color: #1DB954;
}
[data-testid="stTextInput"] input:focus {
  border-color: #1DB954 !important;
  box-shadow: 0 0 0 1px #1DB954 !important;
  outline: none !important;
}
[data-testid="stTextInput"] input::placeholder { color: #555 !important; }

/* ── Mode toggle (radio styled as pills) ── */
[data-testid="stRadio"] { display: flex; justify-content: center; }
[data-testid="stRadio"] > div { width: auto !important; }
[data-testid="stRadio"] > div > div:first-child { display: none !important; }
[data-testid="stRadio"] [role="radiogroup"] { display: flex; gap: 8px; }
[data-testid="stRadio"] input[type="radio"] {
  position: absolute; opacity: 0; width: 0; height: 0;
}
[data-baseweb="radio"] > div:first-child { display: none !important; }
[data-baseweb="radio"] > div:last-child {
  flex: 1 !important;
  text-align: center !important;
  margin: 0 !important;
  padding: 0 !important;
}
[data-testid="stRadio"] label {
  background: rgba(255,255,255,0.15) !important;
  color: rgba(255,255,255,0.6) !important;
  border-radius: 24px !important;
  padding: 8px 28px !important;
  cursor: pointer !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  margin: 0 !important;
  transition: all 0.2s ease !important;
  user-select: none !important;
}
[data-testid="stRadio"] label:has(input:checked) {
  background: #1A1A1A !important;
  color: #FFFFFF !important;
  font-weight: 700 !important;
}
[data-testid="stRadio"] label:hover {
  background: rgba(255,255,255,0.22) !important;
  color: rgba(255,255,255,0.85) !important;
}
[data-testid="stRadio"] label:has(input:checked):hover {
  background: #2a2a2a !important;
  color: #FFFFFF !important;
}

/* Hide "Press Enter to submit form" helper text */
[data-testid="InputInstructions"] { display: none !important; }
.stTextInput small { display: none !important; }

/* ── Find Music (form submit) ── */
[data-testid="stFormSubmitButton"] button {
  background: #1DB954 !important;
  color: #0A0A0A !important;
  border: none !important;
  border-radius: 24px !important;
  font-size: 13px !important;
  font-weight: 700 !important;
  padding: 8px 28px !important;
  width: fit-content !important;
  display: block !important;
  margin: 0 auto !important;
}
[data-testid="stFormSubmitButton"] button:hover { background: #1ED760 !important; }
[data-testid="stFormSubmitButton"] button:focus { outline: none !important; box-shadow: none !important; }

/* ── Find Music (track-mode regular button) ── */
.stButton button,
[data-testid="stButton"] button,
[data-testid="baseButton-secondary"],
[data-testid="stBaseButton-secondary"],
.stButton button[kind="secondary"] {
  background: #1DB954 !important;
  color: #0A0A0A !important;
  border: none !important;
  border-radius: 24px !important;
  font-size: 13px !important;
  font-weight: 700 !important;
  padding: 8px 28px !important;
  width: fit-content !important;
  display: block !important;
  margin: 0 auto !important;
}
.stButton button:hover,
[data-testid="stButton"] button:hover { background: #1ED760 !important; }
.stButton button:focus,
[data-testid="stButton"] button:focus { outline: none !important; box-shadow: none !important; }
.stButton button:disabled,
[data-testid="stButton"] button:disabled {
  background: #2A2A2A !important;
  color: #666 !important;
  cursor: not-allowed !important;
}

/* ── Track search dropdown (selectbox) ── */
[data-testid="stSelectbox"] label { display: none; }
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
  background: #1A1A1A !important;
  border: 1px solid #333 !important;
  border-radius: 8px !important;
  color: #fff !important;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {
  border-color: #1DB954 !important;
  box-shadow: 0 0 0 1px #1DB954 !important;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] span { color: #fff !important; }
[data-testid="stSelectbox"] svg { fill: #A0A0A0 !important; }

/* ── Song cards ── */
.song-card {
  background: #141414;
  border: 1px solid #2A2A2A;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  position: relative;
  transition: border-color 0.2s ease;
}
.song-card:hover { border-color: #1DB954; }
.card-main { display: flex; gap: 16px; align-items: flex-start; }
.track-num {
  color: #1DB954;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 14px;
  font-weight: 500;
  flex-shrink: 0;
  padding-top: 2px;
}
.track-info { flex: 1; }
.track-name { color: #fff; font-size: 16px; font-weight: 700; margin-bottom: 2px; }
.track-artist { color: #A0A0A0; font-size: 14px; margin-bottom: 10px; }
.score-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.score-bar-bg { flex: 1; background: #2A2A2A; height: 3px; border-radius: 2px; overflow: hidden; }
.score-bar-fill { height: 100%; background: #1DB954; border-radius: 2px; }
.score-text {
  color: #A0A0A0;
  font-size: 12px;
  font-family: 'IBM Plex Mono', monospace;
  flex-shrink: 0;
}
.track-explanation { color: #CCCCCC; font-size: 13px; font-style: italic; line-height: 1.5; }

/* Hover-only reveal */
.card-hover {
  max-height: 0;
  overflow: hidden;
  opacity: 0;
  transition: max-height 0.25s ease, opacity 0.2s ease;
}
.song-card:hover .card-hover { max-height: 80px; opacity: 1; }
.track-album { color: #666; font-size: 12px; font-style: italic; margin-top: 10px; margin-left: 30px; }
.spotify-link {
  display: block;
  text-align: right;
  color: #1DB954;
  font-size: 12px;
  text-decoration: none;
  margin-top: 6px;
  font-weight: 500;
}
.spotify-link:hover { color: #1ED760; text-decoration: underline; }

/* A/B badge (top-right, appears on hover) */
.ab-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  opacity: 0;
  transition: opacity 0.2s ease;
}
.song-card:hover .ab-badge { opacity: 1; }
.strategy-a { background: #1A3A2A; color: #1DB954; }
.strategy-b { background: #1A2A3A; color: #4A9EDB; }

</style>
""", unsafe_allow_html=True)


# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown(
    '<div style="color:#fff;font-size:28px;font-weight:700;letter-spacing:-0.5px;margin-bottom:32px">Moodify</div>',
    unsafe_allow_html=True,
)

# ─── Mode toggle ─────────────────────────────────────────────────────────────
_selected = st.radio(
    "mode",
    options=["Mood", "Track"],
    index=0 if st.session_state.mode == "mood" else 1,
    horizontal=True,
    label_visibility="collapsed",
    key="mode_radio",
)
_new_mode = _selected.lower()
if _new_mode != st.session_state.mode:
    st.session_state.mode = _new_mode
    st.session_state.results = None
    st.session_state.error = None
mode = st.session_state.mode

st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)

# ─── Input + submit ───────────────────────────────────────────────────────────
if mode == "mood":
    # Mood mode: free-text in a form, submitted on Enter or button click.
    with st.form("mood_form", clear_on_submit=False):
        mood_input = st.text_input(
            "q",
            placeholder="Describe how you're feeling or what you're doing...",
            label_visibility="collapsed",
        )
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        _, fc, _ = st.columns([2, 2, 2])
        with fc:
            submitted = st.form_submit_button("Find Music")

    if submitted:
        if not mood_input.strip():
            st.session_state.error = "Please enter something to search."
        else:
            st.session_state.error = None
            with st.spinner("Finding your music..."):
                data = fetch_recommendations(mood_input.strip(), "mood")
            st.session_state.results = data
            if not data:
                st.session_state.error = "Something went wrong. Make sure the API is running."

else:
    # Track mode: type a song name → pick a match from the dropdown → Find Music.
    # Wrapped in a bordered container so the layout matches the mood form's white box.
    with st.container(border=True):
        search_q = st.text_input(
            "track_search",
            placeholder="Search your favorite song...",
            label_visibility="collapsed",
            key="track_search",
        )

        matches = search_tracks(search_q.strip()) if search_q.strip() else []
        options = {f'{m["name"]} — {m["artist"]}': m["spotify_id"] for m in matches}

        selected_label = None
        if options:
            selected_label = st.selectbox(
                "match",
                options=list(options.keys()),
                label_visibility="collapsed",
                key="track_match",
            )
        elif search_q.strip():
            st.markdown(
                '<p style="color:#A0A0A0;font-size:13px;text-align:center;margin-top:8px">'
                "No matching songs found.</p>",
                unsafe_allow_html=True,
            )

        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        _, fc, _ = st.columns([2, 2, 2])
        with fc:
            submitted = st.button("Find Music", key="track_submit")

    if submitted:
        if not selected_label:
            st.session_state.error = "Please search and select a song first."
        else:
            st.session_state.error = None
            with st.spinner("Finding your music..."):
                data = fetch_recommendations(options[selected_label], "track")
            st.session_state.results = data
            if not data:
                st.session_state.error = "Something went wrong. Make sure the API is running."

# ─── Error message ────────────────────────────────────────────────────────────
if st.session_state.error:
    st.markdown(
        f'<p style="color:#FF4444;font-size:13px;text-align:center;margin-top:4px">'
        f'{st.session_state.error}</p>',
        unsafe_allow_html=True,
    )

# ─── Results ─────────────────────────────────────────────────────────────────
results = st.session_state.results
if results:
    recs = results.get("recommendations", [])
    strategy = results.get("strategy", "A")
    st.markdown(
        '<div style="color:#fff;font-size:18px;font-weight:700;margin-top:40px;margin-bottom:16px">'
        "Your Recommendations</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "".join(render_card(i + 1, t, strategy) for i, t in enumerate(recs)),
        unsafe_allow_html=True,
    )

