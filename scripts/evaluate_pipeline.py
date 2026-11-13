"""Offline evaluation harness — measures similarity, latency, and popularity over the fixed eval query set."""

import argparse
import hashlib
import time
from dataclasses import dataclass
from statistics import mean
import mlflow
import json
from typing import Callable

from app.recommender import get_candidates, track_to_vector
from app.models import Track

from scripts.eval_queries import MOOD_QUERIES, MoodQuery, TRACK_QUERIES, TrackQuery, FEATURE_ORDER
from scripts.run_config import RUNS, RunConfig, build_ranker, config_params

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

def load_frozen_features(path: str) -> dict[str, dict[str, float]]:
  ''' Gets frozen features from json '''
  with open(path) as f:
    return json.load(f)

def evaluate_mood_queries(
  mood_queries: list[MoodQuery],
  ranker: Callable,
  frozen_features: dict[str, dict[str, float]],
  popularity_target: int,
  candidate_pool_size: int,
) -> EvalMetrics:
  ''' Measures latency, average similarity, and average popularity scores across evaluation mood queries '''
  db = SessionLocal()

  try: 
    similarity_scores = []
    latency_times = []
    popularity_scores = []
    for mood_query in mood_queries:
      features = frozen_features[mood_query.mood_string]
      query_vector = [features[k] for k in FEATURE_ORDER] + [popularity_target]

      start = time.perf_counter()

      candidates = get_candidates(query_vector, n=candidate_pool_size)
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


def evaluate_track_queries(track_queries: list[TrackQuery], ranker: Callable, candidate_pool_size: int) -> EvalMetrics:
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

      candidates = get_candidates(query_vector, n=candidate_pool_size)
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


EXPERIMENT_NAME = "moodify-pipeline"
INDEX_PATH = "models/annoy_index.ann"
FROZEN_FEATURES_PATH = "scripts/eval_mood_features.json"


def run(config: RunConfig) -> None:
  ''' Evaluates one configuration and logs it as a single MLflow run '''
  frozen_features = load_frozen_features(FROZEN_FEATURES_PATH)
  ranker = build_ranker(config)

  mlflow.set_experiment(EXPERIMENT_NAME)
  index_hash = file_hash(INDEX_PATH)
  index_is_new = not index_already_logged(EXPERIMENT_NAME, index_hash)

  with mlflow.start_run(run_name=config.run_name):
    mlflow.log_params(config_params(config))
    mlflow.log_param("index_hash", index_hash)

    mlflow.log_artifact("models/scaler.pkl")
    mlflow.log_artifact("scripts/eval_queries.py")
    mlflow.log_artifact(FROZEN_FEATURES_PATH)
    if index_is_new:
      mlflow.log_artifact(INDEX_PATH)

    mood = evaluate_mood_queries(
      MOOD_QUERIES, ranker, frozen_features, config.popularity_target, config.candidate_pool_size
    )
    track = evaluate_track_queries(TRACK_QUERIES, ranker, config.candidate_pool_size)

    mlflow.log_metrics({
      "mood_avg_similarity": mood.average_similarity,
      "mood_avg_latency": mood.average_latency,
      "mood_avg_popularity": mood.average_popularity,
      "track_avg_similarity": track.average_similarity,
      "track_avg_latency": track.average_latency,
      "track_avg_popularity": track.average_popularity,
    })


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Run one named evaluation config and log it to MLflow")
  parser.add_argument("run_name", choices=sorted(RUNS), help="a config name defined in scripts/run_config.py")
  run(RUNS[parser.parse_args().run_name])


  