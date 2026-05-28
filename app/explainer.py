"""Generates one-sentence explanations for recommended tracks using Claude."""

import os
from anthropic import Anthropic
import json
from app.models import Track

client = Anthropic(api_key = os.environ.get("ANTHROPIC_API_KEY"))

def explain_recommendations(mood_string: str, tracks: list[Track]) -> list[str]:
    """Generates one-sentence explanations for recommended tracks using Claude."""
    
    try:
      message = client.messages.create(
          model="claude-sonnet-4-6",
          max_tokens=1024,
          system="""You are a music recommendation explainer. You will receive a mood description
  and a list of 10 songs. For each song, write exactly one sentence (under 30 words) explaining
  why it fits the mood. Respond with ONLY a JSON array of 10 strings, one per song, in the same
  order as the input list. No preamble.""",
          messages=[{
              "role": "user",
              "content": (
                  f"Mood: {mood_string}\n\nSongs:\n" +
                  "\n".join(
                      f'{i+1}. "{track.name}" by {track.artist} '
                      f'(energy={track.energy:.2f}, valence={track.valence:.2f}, tempo={track.tempo:.0f} BPM)'
                      for i, track in enumerate(tracks)
                  )
              )
          }]
      )
      
      parsed = json.loads(message.content[0].text) 
      if isinstance(parsed, list) and len(parsed) == len(tracks):
        return parsed
      return [None] * len(tracks)
    except Exception:
      return [None] * len(tracks)