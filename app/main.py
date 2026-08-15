from fastapi import FastAPI 
from pydantic import BaseModel 
from typing import List
from app.recommender import recommend_tracks
from app.enhanced_recommender import (
    recommend_tracks_enhanced,
)

app = FastAPI( 
    title="NextTrack API", 
    description="A diversity-aware music recommendation API.", 
    version="0.1.0" 
) 

class RecommendationRequest(BaseModel):
    recent_tracks: list[str]
    exploration_level: float = 0.3

    preferred_genres: list[str] | None = None
    preferred_artists: list[str] | None = None
    preference_strength: float = 0.0

@app.get("/") 
def read_root():
     return {"message": "NextTrack API is running"}

@app.post("/recommend")
def recommend(request: RecommendationRequest):
    recommendations = recommend_tracks_enhanced(
    recent_tracks=request.recent_tracks,
    exploration_level=request.exploration_level,
    preferred_genres=request.preferred_genres,
    preferred_artists=request.preferred_artists,
    preference_strength=request.preference_strength,
)

    return {
        "recent_tracks": request.recent_tracks,
        "exploration_level": request.exploration_level,
        "recommendations": recommendations
    }

