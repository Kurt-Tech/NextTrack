from collections import Counter

import numpy as np

from app.audio_similarity import (
    calculate_cosine_similarity,
    get_normalized_audio_features,
)
from app.metadata import get_track, load_tracks

from app.preference_scoring import (
    apply_preference_weight,
    calculate_preference_score,
)


def _artist_names(artists: str) -> set[str]:
    return {
        artist.strip().lower()
        for artist in str(artists).split(";")
        if artist.strip()
    }


def _get_primary_genre(genres: list[str]) -> str:
    return Counter(genres).most_common(1)[0][0]


def recommend_tracks_enhanced(
    recent_tracks: list[str],
    exploration_level: float = 0.3,
    limit: int = 10,
    preferred_genres: list[str] | None = None,
    preferred_artists: list[str] | None = None,
    preference_strength: float = 0.0,
) -> list[dict]:
    if limit < 1:
        raise ValueError("limit must be at least 1")

    exploration_level = max(
        0.0,
        min(1.0, exploration_level),
    )

    preference_strength = max(
        0.0,
        min(1.0, preference_strength),
    )

    has_genre_preferences = any(
        str(genre).strip()
        for genre in (preferred_genres or [])
    )

    has_artist_preferences = any(
        str(artist).strip()
        for artist in (preferred_artists or [])
    )

    has_preferences = (
        has_genre_preferences
        or has_artist_preferences
    )

    preference_active = (
        has_preferences
        and preference_strength > 0.0
    )   

    df = load_tracks()

    recent_track_data = []

    for track_id in recent_tracks:
        track = get_track(track_id)

        if track is not None:
            recent_track_data.append(track)

    if not recent_track_data:
        return []

    valid_recent_ids = [
        track["track_id"]
        for track in recent_track_data
    ]

    recent_genres = [
        track["track_genre"]
        for track in recent_track_data
    ]

    recent_genres_set = set(recent_genres)

    primary_genre = _get_primary_genre(
        recent_genres
    )

    recent_artist_names = set()

    for track in recent_track_data:
        recent_artist_names.update(
            _artist_names(track["artists"])
        )

    normalized_features = (
        get_normalized_audio_features()
    )

    recent_feature_vectors = (
        normalized_features
        .loc[valid_recent_ids]
    )

    context_vector = (
        recent_feature_vectors
        .mean(axis=0)
        .to_numpy(dtype=float)
    )

    candidates = df[
        ~df["track_id"].isin(valid_recent_ids)
    ].copy()

    candidate_vectors = (
        normalized_features
        .loc[candidates["track_id"]]
        .to_numpy(dtype=float)
    )

    candidates["audio_similarity"] = (
        calculate_cosine_similarity(
            context_vector,
            candidate_vectors,
        )
    )

    candidates["popularity_score"] = (
        candidates["popularity"]
        .fillna(0)
        / 100
    )

    candidates["genre_match"] = (
        candidates["track_genre"]
        .apply(
            lambda genre:
            1.0
            if genre == primary_genre
            else 0.65
            if genre in recent_genres_set
            else 0.0
        )
    )

    candidates["artist_match"] = (
        candidates["artists"]
        .apply(
            lambda artists:
            1.0
            if _artist_names(artists)
            & recent_artist_names
            else 0.0
        )
    )

    candidates["familiarity_score"] = (
        0.7 * candidates["genre_match"]
        + 0.3 * candidates["artist_match"]
    )

    candidates["diversity_score"] = (
        0.6 * (1 - candidates["genre_match"])
        + 0.4 * (1 - candidates["artist_match"])
    )

    candidates["contextual_relevance_score"] = (
        0.60 * candidates["audio_similarity"]
        + 0.25 * candidates["familiarity_score"]
        + 0.15 * candidates["popularity_score"]
    )

    if preference_active:
        candidates["preference_score"] = [
            calculate_preference_score(
                track_genre=genre,
                artists=artists,
                preferred_genres=preferred_genres,
                preferred_artists=preferred_artists,
            )
            for genre, artists in zip(
                candidates["track_genre"],
                candidates["artists"],
            )
        ]

        candidates["relevance_score"] = (
            apply_preference_weight(
                contextual_relevance=(
                    candidates[
                        "contextual_relevance_score"
                    ]
                ),
                preference_score=(
                    candidates["preference_score"]
                ),
                preference_strength=preference_strength,
                has_preferences=True,
            )
        )

    else:
        candidates["preference_score"] = 0.0

        candidates["relevance_score"] = (
            candidates[
                "contextual_relevance_score"
            ]
        )

    candidates["score"] = (
        (1 - exploration_level)
        * candidates["relevance_score"]
        + exploration_level
        * (
            0.65 * candidates["relevance_score"]
            + 0.35 * candidates["diversity_score"]
        )
    )

    candidates = candidates.sort_values(
        by="score",
        ascending=False,
    )

    selected = []
    selected_genres = set()
    selected_artists = set()

    candidate_pool_size = max(
        limit * 50,
        100,
    )

    for _, candidate in (
        candidates
        .head(candidate_pool_size)
        .iterrows()
    ):
        candidate_artists = _artist_names(
            candidate["artists"]
        )

        genre_repeat = (
            candidate["track_genre"]
            in selected_genres
        )

        artist_repeat = bool(
            candidate_artists
            & selected_artists
        )

        repeat_penalty = (
            exploration_level
            * (
                0.05 * genre_repeat
                + 0.10 * artist_repeat
            )
        )

        candidate = candidate.copy()

        candidate["score"] = round(
            candidate["score"]
            - repeat_penalty,
            4,
        )

        selected.append(candidate)

        selected_genres.add(
            candidate["track_genre"]
        )

        selected_artists.update(
            candidate_artists
        )

    selected = sorted(
        selected,
        key=lambda track: track["score"],
        reverse=True,
    )

    response_columns = [
        "track_id",
        "track_name",
        "artists",
        "album_name",
        "track_genre",
        "popularity",
        "audio_similarity",
        "score",
    ]

    return [
        {
            column: (
                float(track[column])
                if column in {
                    "audio_similarity",
                    "score",
                }
                else track[column]
            )
            for column in response_columns
        }
        for track in selected[:limit]
    ]