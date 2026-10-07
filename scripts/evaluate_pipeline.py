"""Offline evaluation harness — measures similarity, latency, and popularity over the fixed eval query set."""

import hashlib
import time
from dataclasses import dataclass
from statistics import mean
import mlflow
from functools import partial

from app.mood import translate_mood
from app.ranker import ranker_a, ranker_b
from app.recommender import get_candidates, track_to_vector
from app.models import Track

from scripts.eval_queries import MOOD_QUERIES, MoodQuery, TRACK_QUERIES, TrackQuery

from app.database import SessionLocal

@dataclass(frozen=True)
class EvalMetrics:
  '''Evaluation Metrics for pipeline'''
  average_similarity: float
  average_latency: float
  average_popularity: float

def calc_eval_metrics(recommendations: list[tuple[Track, float]]) -> tuple[float, float]:
  ''' Calculates average_similarity and average_popularity given the recommended tracks '''
  avg_similarity = mean(score for _, score in recommendations)
  avg_popularity = mean(track.popularity for track, _ in recommendations)
  
  return (avg_similarity, avg_popularity)


def evaluate_mood_queries(mood_queries: list[MoodQuery], ranker) -> EvalMetrics:
  ''' Measures latency, average similarity, and average popularity scores across evaluation mood queries '''
  db = SessionLocal()

  try: 
    similarity_scores = []
    latency_times = []
    popularity_scores = []
    for mood_query in mood_queries:
      query_vector = list(translate_mood(mood_query.mood_string).values()) + [75] # popularity score

      start = time.perf_counter()

      candidates = get_candidates(query_vector)
      recommendations = ranker(query_vector, candidates, db)

      elapsed = time.perf_counter() - start

      avg_similarity_score, avg_popularity_score = calc_eval_metrics(recommendations)
      similarity_scores.append(avg_similarity_score)
      popularity_scores.append(avg_popularity_score)

      latency_times.append(elapsed)
    
    average_similarity = mean(similarity_scores)

    average_latency_time = mean(latency_times)

    average_popularity = mean(popularity_scores)
    
    return EvalMetrics(
      average_similarity=average_similarity,
      average_latency=average_latency_time,
      average_popularity=average_popularity
    )
  finally:
    db.close()


def evaluate_track_queries(track_queries: list[TrackQuery], ranker) -> EvalMetrics:
  ''' Measures latency, average similarity, and average popularity scores across evaluation track queries '''
  db = SessionLocal()

  try:
    similarity_scores = []
    latency_times = []
    popularity_scores = []

    for track_query in track_queries:
      track = db.query(Track).filter(Track.spotify_id == track_query.spotify_id).first()

      if not track:
        raise ValueError(f"Track not found in catalog: {track_query.spotify_id} ({track_query.name})")

      
      query_vector = track_to_vector(track)

      start = time.perf_counter()

      candidates = get_candidates(query_vector)
      recommendations = ranker(query_vector, candidates, db)

      elapsed = time.perf_counter() - start

      latency_times.append(elapsed)

      avg_similarity_score, avg_popularity_score = calc_eval_metrics(recommendations)
      similarity_scores.append(avg_similarity_score)
      popularity_scores.append(avg_popularity_score)

    average_similarity = mean(similarity_scores)

    average_latency_time = mean(latency_times)

    average_popularity = mean(popularity_scores)

    return EvalMetrics(
      average_similarity=average_similarity,
      average_latency=average_latency_time,
      average_popularity=average_popularity
    )
  finally:
    db.close()


def file_hash(path: str) -> str:
  ''' Returns a short SHA-256 fingerprint of a file's contents '''
  with open(path, "rb") as f:
    return hashlib.sha256(f.read()).hexdigest()[:12]


def index_already_logged(experiment_name: str, index_hash: str) -> bool:
  ''' Checks whether a previous run in the experiment already stored an index with this hash '''
  previous_runs = mlflow.search_runs(
    experiment_names=[experiment_name],
    filter_string=f"params.index_hash = '{index_hash}'",
    max_results=1,
  )
  return not previous_runs.empty


if __name__ == "__main__":
  EXPERIMENT_NAME = "moodify-pipeline"
  INDEX_PATH = "models/annoy_index.ann"

  RUN_NAME = "boost-w0.05"
  POPULARITY_WEIGHT = 0.05
  RANKER = partial(ranker_b, popularity_weight=POPULARITY_WEIGHT)
  

  mlflow.set_experiment(EXPERIMENT_NAME)
  index_hash = file_hash(INDEX_PATH)
  index_is_new = not index_already_logged(EXPERIMENT_NAME, index_hash)

  with mlflow.start_run(run_name=RUN_NAME):
    mlflow.log_param("n_trees", 50)
    mlflow.log_param("popularity_target", "N/A")
    mlflow.log_param("candidate_pool_size", 500)
    mlflow.log_param("index_hash", index_hash)
    mlflow.log_param("ranker", "B")
    mlflow.log_param("popularity_weight", POPULARITY_WEIGHT)

    mlflow.log_artifact("models/scaler.pkl")
    mlflow.log_artifact("scripts/eval_queries.py")
    if index_is_new:
      mlflow.log_artifact(INDEX_PATH)

    
    mood_eval_metrics = evaluate_mood_queries(MOOD_QUERIES, RANKER)
    track_eval_metrics = evaluate_track_queries(TRACK_QUERIES, RANKER)

    mlflow.log_metric("mood_avg_similarity", mood_eval_metrics.average_similarity)
    mlflow.log_metric("mood_avg_latency", mood_eval_metrics.average_latency)
    mlflow.log_metric("mood_avg_popularity", mood_eval_metrics.average_popularity)

    mlflow.log_metric("track_avg_similarity", track_eval_metrics.average_similarity)
    mlflow.log_metric("track_avg_latency", track_eval_metrics.average_latency)
    mlflow.log_metric("track_avg_popularity", track_eval_metrics.average_popularity)

    


  