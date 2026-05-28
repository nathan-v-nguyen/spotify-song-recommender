"""Generates one-sentence explanations for recommended tracks using Claude."""

import os
import logging
from anthropic import Anthropic
import json
from app.models import Track

logger = logging.getLogger(__name__)
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def _format_track(i: int, track: Track) -> str:
    energy = f"{track.energy:.2f}" if track.energy is not None else "N/A"
    valence = f"{track.valence:.2f}" if track.valence is not None else "N/A"
    tempo = f"{track.tempo:.0f}" if track.tempo is not None else "N/A"
    return f'{i+1}. "{track.name}" by {track.artist} (energy={energy}, valence={valence}, tempo={tempo} BPM)'


def explain_recommendations(mood_string: str, tracks: list[Track]) -> list[str | None]:
    """Generates one-sentence explanations for recommended tracks using Claude."""
    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=(
                "You are a music recommendation explainer. You will receive a mood description "
                "and a list of songs. For each song, write exactly one sentence (under 30 words) explaining "
                "why it fits the mood. Respond with ONLY a JSON array of strings, one per song, in the same "
                "order as the input list. No preamble."
            ),
            messages=[{
                "role": "user",
                "content": (
                    f"Mood: {mood_string}\n\nSongs:\n" +
                    "\n".join(_format_track(i, track) for i, track in enumerate(tracks))
                ),
            }],
        )
        raw = message.content[0].text.strip()
        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:])  # remove first line (```json)
            raw = raw.rsplit("```", 1)[0]  # remove closing ```
            raw = raw.strip()
        parsed = json.loads(raw)
        if isinstance(parsed, list) and len(parsed) == len(tracks):
            return parsed
        logger.warning("Explainer returned %d items for %d tracks", len(parsed), len(tracks))
        return [None] * len(tracks)
    except Exception as e:
        logger.error("Explainer failed: %s", e)
        print(f"EXPLAINER ERROR: {e}")
        return [None] * len(tracks)