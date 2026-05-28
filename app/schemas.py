"""Pydantic request and response models for all API endpoints.""" 

from pydantic import BaseModel, ConfigDict, Field

class TrackRecommendationRequest(BaseModel):
  """What the user sends in"""
  spotify_id: str
  limit: int = Field(default=10, ge=1, le=50)

class TrackRecommendation(BaseModel):
  """A single recommended track in the response"""
  model_config = ConfigDict(from_attributes=True)

  spotify_id: str
  name: str
  artist: str
  album: str | None
  explanation: str | None
  similarity_score: float

class MoodRecommendationRequest(BaseModel):
  """What the user sends for mood-based recommendations"""
  mood_string: str = Field(min_length=1,max_length=500)
  limit: int = Field(default=10, ge=1, le=50)

class RecommendationResponse(BaseModel):
  """The full response envelope that wraps everything"""
  recommendations: list[TrackRecommendation]
  experiment_group: str
  strategy: str
  log_id: int