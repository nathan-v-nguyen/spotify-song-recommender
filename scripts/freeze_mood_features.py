from scripts.eval_queries import MOOD_QUERIES, FEATURE_ORDER
from app.mood import translate_mood, _neutral_features
from statistics import median
import json

if __name__ == "__main__":
  '''Gets feature vectors for 6 mood query strings'''
  frozen = {}
  for mood_query in MOOD_QUERIES:
    mood_str = mood_query.mood_string
    results = [translate_mood(mood_str) for _ in range(5)]
    failures = sum(r == _neutral_features() for r in results)
    if failures: raise ValueError(f"Mood translation failed for: {mood_str}")

    res = {}

    for key in FEATURE_ORDER:
      med = median(r[key] for r in results)
      res[key] = med

    frozen[mood_str] = res
    
  with open("scripts/eval_mood_features.json", "w") as f:
    json.dump(frozen, f, indent=2)