from pathlib import Path
from functools import lru_cache
import pandas as pd

DATA_PATH = Path(__file__).resolve().parent / "data" / "spotify_tracks_clean.csv"


@lru_cache(maxsize=1)
def load_tracks() -> pd.DataFrame:
    """Load the cleaned Spotify dataset once and reuse it."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    # Normalise useful text fields
    for col in ["track_id", "track_name", "artists", "album_name", "track_genre"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    df["track_genre"] = df["track_genre"].str.lower()

    # Search helper column
    df["search_text"] = (
        df["track_name"].fillna("")
        + " "
        + df["artists"].fillna("")
        + " "
        + df["track_genre"].fillna("")
    ).str.lower()

    return df


def get_track(track_id: str) -> dict | None:
    """Return one track by track_id."""
    df = load_tracks()
    result = df[df["track_id"] == track_id]

    if result.empty:
        return None

    return result.iloc[0].to_dict()


def get_tracks_by_genre(genre: str, limit: int = 20) -> list[dict]:
    """Return tracks matching a genre."""
    df = load_tracks()
    genre = genre.strip().lower()

    results = df[df["track_genre"] == genre]

    return results.head(limit).to_dict(orient="records")


def get_tracks_by_artist(artist: str, limit: int = 20) -> list[dict]:
    """Return tracks by artist name."""
    df = load_tracks()
    artist = artist.strip().lower()

    results = df[df["artists"].str.lower().str.contains(artist, na=False)]

    return results.head(limit).to_dict(orient="records")


def search_tracks(query: str, limit: int = 20) -> list[dict]:
    """Search tracks by title, artist, or genre."""
    df = load_tracks()
    query = query.strip().lower()

    results = df[df["search_text"].str.contains(query, na=False)]

    return results.head(limit).to_dict(orient="records")


def get_random_tracks(limit: int = 10) -> list[dict]:
    """Return random tracks from the dataset."""
    df = load_tracks()

    limit = min(limit, len(df))

    return df.sample(limit).to_dict(orient="records")


def get_all_genres() -> list[str]:
    """Return all unique genres."""
    df = load_tracks()

    return sorted(df["track_genre"].dropna().unique().tolist())


def get_dataset_summary() -> dict:
    """Return basic dataset information."""
    df = load_tracks()

    return {
        "total_tracks": len(df),
        "total_genres": df["track_genre"].nunique(),
        "total_artists": df["artists"].nunique(),
        "columns": list(df.columns),
    }