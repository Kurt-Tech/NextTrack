import pandas as pd
import pytest

from app.candidate_pool import (
    build_candidate_pool,
)


def make_candidates(
    primary_count: int = 600,
    alternative_count: int = 400,
) -> pd.DataFrame:
    rows = []

    score = 1.0

    for index in range(
        primary_count
    ):
        rows.append(
            {
                "track_id": (
                    f"primary-{index}"
                ),
                "track_genre": "rock",
                "relevance_score": score,
            }
        )

        score -= 0.0001

    alternative_genres = [
        "jazz",
        "country",
        "electronic",
        "classical",
        "pop",
    ]

    for index in range(
        alternative_count
    ):
        rows.append(
            {
                "track_id": (
                    f"alternative-{index}"
                ),
                "track_genre": (
                    alternative_genres[
                        index
                        % len(
                            alternative_genres
                        )
                    ]
                ),
                "relevance_score": score,
            }
        )

        score -= 0.0001

    return pd.DataFrame(
        rows
    )


def test_zero_exploration_preserves_relevance_pool():
    candidates = (
        make_candidates()
    )

    pool = build_candidate_pool(
        candidates=candidates,
        primary_genre="rock",
        exploration_level=0.0,
        limit=10,
    )

    expected = (
        candidates
        .sort_values(
            by="relevance_score",
            ascending=False,
        )
        .head(500)
    )

    assert (
        pool["track_id"].tolist()
        ==
        expected[
            "track_id"
        ].tolist()
    )


def test_candidate_pool_has_expected_size():
    candidates = (
        make_candidates()
    )

    pool = build_candidate_pool(
        candidates=candidates,
        primary_genre="rock",
        exploration_level=1.0,
        limit=10,
    )

    assert len(pool) == 500


def test_high_exploration_adds_alternative_genres():
    candidates = (
        make_candidates()
    )

    pool = build_candidate_pool(
        candidates=candidates,
        primary_genre="rock",
        exploration_level=1.0,
        limit=10,
    )

    alternative_count = (
        pool[
            pool["track_genre"]
            != "rock"
        ]
        .shape[0]
    )

    assert alternative_count > 0


def test_more_exploration_adds_more_alternatives():
    candidates = (
        make_candidates()
    )

    low = build_candidate_pool(
        candidates=candidates,
        primary_genre="rock",
        exploration_level=0.25,
        limit=10,
    )

    high = build_candidate_pool(
        candidates=candidates,
        primary_genre="rock",
        exploration_level=1.0,
        limit=10,
    )

    low_alternatives = (
        low[
            low["track_genre"]
            != "rock"
        ]
        .shape[0]
    )

    high_alternatives = (
        high[
            high["track_genre"]
            != "rock"
        ]
        .shape[0]
    )

    assert (
        high_alternatives
        > low_alternatives
    )


def test_diversity_reserve_contains_multiple_genres():
    candidates = (
        make_candidates()
    )

    pool = build_candidate_pool(
        candidates=candidates,
        primary_genre="rock",
        exploration_level=1.0,
        limit=10,
    )

    alternative_genres = set(
        pool.loc[
            pool[
                "track_genre"
            ]
            != "rock",
            "track_genre",
        ]
    )

    assert len(
        alternative_genres
    ) > 1


def test_candidate_pool_has_unique_tracks():
    candidates = (
        make_candidates()
    )

    pool = build_candidate_pool(
        candidates=candidates,
        primary_genre="rock",
        exploration_level=1.0,
        limit=10,
    )

    assert (
        pool["track_id"].nunique()
        ==
        len(pool)
    )


def test_exploration_above_one_is_clamped():
    candidates = (
        make_candidates()
    )

    one = build_candidate_pool(
        candidates=candidates,
        primary_genre="rock",
        exploration_level=1.0,
        limit=10,
    )

    above_one = (
        build_candidate_pool(
            candidates=candidates,
            primary_genre="rock",
            exploration_level=2.0,
            limit=10,
        )
    )

    assert (
        one["track_id"].tolist()
        ==
        above_one[
            "track_id"
        ].tolist()
    )


def test_negative_exploration_is_clamped():
    candidates = (
        make_candidates()
    )

    zero = build_candidate_pool(
        candidates=candidates,
        primary_genre="rock",
        exploration_level=0.0,
        limit=10,
    )

    negative = (
        build_candidate_pool(
            candidates=candidates,
            primary_genre="rock",
            exploration_level=-1.0,
            limit=10,
        )
    )

    assert (
        zero["track_id"].tolist()
        ==
        negative[
            "track_id"
        ].tolist()
    )


def test_negative_limit_is_rejected():
    candidates = (
        make_candidates()
    )

    with pytest.raises(
        ValueError,
        match="limit must be at least 1",
    ):
        build_candidate_pool(
            candidates=candidates,
            primary_genre="rock",
            exploration_level=0.5,
            limit=-1,
        )