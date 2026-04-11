"""SQLAlchemy ORM models defining all database tables."""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Track(Base):
    """Stores every song in the catalog with Spotify audio features."""

    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, index=True)
    spotify_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    album = Column(String)
    energy = Column(Float)
    valence = Column(Float)
    danceability = Column(Float)
    tempo = Column(Float)
    acousticness = Column(Float)
    instrumentalness = Column(Float)
    loudness = Column(Float)
    speechiness = Column(Float)
    popularity = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())


class RecommendationLog(Base):
    """Logs every recommendation request for monitoring and A/B experiment data."""

    __tablename__ = "recommendation_logs"

    id = Column(Integer, primary_key=True, index=True)
    request_type = Column(String)
    input_data = Column(String)
    experiment_group = Column(String)
    strategy_used = Column(String)
    recommendations = Column(String)
    created_at = Column(DateTime, server_default=func.now())


class Feedback(Base):
    """Stores thumbs up/down ratings tied to specific recommendation logs."""

    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(Integer, ForeignKey("recommendation_logs.id"), nullable=False, index=True)
    spotify_id = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class ApiKey(Base):
    """Stores valid API keys and their deterministic A/B experiment group assignment."""

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    experiment_group = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())