import pytest

from app.preference_scoring import (
    apply_preference_weight,
    calculate_preference_score,
)


def test_matching_genre_scores_one():
    score = calculate_preference_score(
        track_genre="rock",
        artists="Artist A",
        preferred_genres=["rock"],
    )

    assert score == 1.0


def test_non_matching_genre_scores_zero():
    score = calculate_preference_score(
        track_genre="jazz",
        artists="Artist A",
        preferred_genres=["rock"],
    )

    assert score == 0.0


def test_matching_artist_scores_one():
    score = calculate_preference_score(
        track_genre="rock",
        artists="Artist A;Artist B",
        preferred_artists=["Artist B"],
    )

    assert score == 1.0


def test_preferences_are_case_insensitive():
    score = calculate_preference_score(
        track_genre="Rock",
        artists="Artist A",
        preferred_genres=["ROCK"],
    )

    assert score == 1.0


def test_genre_and_artist_preferences_are_weighted():
    score = calculate_preference_score(
        track_genre="rock",
        artists="Artist A",
        preferred_genres=["rock"],
        preferred_artists=["Artist B"],
    )

    assert score == pytest.approx(0.6)


def test_no_preferences_returns_zero():
    score = calculate_preference_score(
        track_genre="rock",
        artists="Artist A",
    )

    assert score == 0.0


def test_zero_strength_preserves_contextual_relevance():
    result = apply_preference_weight(
        contextual_relevance=0.8,
        preference_score=1.0,
        preference_strength=0.0,
    )

    assert result == pytest.approx(0.8)


def test_maximum_strength_preserves_contextual_component():
    result = apply_preference_weight(
        contextual_relevance=0.8,
        preference_score=1.0,
        preference_strength=1.0,
    )

    assert result == pytest.approx(0.84)


def test_no_preferences_preserves_contextual_relevance():
    result = apply_preference_weight(
        contextual_relevance=0.8,
        preference_score=0.0,
        preference_strength=1.0,
        has_preferences=False,
    )

    assert result == pytest.approx(0.8)


def test_preference_strength_is_clamped():
    above_one = apply_preference_weight(
        contextual_relevance=0.8,
        preference_score=1.0,
        preference_strength=2.0,
    )

    one = apply_preference_weight(
        contextual_relevance=0.8,
        preference_score=1.0,
        preference_strength=1.0,
    )

    assert above_one == pytest.approx(one)