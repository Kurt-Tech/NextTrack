from app.enhanced_recommender import recommend_tracks_enhanced
from app.evaluation import (
    calculate_artist_diversity,
    calculate_genre_diversity,
    calculate_genre_preference_hit_rate,
    calculate_mean_audio_similarity,
    calculate_mean_popularity,
)


PREFERENCE_STRENGTHS = [
    0.0,
    0.25,
    0.5,
    0.75,
    1.0,
]


SCENARIOS = [
    {
        "name": "Acoustic context -> Rock preference",
        "recent_tracks": [
            "5SuOikwiRyPMVoIQDJUgSV",
            "4qPNDBW1i3p13qLCt0Ki3A",
            "1iJBSr7s7jYXzM8EGcbK5b",
        ],
        "preferred_genres": ["rock"],
    },
    {
        "name": "Rock context -> Electronic preference",
        "recent_tracks": [
            "7DbdUf8aHSYoliSjO6LZv6",
            "1zB4vmk8tFRmM9UULNzbLB",
            "0pqnGHJpmpxLKifKRmU6WP",
        ],
        "preferred_genres": ["electronic"],
    },
    {
        "name": "Hip-hop context -> Country preference",
        "recent_tracks": [
            "1aL9518P5G72N92b48tuKw",
            "08Isz2ETWSBhvIl8UpKYsp",
            "42TMa2hgBNjte4uV7jNCnQ",
        ],
        "preferred_genres": ["country"],
    },
]


def evaluate_scenario(
    scenario: dict,
) -> None:
    print("=" * 80)
    print(scenario["name"])
    print(
        f"Preferred genres: "
        f"{scenario['preferred_genres']}"
    )
    print(
        f"Recent tracks: "
        f"{scenario['recent_tracks']}"
    )
    print("-" * 80)

    for strength in PREFERENCE_STRENGTHS:
        recommendations = (
            recommend_tracks_enhanced(
                recent_tracks=(
                    scenario["recent_tracks"]
                ),
                exploration_level=0.3,
                limit=10,
                preferred_genres=(
                    scenario["preferred_genres"]
                ),
                preference_strength=strength,
            )
        )

        preference_hit_rate = (
            calculate_genre_preference_hit_rate(
                recommendations,
                scenario["preferred_genres"],
            )
        )

        audio_similarity = (
            calculate_mean_audio_similarity(
                scenario["recent_tracks"],
                recommendations,
            )
        )

        genre_diversity = (
            calculate_genre_diversity(
                recommendations
            )
        )

        artist_diversity = (
            calculate_artist_diversity(
                recommendations
            )
        )

        mean_popularity = (
            calculate_mean_popularity(
                recommendations
            )
        )

        print(
            f"\nPreference strength: "
            f"{strength:.2f}"
        )

        print(
            f"  Preference hit rate: "
            f"{preference_hit_rate:.2f}"
        )

        print(
            f"  Audio similarity: "
            f"{audio_similarity:.4f}"
        )

        print(
            f"  Genre diversity: "
            f"{genre_diversity:.2f}"
        )

        print(
            f"  Artist diversity: "
            f"{artist_diversity:.2f}"
        )

        print(
            f"  Mean popularity: "
            f"{mean_popularity:.2f}"
        )


def main() -> None:
    print(
        "NextTrack Phase 3 "
        "Preference Sensitivity Evaluation"
    )
    print("=" * 80)

    for scenario in SCENARIOS:
        evaluate_scenario(
            scenario
        )


if __name__ == "__main__":
    main()