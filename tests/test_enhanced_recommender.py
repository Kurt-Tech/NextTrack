from app.enhanced_recommender import (
    recommend_tracks_enhanced,
)


RECENT_TRACKS = [
    "5SuOikwiRyPMVoIQDJUgSV",
    "4qPNDBW1i3p13qLCt0Ki3A",
    "1iJBSr7s7jYXzM8EGcbK5b",
]


def test_enhanced_recommender_returns_requested_number():
    results = recommend_tracks_enhanced(
        RECENT_TRACKS,
        exploration_level=0.3,
        limit=5,
    )

    assert len(results) == 5


def test_enhanced_recommender_excludes_recent_tracks():
    results = recommend_tracks_enhanced(
        RECENT_TRACKS,
        exploration_level=0.3,
        limit=10,
    )

    result_ids = {
        track["track_id"]
        for track in results
    }

    assert result_ids.isdisjoint(
        RECENT_TRACKS
    )


def test_enhanced_results_include_audio_similarity():
    results = recommend_tracks_enhanced(
        RECENT_TRACKS,
        exploration_level=0.3,
        limit=5,
    )

    assert results

    for track in results:
        assert "audio_similarity" in track


def test_audio_similarity_is_valid_range():
    results = recommend_tracks_enhanced(
        RECENT_TRACKS,
        exploration_level=0.3,
        limit=10,
    )

    for track in results:
        assert (
            0.0
            <= track["audio_similarity"]
            <= 1.0
        )


def test_enhanced_scores_are_sorted():
    results = recommend_tracks_enhanced(
        RECENT_TRACKS,
        exploration_level=0.3,
        limit=10,
    )

    scores = [
        track["score"]
        for track in results
    ]

    assert scores == sorted(
        scores,
        reverse=True,
    )


def test_enhanced_recommender_handles_empty_history():
    results = recommend_tracks_enhanced(
        [],
        exploration_level=0.3,
        limit=5,
    )

    assert results == []


def test_enhanced_recommender_handles_unknown_tracks():
    results = recommend_tracks_enhanced(
        ["not-a-real-track-id"],
        exploration_level=0.3,
        limit=5,
    )

    assert results == []


def test_enhanced_recommender_rejects_negative_limit():
    try:
        recommend_tracks_enhanced(
            RECENT_TRACKS,
            exploration_level=0.3,
            limit=-5,
        )

        assert False

    except ValueError as error:
        assert str(error) == (
            "limit must be at least 1"
        )


def test_enhanced_exploration_changes_results():
    low = recommend_tracks_enhanced(
        RECENT_TRACKS,
        exploration_level=0.0,
        limit=10,
    )

    high = recommend_tracks_enhanced(
        RECENT_TRACKS,
        exploration_level=1.0,
        limit=10,
    )

    assert low != high