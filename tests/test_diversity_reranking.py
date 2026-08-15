import numpy as np
import pytest

from app.diversity_reranking import (
    calculate_list_redundancy,
    calculate_track_redundancy,
    rerank_for_diversity,
)


def make_candidate(
    track_id: str,
    relevance: float,
    genre: str,
    artist: str,
    vector: list[float],
) -> dict:
    return {
        "track_id": track_id,
        "relevance_score": relevance,
        "track_genre": genre,
        "artists": artist,
        "audio_vector": np.asarray(
            vector,
            dtype=float,
        ),
    }


def test_identical_tracks_have_high_redundancy():
    first = make_candidate(
        "1",
        0.9,
        "rock",
        "Artist A",
        [1.0, 0.0],
    )

    second = make_candidate(
        "2",
        0.8,
        "rock",
        "Artist A",
        [1.0, 0.0],
    )

    redundancy = (
        calculate_track_redundancy(
            first,
            second,
        )
    )

    assert redundancy == pytest.approx(
        1.0
    )


def test_different_tracks_have_lower_redundancy():
    first = make_candidate(
        "1",
        0.9,
        "rock",
        "Artist A",
        [1.0, 0.0],
    )

    second = make_candidate(
        "2",
        0.8,
        "jazz",
        "Artist B",
        [0.0, 1.0],
    )

    redundancy = (
        calculate_track_redundancy(
            first,
            second,
        )
    )

    assert redundancy < 0.5


def test_empty_selected_list_has_zero_redundancy():
    candidate = make_candidate(
        "1",
        0.9,
        "rock",
        "Artist A",
        [1.0, 0.0],
    )

    assert (
        calculate_list_redundancy(
            candidate,
            [],
        )
        == 0.0
    )


def test_list_redundancy_uses_maximum_pair():
    candidate = make_candidate(
        "1",
        0.8,
        "rock",
        "Artist A",
        [1.0, 0.0],
    )

    similar = make_candidate(
        "2",
        0.9,
        "rock",
        "Artist A",
        [1.0, 0.0],
    )

    different = make_candidate(
        "3",
        0.9,
        "jazz",
        "Artist B",
        [0.0, 1.0],
    )

    redundancy = (
        calculate_list_redundancy(
            candidate,
            [
                different,
                similar,
            ],
        )
    )

    assert redundancy == pytest.approx(
        1.0
    )


def test_zero_exploration_preserves_relevance_order():
    candidates = [
        make_candidate(
            "1",
            0.90,
            "rock",
            "Artist A",
            [1.0, 0.0],
        ),
        make_candidate(
            "2",
            0.80,
            "rock",
            "Artist A",
            [1.0, 0.0],
        ),
        make_candidate(
            "3",
            0.70,
            "jazz",
            "Artist B",
            [0.0, 1.0],
        ),
    ]

    results = rerank_for_diversity(
        candidates,
        exploration_level=0.0,
        limit=3,
    )

    assert [
        result["track_id"]
        for result in results
    ] == [
        "1",
        "2",
        "3",
    ]


def test_high_exploration_can_promote_less_redundant_track():
    candidates = [
        make_candidate(
            "1",
            0.90,
            "rock",
            "Artist A",
            [1.0, 0.0],
        ),
        make_candidate(
            "2",
            0.88,
            "rock",
            "Artist A",
            [1.0, 0.0],
        ),
        make_candidate(
            "3",
            0.82,
            "jazz",
            "Artist B",
            [0.0, 1.0],
        ),
    ]

    results = rerank_for_diversity(
        candidates,
        exploration_level=1.0,
        limit=3,
    )

    assert results[0]["track_id"] == "1"

    assert results[1]["track_id"] == "3"


def test_reranking_respects_limit():
    candidates = [
        make_candidate(
            str(index),
            1.0 - index * 0.1,
            "rock",
            f"Artist {index}",
            [1.0, float(index)],
        )
        for index in range(5)
    ]

    results = rerank_for_diversity(
        candidates,
        exploration_level=0.5,
        limit=3,
    )

    assert len(results) == 3


def test_reranking_returns_unique_tracks():
    candidates = [
        make_candidate(
            str(index),
            1.0 - index * 0.1,
            "rock",
            f"Artist {index}",
            [1.0, float(index)],
        )
        for index in range(5)
    ]

    results = rerank_for_diversity(
        candidates,
        exploration_level=1.0,
        limit=5,
    )

    track_ids = [
        result["track_id"]
        for result in results
    ]

    assert len(track_ids) == len(
        set(track_ids)
    )


def test_negative_limit_is_rejected():
    with pytest.raises(
        ValueError,
        match="limit must be at least 1",
    ):
        rerank_for_diversity(
            [],
            exploration_level=0.5,
            limit=-1,
        )


def test_exploration_is_clamped():
    candidates = [
        make_candidate(
            "1",
            0.90,
            "rock",
            "Artist A",
            [1.0, 0.0],
        ),
        make_candidate(
            "2",
            0.88,
            "rock",
            "Artist A",
            [1.0, 0.0],
        ),
        make_candidate(
            "3",
            0.82,
            "jazz",
            "Artist B",
            [0.0, 1.0],
        ),
    ]

    above_one = rerank_for_diversity(
        candidates,
        exploration_level=2.0,
        limit=3,
    )

    one = rerank_for_diversity(
        candidates,
        exploration_level=1.0,
        limit=3,
    )

    assert [
        result["track_id"]
        for result in above_one
    ] == [
        result["track_id"]
        for result in one
    ]

def test_incremental_reranker_is_deterministic():
    candidates = [
        make_candidate(
            "1",
            0.95,
            "rock",
            "Artist A",
            [1.0, 0.0],
        ),
        make_candidate(
            "2",
            0.90,
            "rock",
            "Artist B",
            [0.9, 0.1],
        ),
        make_candidate(
            "3",
            0.85,
            "jazz",
            "Artist C",
            [0.0, 1.0],
        ),
        make_candidate(
            "4",
            0.80,
            "electronic",
            "Artist D",
            [0.2, 0.8],
        ),
    ]

    first = rerank_for_diversity(
        candidates=candidates,
        exploration_level=0.75,
        limit=4,
    )

    second = rerank_for_diversity(
        candidates=candidates,
        exploration_level=0.75,
        limit=4,
    )

    assert [
        item["track_id"]
        for item in first
    ] == [
        item["track_id"]
        for item in second
    ]