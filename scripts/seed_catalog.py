import pandas as pd
import os
from app.database import SessionLocal
from app.models import Track

df = pd.read_csv("data/dataset.csv")
df = df[["track_id", "artists", "album_name", "track_name", "popularity", "danceability", "energy", "loudness", "acousticness", "instrumentalness", "valence", "tempo", "speechiness"]]
df = df.dropna()
df = df.drop_duplicates(subset=['track_id'])
df = df.set_index("track_id")


db = SessionLocal()

existing_ids = set(row[0] for row in db.query(Track.spotify_id).all())

try:
  count = 0
  for id, row in df.iterrows():
    if id in existing_ids:
      continue
    track = Track(
      spotify_id=id,
      name=row["track_name"],
      artist=row["artists"],
      album=row["album_name"],
      energy=row["energy"],
      valence=row["valence"],
      danceability=row["danceability"],
      tempo=row["tempo"],
      acousticness=row["acousticness"],
      instrumentalness=row["instrumentalness"],
      loudness=row["loudness"],
      popularity= int(row["popularity"]),
      speechiness=row["speechiness"]
      )
    db.add(track)
    count += 1
    if count % 100 == 0:
            print(f"Added {count} tracks...")
  db.commit()
  print(f"Done! Total tracks added: {count}")
finally:
  db.close()


