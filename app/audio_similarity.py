from functools import lru_cache

import numpy as np
import pandas as pd

from app.metadata import load_tracks


AUDIO_FEATURES = [
    "danceability",
    "energy",
    "loudness",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
]


@lru_cache(maxsize=1)
def get_normalized_audio_features() -> pd.DataFrame:
    """
    Return the audio features for every track after z-score
    standardization.

    The returned DataFrame uses track_id as its index.
    """
    df = load_tracks()

    features = (
        df[AUDIO_FEATURES]
        .astype(float)
        .copy()
    )

    means = features.mean()
    standard_deviations = features.std(ddof=0)

    # Defensive handling in case a future dataset contains
    # a feature with no variation.
    standard_deviations = standard_deviations.replace(0, 1)

    normalized = (
        features - means
    ) / standard_deviations

    normalized.index = df["track_id"]

    return normalized


def build_context_vector(
    recent_tracks: list[str],
) -> np.ndarray | None:
    """
    Build an audio representation of the user's recent
    listening context.

    Unknown track IDs are ignored. If no valid tracks remain,
    None is returned.
    """
    normalized = get_normalized_audio_features()

    valid_track_ids = [
        track_id
        for track_id in recent_tracks
        if track_id in normalized.index
    ]

    if not valid_track_ids:
        return None

    recent_features = normalized.loc[
        valid_track_ids
    ]

    context_vector = (
        recent_features
        .mean(axis=0)
        .to_numpy(dtype=float)
    )

    return context_vector


def calculate_cosine_similarity(
    context_vector: np.ndarray,
    candidate_vectors: np.ndarray,
) -> np.ndarray:
    """
    Calculate cosine similarity between one context vector
    and multiple candidate vectors.

    The raw cosine range [-1, 1] is converted to [0, 1]
    to simplify later hybrid scoring.
    """
    context_vector = np.asarray(
        context_vector,
        dtype=float,
    )

    candidate_vectors = np.asarray(
        candidate_vectors,
        dtype=float,
    )

    context_norm = np.linalg.norm(context_vector)

    candidate_norms = np.linalg.norm(
        candidate_vectors,
        axis=1,
    )

    denominators = (
        candidate_norms * context_norm
    )

    raw_similarity = np.divide(
        candidate_vectors @ context_vector,
        denominators,
        out=np.zeros(
            candidate_vectors.shape[0],
            dtype=float,
        ),
        where=denominators != 0,
    )

    normalized_similarity = (
        raw_similarity + 1.0
    ) / 2.0

    return np.clip(
        normalized_similarity,
        0.0,
        1.0,
    )