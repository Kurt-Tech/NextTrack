from app.recommender import recommend_tracks

from app.recommender import (
    _get_primary_genre,
    recommend_tracks,
)

RECENT_TRACKS = [
    "5SuOikwiRyPMVoIQDJUgSV",
    "4qPNDBW1i3p13qLCt0Ki3A",
    "1iJBSr7s7jYXzM8EGcbK5b",
]


def test_recommender_returns_requested_number_of_tracks():
    results = recommend_tracks(
        RECENT_TRACKS,
        exploration_level=0.3,
        limit=5,
    )

    assert len(results) == 5


def test_recommender_excludes_recent_tracks():
    results = recommend_tracks(
        RECENT_TRACKS,
        exploration_level=0.3,
        limit=10,
    )

    recommended_ids = {
        track["track_id"]
        for track in results
    }

    assert recommended_ids.isdisjoint(RECENT_TRACKS)


def test_recommender_returns_unique_tracks():
    results = recommend_tracks(
        RECENT_TRACKS,
        exploration_level=0.3,
        limit=10,
    )

    track_ids = [
        track["track_id"]
        for track in results
    ]

    assert len(track_ids) == len(set(track_ids))


def test_recommender_returns_expected_fields():
    results = recommend_tracks(
        RECENT_TRACKS,
        exploration_level=0.3,
        limit=5,
    )

    required_fields = {
        "track_id",
        "track_name",
        "artists",
        "album_name",
        "track_genre",
        "popularity",
        "score",
    }

    assert results

    for track in results:
        assert required_fields.issubset(track.keys())


def test_recommendations_are_sorted_by_score():
    results = recommend_tracks(
        RECENT_TRACKS,
        exploration_level=0.3,
        limit=10,
    )

    scores = [
        track["score"]
        for track in results
    ]

    assert scores == sorted(scores, reverse=True)


def test_empty_recent_history_returns_no_recommendations():
    results = recommend_tracks(
        [],
        exploration_level=0.3,
        limit=5,
    )

    assert results == []


def test_unknown_track_ids_return_no_recommendations():
    results = recommend_tracks(
        ["not-a-real-track-id"],
        exploration_level=0.3,
        limit=5,
    )

    assert results == []


def test_unknown_track_ids_are_ignored_when_valid_tracks_exist():
    results = recommend_tracks(
        [
            "not-a-real-track-id",
            "5SuOikwiRyPMVoIQDJUgSV",
        ],
        exploration_level=0.3,
        limit=5,
    )

    assert len(results) == 5


def test_exploration_below_zero_is_clamped():
    below_zero = recommend_tracks(
        RECENT_TRACKS,
        exploration_level=-1.0,
        limit=5,
    )

    zero = recommend_tracks(
        RECENT_TRACKS,
        exploration_level=0.0,
        limit=5,
    )

    assert below_zero == zero


def test_exploration_above_one_is_clamped():
    above_one = recommend_tracks(
        RECENT_TRACKS,
        exploration_level=2.0,
        limit=5,
    )

    one = recommend_tracks(
        RECENT_TRACKS,
        exploration_level=1.0,
        limit=5,
    )

    assert above_one == one


def test_exploration_level_changes_recommendations():
    low_exploration = recommend_tracks(
        RECENT_TRACKS,
        exploration_level=0.0,
        limit=10,
    )

    high_exploration = recommend_tracks(
        RECENT_TRACKS,
        exploration_level=1.0,
        limit=10,
    )

    assert low_exploration != high_exploration

import pytest

def test_negative_limit_is_rejected():
    with pytest.raises(
        ValueError,
        match="limit must be at least 1"
    ):
        recommend_tracks(
            RECENT_TRACKS,
            exploration_level=0.3,
            limit=-5,
        )

def test_primary_genre_uses_most_frequent_genre():
    genres = [
        "rock",
        "acoustic",
        "rock",
        "jazz",
    ]

    assert _get_primary_genre(genres) == "rock"


def test_primary_genre_tie_uses_first_encountered_genre():
    genres = [
        "acoustic",
        "rock",
        "jazz",
    ]

    assert _get_primary_genre(genres) == "acoustic"