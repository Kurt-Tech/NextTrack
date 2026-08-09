def _artist_names(artists: str) -> set[str]:
    return {
        artist.strip().lower()
        for artist in str(artists).split(";")
        if artist.strip()
    }


def rerank_candidates(
    candidates: list[dict],
    exploration_level: float,
    limit: int,
) -> list[dict]:
    """
    Greedily rerank candidates by balancing relevance with
    diversity relative to tracks already selected.

    Exploration controls the diversity contribution, while
    relevance remains the majority component at all levels.
    """
    if limit < 1:
        raise ValueError("limit must be at least 1")

    if not candidates:
        return []

    exploration_level = max(
        0.0,
        min(1.0, exploration_level),
    )

    # At maximum exploration, relevance still contributes 55%.
    diversity_weight = (
        0.45 * exploration_level
    )

    relevance_weight = (
        1.0 - diversity_weight
    )

    remaining = [
        candidate.copy()
        for candidate in candidates
    ]

    selected = []
    selected_genres = set()
    selected_artists = set()

    while (
        remaining
        and len(selected) < limit
    ):
        best_candidate = None
        best_selection_score = None

        for candidate in remaining:
            if not selected:
                list_diversity = 0.0

            else:
                candidate_artists = (
                    _artist_names(
                        candidate["artists"]
                    )
                )

                genre_novelty = (
                    0.0
                    if candidate["track_genre"]
                    in selected_genres
                    else 1.0
                )

                artist_novelty = (
                    1.0
                    if candidate_artists.isdisjoint(
                        selected_artists
                    )
                    else 0.0
                )

                list_diversity = (
                    0.6 * genre_novelty
                    + 0.4 * artist_novelty
                )

            selection_score = (
                relevance_weight
                * candidate["relevance_score"]
                + diversity_weight
                * list_diversity
            )

            if (
                best_selection_score is None
                or selection_score
                > best_selection_score
            ):
                best_candidate = candidate
                best_selection_score = (
                    selection_score
                )

        best_candidate = (
            best_candidate.copy()
        )

        best_candidate["score"] = round(
            best_selection_score,
            4,
        )

        selected.append(
            best_candidate
        )

        selected_genres.add(
            best_candidate["track_genre"]
        )

        selected_artists.update(
            _artist_names(
                best_candidate["artists"]
            )
        )

        remaining.remove(
            next(
                candidate
                for candidate in remaining
                if candidate["track_id"]
                == best_candidate["track_id"]
            )
        )

    return selected