from fastapi import FastAPI 
from pydantic import BaseModel 
from typing import List

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
    return { 
        "recent_tracks": request.recent_tracks, 
        "exploration_level": request.exploration_level, 
        "recommendations": [ 
            { 
                "track_id": 
                "track_001", "title": "Placeholder Track", 
                "artist": "Placeholder Artist", 
                "score": 0.85 
            } 
        ] 
    }

