import pytest

from experiments.reranking.reranking import (
    rerank_candidates,
)


CANDIDATES = [
    {
        "track_id": "track-a",
        "artists": "Artist A",
        "track_genre": "rock",
        "relevance_score": 0.95,
    },
    {
        "track_id": "track-b",
        "artists": "Artist A",
        "track_genre": "rock",
        "relevance_score": 0.94,
    },
    {
        "track_id": "track-c",
        "artists": "Artist B",
        "track_genre": "jazz",
        "relevance_score": 0.90,
    },
]


def test_zero_exploration_preserves_relevance_order():
    results = rerank_candidates(
        CANDIDATES,
        exploration_level=0.0,
        limit=3,
    )

    assert [
        track["track_id"]
        for track in results
    ] == [
        "track-a",
        "track-b",
        "track-c",
    ]


def test_high_exploration_promotes_diverse_candidate():
    results = rerank_candidates(
        CANDIDATES,
        exploration_level=1.0,
        limit=2,
    )

    assert results[0]["track_id"] == "track-a"
    assert results[1]["track_id"] == "track-c"


def test_reranking_returns_requested_limit():
    results = rerank_candidates(
        CANDIDATES,
        exploration_level=0.5,
        limit=2,
    )

    assert len(results) == 2


def test_negative_limit_is_rejected():
    with pytest.raises(
        ValueError,
        match="limit must be at least 1",
    ):
        rerank_candidates(
            CANDIDATES,
            exploration_level=0.5,
            limit=-1,
        )


def test_empty_candidates_return_empty_list():
    results = rerank_candidates(
        [],
        exploration_level=0.5,
        limit=5,
    )

    assert results == []


def test_exploration_below_zero_is_clamped():
    below_zero = rerank_candidates(
        CANDIDATES,
        exploration_level=-1.0,
        limit=3,
    )

    zero = rerank_candidates(
        CANDIDATES,
        exploration_level=0.0,
        limit=3,
    )

    assert below_zero == zero


def test_exploration_above_one_is_clamped():
    above_one = rerank_candidates(
        CANDIDATES,
        exploration_level=2.0,
        limit=3,
    )

    one = rerank_candidates(
        CANDIDATES,
        exploration_level=1.0,
        limit=3,
    )

    assert above_one == one