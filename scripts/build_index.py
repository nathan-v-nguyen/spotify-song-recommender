"""Build and save the Annoy index from tracks stored in the database."""

import json
import os

import joblib
import numpy as np
from annoy import AnnoyIndex
from sklearn.preprocessing import MinMaxScaler

from app.database import SessionLocal
from app.models import Track


MODELS_DIR = "models"
SCALER_PATH = os.path.join(MODELS_DIR, "scaler.pkl")


def load_tracks() -> tuple[list[str], list[list[float]]]:
    """Load all tracks from DB and return parallel lists of spotify_ids and raw feature rows."""
    db = SessionLocal()
    try:
        tracks = db.query(Track).all()
        spotify_ids = []
        feature_rows = []
        for track in tracks:
            spotify_ids.append(track.spotify_id)
            feature_rows.append([
                track.energy,
                track.valence,
                track.danceability,
                track.tempo,
                track.acousticness,
                track.instrumentalness,
                track.loudness,
                track.speechiness,
                track.popularity,
            ])
        return spotify_ids, feature_rows
    finally:
        db.close()


def normalize_features(feature_rows: list[list[float]]) -> tuple[np.ndarray, MinMaxScaler]:
    """Fit a MinMaxScaler on the full feature matrix and return the normalized matrix and scaler.

    The scaler is saved to disk so query vectors at request time can be transformed
    identically — same min/max boundaries learned from the catalog.
    """
    matrix = np.array(feature_rows, dtype=float)
    scaler = MinMaxScaler()
    normalized = scaler.fit_transform(matrix)
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(scaler, SCALER_PATH)
    print(f"Scaler saved to {SCALER_PATH}")
    return normalized, scaler

def build_index(spotify_ids: list[str], normalized_matrix: np.ndarray) -> None:
    """Build Annoy index from normalized feature matrix and save to disk."""
    f = 9
    t = AnnoyIndex(f, 'angular')

    for i, vector in enumerate(normalized_matrix):
        t.add_item(i, vector.tolist())
    
    t.build(50)
    
    index_path = os.path.join(MODELS_DIR, "annoy_index.ann")
    t.save(index_path)
    print(f"Index saved to {index_path}")

    id_map_path = os.path.join(MODELS_DIR, "track_id_map.json")
    with open(id_map_path, "w") as f_out:
        json.dump(spotify_ids, f_out)
    print(f"ID map saved to {id_map_path}")
    print(f"Total tracks indexed: {len(spotify_ids)}")



if __name__ == "__main__":
    spotify_ids, feature_rows = load_tracks()
    print(f"Loaded {len(spotify_ids)} tracks from database")

    normalized_matrix, scaler = normalize_features(feature_rows)
    print(f"Normalized feature matrix shape: {normalized_matrix.shape}")

    build_index(spotify_ids, normalized_matrix)
