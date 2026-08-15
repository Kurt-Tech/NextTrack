import pytest

from app.diversity_scoring import (
    calculate_pair_redundancy,
    calculate_selection_score,
)


def test_identical_context_has_high_redundancy():
    result = calculate_pair_redundancy(
        audio_similarity=1.0,
        same_genre=True,
        shared_artist=True,
    )

    assert result == pytest.approx(1.0)


def test_different_track_has_low_redundancy():
    result = calculate_pair_redundancy(
        audio_similarity=0.2,
        same_genre=False,
        shared_artist=False,
    )

    assert result == pytest.approx(0.1)


def test_genre_overlap_increases_redundancy():
    without_genre = calculate_pair_redundancy(
        audio_similarity=0.5,
        same_genre=False,
        shared_artist=False,
    )

    with_genre = calculate_pair_redundancy(
        audio_similarity=0.5,
        same_genre=True,
        shared_artist=False,
    )

    assert with_genre > without_genre


def test_artist_overlap_increases_redundancy():
    without_artist = calculate_pair_redundancy(
        audio_similarity=0.5,
        same_genre=False,
        shared_artist=False,
    )

    with_artist = calculate_pair_redundancy(
        audio_similarity=0.5,
        same_genre=False,
        shared_artist=True,
    )

    assert with_artist > without_artist


def test_zero_exploration_preserves_relevance():
    result = calculate_selection_score(
        relevance_score=0.8,
        redundancy_score=1.0,
        exploration_level=0.0,
    )

    assert result == pytest.approx(0.8)


def test_higher_exploration_penalizes_redundancy():
    low = calculate_selection_score(
        relevance_score=0.8,
        redundancy_score=0.8,
        exploration_level=0.25,
    )

    high = calculate_selection_score(
        relevance_score=0.8,
        redundancy_score=0.8,
        exploration_level=1.0,
    )

    assert high < low


def test_exploration_is_clamped():
    above_one = calculate_selection_score(
        relevance_score=0.8,
        redundancy_score=0.5,
        exploration_level=2.0,
    )

    one = calculate_selection_score(
        relevance_score=0.8,
        redundancy_score=0.5,
        exploration_level=1.0,
    )

    assert above_one == pytest.approx(one)


def test_redundancy_is_clamped():
    above_one = calculate_selection_score(
        relevance_score=0.8,
        redundancy_score=2.0,
        exploration_level=1.0,
    )

    one = calculate_selection_score(
        relevance_score=0.8,
        redundancy_score=1.0,
        exploration_level=1.0,
    )

    assert above_one == pytest.approx(one)


def test_zero_exploration_returns_exact_relevance():
    result = calculate_selection_score(
        relevance_score=0.8,
        redundancy_score=1.0,
        exploration_level=0.0,
    )

    assert result == pytest.approx(
        0.8
    )

def test_mmr_selection_formula():
    result = calculate_selection_score(
        relevance_score=0.8,
        redundancy_score=0.6,
        exploration_level=1.0,
        maximum_diversity_weight=0.35,
    )

    expected = (
        0.65 * 0.8
        + 0.35 * 0.4
    )

    assert result == pytest.approx(
        expected
    )

def test_less_redundant_candidate_scores_higher():
    redundant = calculate_selection_score(
        relevance_score=0.8,
        redundancy_score=0.9,
        exploration_level=1.0,
    )

    diverse = calculate_selection_score(
        relevance_score=0.8,
        redundancy_score=0.2,
        exploration_level=1.0,
    )

    assert diverse > redundant

def test_maximum_diversity_weight_is_clamped():
    above_one = calculate_selection_score(
        relevance_score=0.8,
        redundancy_score=0.5,
        exploration_level=1.0,
        maximum_diversity_weight=2.0,
    )

    one = calculate_selection_score(
        relevance_score=0.8,
        redundancy_score=0.5,
        exploration_level=1.0,
        maximum_diversity_weight=1.0,
    )

    assert above_one == pytest.approx(
        one
    )

def test_exploration_uses_sqrt_mapping():
    result = calculate_selection_score(
        relevance_score=0.8,
        redundancy_score=0.6,
        exploration_level=0.25,
        maximum_diversity_weight=0.35,
    )

    diversity_weight = (
        0.35 * 0.5
    )

    expected = (
        (1.0 - diversity_weight) * 0.8
        + diversity_weight * 0.4
    )

    assert result == pytest.approx(
        expected
    )