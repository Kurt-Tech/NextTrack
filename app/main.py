from fastapi import FastAPI 
from pydantic import BaseModel 
from typing import List
from app.recommender import recommend_tracks

app = FastAPI( 
    title="NextTrack API", 
    description="A diversity-aware music recommendation API.", 
    version="0.1.0" 
) 

class RecommendationRequest(BaseModel): 
    recent_tracks: List[str] 
    exploration_level: float = 0.3

@app.get("/") 
def read_root():
     return {"message": "NextTrack API is running"}

@app.post("/recommend")
def recommend(request: RecommendationRequest):
    recommendations = recommend_tracks(
        recent_tracks=request.recent_tracks,
        exploration_level=request.exploration_level,
        limit=10
    )

    return {
        "recent_tracks": request.recent_tracks,
        "exploration_level": request.exploration_level,
        "recommendations": recommendations
    }

