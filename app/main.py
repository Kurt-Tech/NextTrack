from fastapi import FastAPI, HTTPException
from pydantic import BaseModel 
from typing import List
from app.recommender import recommend_tracks
from app.enhanced_recommender import (
    recommend_tracks_enhanced,
)
from app.evaluation_contexts import EVALUATION_CONTEXTS
from app.metadata import get_track

from pathlib import Path

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI( 
    title="NextTrack API", 
    description="A diversity-aware music recommendation API.", 
    version="0.1.0" 
) 

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)

@app.get(
    "/evaluation",
    include_in_schema=False,
)
def evaluation_page():
    """Serve the participant evaluation interface."""

    return FileResponse(
        STATIC_DIR / "evaluation.html"
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

@app.get("/evaluation/contexts")
def get_evaluation_contexts():
    """Return predefined listening contexts for the evaluation interface."""

    contexts = []

    for context_id, context in EVALUATION_CONTEXTS.items():
        recent_tracks = []

        for track_id in context["recent_tracks"]:
            track = get_track(track_id)

            if track is None:
                raise HTTPException(
                    status_code=500,
                    detail=(
                        "Configured evaluation track "
                        f"not found: {track_id}"
                    ),
                )

            recent_tracks.append(
                {
                    "track_id": str(track["track_id"]),
                    "track_name": str(track["track_name"]),
                    "artists": str(track["artists"]),
                    "track_genre": str(track["track_genre"]),
                }
            )

        contexts.append(
            {
                "id": context_id,
                "name": context["name"],
                "recent_tracks": recent_tracks,
            }
        )

    return {"contexts": contexts}

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

