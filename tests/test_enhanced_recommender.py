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


def test_zero_exploration_scores_are_sorted():
    results = recommend_tracks_enhanced(
        RECENT_TRACKS,
        exploration_level=0.0,
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

def test_diversity_scores_are_finite():
    results = recommend_tracks_enhanced(
        RECENT_TRACKS,
        exploration_level=1.0,
        limit=10,
    )

    for track in results:
        assert isinstance(
            track["score"],
            float,
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

def test_no_preferences_preserve_phase2_results():
    phase2_results = recommend_tracks_enhanced(
        RECENT_TRACKS,
        exploration_level=0.3,
        limit=10,
    )

    no_preference_results = recommend_tracks_enhanced(
        RECENT_TRACKS,
        exploration_level=0.3,
        limit=10,
        preferred_genres=[],
        preferred_artists=[],
        preference_strength=1.0,
    )

    assert no_preference_results == phase2_results


def test_zero_preference_strength_preserves_phase2_results():
    phase2_results = recommend_tracks_enhanced(
        RECENT_TRACKS,
        exploration_level=0.3,
        limit=10,
    )

    zero_strength_results = recommend_tracks_enhanced(
        RECENT_TRACKS,
        exploration_level=0.3,
        limit=10,
        preferred_genres=["rock", "pop"],
        preferred_artists=["Adele"],
        preference_strength=0.0,
    )

    assert zero_strength_results == phase2_results

def test_active_preferences_change_recommendations():
    without_preferences = recommend_tracks_enhanced(
        RECENT_TRACKS,
        exploration_level=0.3,
        limit=10,
    )

    with_preferences = recommend_tracks_enhanced(
        RECENT_TRACKS,
        exploration_level=0.3,
        limit=10,
        preferred_genres=["rock"],
        preference_strength=1.0,
    )

    assert with_preferences != without_preferences

def test_zero_exploration_preserves_pre_phase4_results():
    results = recommend_tracks_enhanced(
        RECENT_TRACKS,
        exploration_level=0.0,
        limit=10,
    )

    repeated_results = recommend_tracks_enhanced(
        RECENT_TRACKS,
        exploration_level=0.0,
        limit=10,
    )

    assert repeated_results == results


def test_diversity_reranking_changes_high_exploration_results():
    low_exploration = recommend_tracks_enhanced(
        RECENT_TRACKS,
        exploration_level=0.0,
        limit=10,
    )

    high_exploration = recommend_tracks_enhanced(
        RECENT_TRACKS,
        exploration_level=1.0,
        limit=10,
    )

    assert high_exploration != low_exploration

def test_preferences_still_affect_results_with_diversity_ranking():
    without_preferences = recommend_tracks_enhanced(
        RECENT_TRACKS,
        exploration_level=0.5,
        limit=10,
    )

    with_preferences = recommend_tracks_enhanced(
        RECENT_TRACKS,
        exploration_level=0.5,
        limit=10,
        preferred_genres=["rock"],
        preference_strength=1.0,
    )

    assert with_preferences != without_preferences