"""Rank candidate tracks by cosine similarity to the query vector and return the top n."""

from app.recommender import track_to_vector
import numpy as np
import joblib
from sqlalchemy.orm import Session
from app.models import Track

scaler = joblib.load("models/scaler.pkl")



def ranker_a(query_vector: np.ndarray, candidate_ids: list[str], db: Session, n: int = 10) -> list[tuple[Track, float]]:
  """
  Returns list of top 10 Tracks and similarity scores out of the 500 candidates based off cosine similarity
  """
  candidate_tracks = db.query(Track).filter(Track.spotify_id.in_(candidate_ids)).all()
  candidate_vectors = np.array([track_to_vector(t) for t in candidate_tracks])


  query_vector_normalized = scaler.transform([query_vector])[0]
  candidate_matrix_normalized = scaler.transform(candidate_vectors)


  query_norm = query_vector_normalized / (np.linalg.norm(query_vector_normalized) + 1e-9)
  candidate_norms = candidate_matrix_normalized / (np.linalg.norm(candidate_matrix_normalized, axis=1, keepdims=True) + 1e-9)


  scores = candidate_norms @ query_norm


  top_indices = np.argsort(scores)[::-1][:n]
  return [(candidate_tracks[i], scores[i]) for i in top_indices]


def ranker_b(query_vector: np.ndarray, candidate_ids: list[str], db: Session, popularity_weight: float, n: int = 10) -> list[tuple[Track, float]]:
  """
  Returns list of top 10 Tracks and similarity scores out of the 500 candidates based off cosine similarity on 8 features plus a popularity boost. Returns cosine similarity
  """
  candidate_tracks = db.query(Track).filter(Track.spotify_id.in_(candidate_ids)).all()
  candidate_vectors = np.array([track_to_vector(t) for t in candidate_tracks])


  query_vector_normalized = scaler.transform([query_vector])[0]
  candidate_matrix_normalized = scaler.transform(candidate_vectors)

  # Slice off popularity
  query_features = query_vector_normalized[:8]
  candidate_matrix = candidate_matrix_normalized[:, :8]

  query_norm = query_features / (np.linalg.norm(query_features) + 1e-9)
  candidate_norms = candidate_matrix / (np.linalg.norm(candidate_matrix, axis=1, keepdims=True) + 1e-9)

  similarity = candidate_norms @ query_norm

  final_score = similarity + popularity_weight * candidate_matrix_normalized[:, 8]

  top_indices = np.argsort(final_score)[::-1][:n]

  return [(candidate_tracks[i], similarity[i]) for i in top_indices]