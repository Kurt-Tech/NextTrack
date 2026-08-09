from app.evaluation import (
    calculate_artist_diversity,
    calculate_genre_diversity,
    calculate_mean_audio_similarity,
    calculate_mean_popularity,
)
from app.recommender import recommend_tracks


RECENT_TRACKS = [
    "5SuOikwiRyPMVoIQDJUgSV",
    "4qPNDBW1i3p13qLCt0Ki3A",
    "1iJBSr7s7jYXzM8EGcbK5b",
]


def test_mean_audio_similarity_is_valid():
    recommendations = recommend_tracks(
        RECENT_TRACKS,
        exploration_level=0.5,
        limit=10,
    )

    similarity = calculate_mean_audio_similarity(
        RECENT_TRACKS,
        recommendations,
    )

    assert 0.0 <= similarity <= 1.0


def test_genre_diversity_is_valid():
    recommendations = recommend_tracks(
        RECENT_TRACKS,
        exploration_level=0.5,
        limit=10,
    )

    diversity = calculate_genre_diversity(
        recommendations
    )

    assert 0.0 <= diversity <= 1.0


def test_artist_diversity_is_valid():
    recommendations = recommend_tracks(
        RECENT_TRACKS,
        exploration_level=0.5,
        limit=10,
    )

    diversity = calculate_artist_diversity(
        recommendations
    )

    assert 0.0 <= diversity <= 1.0


def test_mean_popularity_is_valid():
    recommendations = recommend_tracks(
        RECENT_TRACKS,
        exploration_level=0.5,
        limit=10,
    )

    popularity = calculate_mean_popularity(
        recommendations
    )

    assert 0.0 <= popularity <= 100.0


def test_empty_recommendations_return_zero_metrics():
    assert calculate_genre_diversity([]) == 0.0
    assert calculate_artist_diversity([]) == 0.0
    assert calculate_mean_popularity([]) == 0.0


def test_artist_diversity_detects_shared_artist():
    recommendations = [
        {
            "artists": "Artist A",
        },
        {
            "artists": "Artist A;Artist B",
        },
    ]

    diversity = calculate_artist_diversity(
        recommendations
    )

    assert diversity == 0.0


def test_artist_diversity_detects_distinct_artists():
    recommendations = [
        {
            "artists": "Artist A",
        },
        {
            "artists": "Artist B",
        },
        {
            "artists": "Artist C",
        },
    ]

    diversity = calculate_artist_diversity(
        recommendations
    )

    assert diversity == 1.0