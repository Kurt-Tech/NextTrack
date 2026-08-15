import numpy as np

from app.audio_similarity import (
    calculate_cosine_similarity,
)
from app.diversity_scoring import (
    calculate_pair_redundancy,
    calculate_selection_score,
)


def _artist_names(
    artists: str,
) -> set[str]:
    """
    Convert a semicolon-separated artist field into
    normalized artist names.
    """

    return {
        artist.strip().lower()
        for artist in str(
            artists
        ).split(";")
        if artist.strip()
    }


def calculate_track_redundancy(
    candidate: dict,
    selected_track: dict,
) -> float:
    """
    Calculate continuous redundancy between two
    recommendation candidates.
    """

    candidate_vector = np.asarray(
        candidate[
            "audio_vector"
        ],
        dtype=float,
    )

    selected_vector = np.asarray(
        selected_track[
            "audio_vector"
        ],
        dtype=float,
    )

    audio_similarity = float(
        calculate_cosine_similarity(
            candidate_vector,
            np.asarray(
                [
                    selected_vector
                ],
                dtype=float,
            ),
        )[0]
    )

    same_genre = (
        str(
            candidate[
                "track_genre"
            ]
        )
        .strip()
        .lower()
        ==
        str(
            selected_track[
                "track_genre"
            ]
        )
        .strip()
        .lower()
    )

    candidate_artists = (
        _artist_names(
            candidate[
                "artists"
            ]
        )
    )

    selected_artists = (
        _artist_names(
            selected_track[
                "artists"
            ]
        )
    )

    shared_artist = bool(
        candidate_artists
        & selected_artists
    )

    return calculate_pair_redundancy(
        audio_similarity=(
            audio_similarity
        ),
        same_genre=(
            same_genre
        ),
        shared_artist=(
            shared_artist
        ),
    )


def calculate_list_redundancy(
    candidate: dict,
    selected: list[dict],
) -> float:
    """
    Calculate redundancy against the selected list.

    This function remains available for testing,
    diagnostics and external use.

    The optimized reranker itself maintains the same
    maximum redundancy incrementally instead of
    recalculating every previous pair.
    """

    if not selected:
        return 0.0

    redundancies = [
        calculate_track_redundancy(
            candidate,
            selected_track,
        )
        for selected_track
        in selected
    ]

    return max(
        redundancies
    )


def rerank_for_diversity(
    candidates: list[dict],
    exploration_level: float,
    limit: int,
    maximum_diversity_weight: float = 0.35,
) -> list[dict]:
    """
    Greedily rerank candidates using relevance and
    continuous list redundancy.

    Optimization
    ------------
    Rather than recalculating a candidate's redundancy
    against every previously selected item at every
    iteration, maintain the maximum redundancy observed
    so far.

    When a new recommendation is selected, each remaining
    candidate is compared only with that newly selected
    track.

    Because list redundancy is defined as:

        max(
            pair_redundancy(
                candidate,
                selected_track,
            )
        )

    this incremental update is mathematically equivalent
    to recalculating the full selected list.

    At exploration level zero, ranking remains entirely
    determined by relevance.
    """

    if limit < 1:
        raise ValueError(
            "limit must be at least 1"
        )

    if not candidates:
        return []

    exploration_level = max(
        0.0,
        min(
            1.0,
            exploration_level,
        ),
    )

    remaining = [
        candidate.copy()
        for candidate
        in candidates
    ]

    selected = []

    # -----------------------------------------------------
    # Incremental redundancy cache.
    #
    # Before anything has been selected, every candidate
    # has zero redundancy against the recommendation list.
    # -----------------------------------------------------

    maximum_redundancy = {
        candidate["track_id"]: 0.0
        for candidate
        in remaining
    }

    while (
        remaining
        and len(selected) < limit
    ):
        best_candidate = None
        best_selection_score = None
        best_redundancy = None

        # -------------------------------------------------
        # Select the best candidate using its cached
        # maximum redundancy against the current list.
        # -------------------------------------------------

        for candidate in remaining:
            redundancy = float(
                maximum_redundancy[
                    candidate[
                        "track_id"
                    ]
                ]
            )

            selection_score = (
                calculate_selection_score(
                    relevance_score=float(
                        candidate[
                            "relevance_score"
                        ]
                    ),
                    redundancy_score=(
                        redundancy
                    ),
                    exploration_level=(
                        exploration_level
                    ),
                    maximum_diversity_weight=(
                        maximum_diversity_weight
                    ),
                )
            )

            # Strict greater-than preserves the original
            # first-encountered tie behaviour.
            if (
                best_candidate is None
                or selection_score
                > best_selection_score
            ):
                best_candidate = (
                    candidate
                )

                best_selection_score = (
                    selection_score
                )

                best_redundancy = (
                    redundancy
                )

        chosen = (
            best_candidate.copy()
        )

        chosen[
            "diversity_selection_score"
        ] = float(
            best_selection_score
        )

        chosen[
            "redundancy_score"
        ] = float(
            best_redundancy
        )

        selected.append(
            chosen
        )

        # -------------------------------------------------
        # Remove the selected candidate.
        # -------------------------------------------------

        selected_track_id = (
            best_candidate[
                "track_id"
            ]
        )

        remaining = [
            candidate
            for candidate
            in remaining
            if candidate[
                "track_id"
            ]
            != selected_track_id
        ]

        # -------------------------------------------------
        # Update each remaining candidate using only the
        # newly selected track.
        #
        # Previous pairwise redundancy values do not need
        # to be recomputed.
        # -------------------------------------------------

        for candidate in remaining:
            track_id = (
                candidate[
                    "track_id"
                ]
            )

            pair_redundancy = (
                calculate_track_redundancy(
                    candidate,
                    best_candidate,
                )
            )

            maximum_redundancy[
                track_id
            ] = max(
                float(
                    maximum_redundancy[
                        track_id
                    ]
                ),
                float(
                    pair_redundancy
                ),
            )

    return selected