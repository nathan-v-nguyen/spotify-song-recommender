import os
from anthropic import Anthropic
import json

client = Anthropic(api_key = os.environ.get("ANTHROPIC_API_KEY"))

def _neutral_features() -> dict[str, float]:
  '''Hardcoded neutral audio features when Claude fails'''
  return {
     "energy": 0.5,
     "valence": 0.5,
     "danceability": 0.5,
     "tempo": 120.0,
     "acousticness": 0.5,
     "instrumentalness": 0.0,
     "loudness": -8.0,
     "speechiness": 0.05
  }

def translate_mood(mood_string: str) -> dict[str, float]:
    try:
      message = client.messages.create(
        model = "claude-haiku-4-5-20251001",
        max_tokens= 256,
        system="""You are an audio feature translator for a music recommendation system.
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
      Respond with JSON only. No explanation. No preamble.""",
        messages=[{"role": "user", "content":f"Mood: {mood_string}"}])
      text = message.content[0].text
      return json.loads(text)
    except (json.JSONDecodeError, Exception):  
      return _neutral_features()
      