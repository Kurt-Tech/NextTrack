import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.recommender import recommend_tracks

recent_tracks = [
    "5SuOikwiRyPMVoIQDJUgSV",
    "4qPNDBW1i3p13qLCt0Ki3A",
    "1iJBSr7s7jYXzM8EGcbK5b"
]

results = recommend_tracks(recent_tracks, limit=5)

for track in results:
    print(
        track["track_id"],
        "-",
        track["track_name"],
        "-",
        track["artists"],
        "-",
        track["track_genre"],
        "- Score:",
        track["score"]
    )
