import numpy as np

from app.audio_similarity import (
    calculate_cosine_similarity,
    get_normalized_audio_features,
)


def calculate_mean_audio_similarity(
    recent_tracks: list[str],
    recommendations: list[dict],
) -> float:
    """
    Calculate mean audio similarity between a listening-context
    vector and an arbitrary recommendation list.

    This function is independent of the recommender that produced
    the results, allowing fair comparison between algorithms.
    """
    normalized = get_normalized_audio_features()

    valid_recent_ids = [
        track_id
        for track_id in recent_tracks
        if track_id in normalized.index
    ]

    recommendation_ids = [
        track["track_id"]
        for track in recommendations
        if track["track_id"] in normalized.index
    ]

    if not valid_recent_ids or not recommendation_ids:
        return 0.0

    context_vector = (
        normalized
        .loc[valid_recent_ids]
        .mean(axis=0)
        .to_numpy(dtype=float)
    )

    candidate_vectors = (
        normalized
        .loc[recommendation_ids]
        .to_numpy(dtype=float)
    )

    similarities = calculate_cosine_similarity(
        context_vector,
        candidate_vectors,
    )

    return float(np.mean(similarities))


def calculate_genre_diversity(
    recommendations: list[dict],
) -> float:
    """
    Return the proportion of unique genres in the recommendation
    list. 1.0 means every recommendation has a different genre.
    """
    if not recommendations:
        return 0.0

    genres = {
        track["track_genre"]
        for track in recommendations
    }

    return len(genres) / len(recommendations)


def _artist_names(artists: str) -> set[str]:
    return {
        artist.strip().lower()
        for artist in str(artists).split(";")
        if artist.strip()
    }


def calculate_artist_diversity(
    recommendations: list[dict],
) -> float:
    """
    Calculate pairwise artist diversity.

    A pair receives a diversity score of 1 when the two
    recommendations share no artists and 0 when they share
    at least one artist.

    The final value is the mean across all recommendation
    pairs.
    """
    if len(recommendations) < 2:
        return 0.0

    artist_sets = [
        _artist_names(track["artists"])
        for track in recommendations
    ]

    diverse_pairs = 0
    total_pairs = 0

    for index, first_artists in enumerate(
        artist_sets
    ):
        for second_artists in artist_sets[
            index + 1:
        ]:
            total_pairs += 1

            if first_artists.isdisjoint(
                second_artists
            ):
                diverse_pairs += 1

    if total_pairs == 0:
        return 0.0

    return diverse_pairs / total_pairs


def calculate_mean_popularity(
    recommendations: list[dict],
) -> float:
    if not recommendations:
        return 0.0

    return float(
        np.mean([
            float(track["popularity"])
            for track in recommendations
        ])
    )