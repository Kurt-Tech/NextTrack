import csv
from pathlib import Path

from app.enhanced_recommender import (
    recommend_tracks_enhanced,
)
from app.evaluation import (
    calculate_artist_diversity,
    calculate_artist_preference_hit_rate,
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
        "name": (
            "Acoustic context -> "
            "Rock + Bryan Adams preference"
        ),
        "recent_tracks": [
            "5SuOikwiRyPMVoIQDJUgSV",
            "4qPNDBW1i3p13qLCt0Ki3A",
            "1iJBSr7s7jYXzM8EGcbK5b",
        ],
        "preferred_genres": [
            "rock",
        ],
        "preferred_artists": [
            "Bryan Adams",
        ],
    },
    {
        "name": (
            "Rock context -> "
            "Electronic + Miranda! preference"
        ),
        "recent_tracks": [
            "7DbdUf8aHSYoliSjO6LZv6",
            "1zB4vmk8tFRmM9UULNzbLB",
            "0pqnGHJpmpxLKifKRmU6WP",
        ],
        "preferred_genres": [
            "electronic",
        ],
        "preferred_artists": [
            "Miranda!",
        ],
    },
    {
        "name": (
            "Hip-hop context -> "
            "Country + Kacey Musgraves preference"
        ),
        "recent_tracks": [
            "1aL9518P5G72N92b48tuKw",
            "08Isz2ETWSBhvIl8UpKYsp",
            "42TMa2hgBNjte4uV7jNCnQ",
        ],
        "preferred_genres": [
            "country",
        ],
        "preferred_artists": [
            "Kacey Musgraves",
        ],
    },
]


def _artist_names(
    artists: str,
) -> set[str]:
    return {
        artist.strip().lower()
        for artist in str(artists).split(";")
        if artist.strip()
    }


def calculate_combined_preference_hit_rate(
    recommendations: list[dict],
    preferred_genres: list[str],
    preferred_artists: list[str],
) -> float:
    """
    Return the proportion of recommendations that
    match both a preferred genre and a preferred artist.
    """
    if (
        not recommendations
        or not preferred_genres
        or not preferred_artists
    ):
        return 0.0

    normalized_genres = {
        str(genre).strip().lower()
        for genre in preferred_genres
        if str(genre).strip()
    }

    normalized_artists = {
        str(artist).strip().lower()
        for artist in preferred_artists
        if str(artist).strip()
    }

    matches = 0

    for track in recommendations:
        genre = (
            str(track["track_genre"])
            .strip()
            .lower()
        )

        candidate_artists = _artist_names(
            track["artists"]
        )

        genre_match = (
            genre in normalized_genres
        )

        artist_match = bool(
            candidate_artists
            & normalized_artists
        )

        if genre_match and artist_match:
            matches += 1

    return matches / len(recommendations)


def evaluate_scenario(
    scenario: dict,
) -> list[dict]:
    print("=" * 80)
    print(scenario["name"])

    print(
        f"Preferred genres: "
        f"{scenario['preferred_genres']}"
    )

    print(
        f"Preferred artists: "
        f"{scenario['preferred_artists']}"
    )

    print(
        f"Recent tracks: "
        f"{scenario['recent_tracks']}"
    )

    print("-" * 80)

    results = []

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
                preferred_artists=(
                    scenario["preferred_artists"]
                ),
                preference_strength=strength,
            )
        )

        genre_hit_rate = (
            calculate_genre_preference_hit_rate(
                recommendations,
                scenario["preferred_genres"],
            )
        )

        artist_hit_rate = (
            calculate_artist_preference_hit_rate(
                recommendations,
                scenario["preferred_artists"],
            )
        )

        combined_hit_rate = (
            calculate_combined_preference_hit_rate(
                recommendations,
                scenario["preferred_genres"],
                scenario["preferred_artists"],
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

        result = {
            "scenario": scenario["name"],
            "preference_strength": strength,
            "preferred_genres": ";".join(
                scenario["preferred_genres"]
            ),
            "preferred_artists": ";".join(
                scenario["preferred_artists"]
            ),
            "genre_hit_rate": genre_hit_rate,
            "artist_hit_rate": artist_hit_rate,
            "combined_hit_rate": combined_hit_rate,
            "audio_similarity": audio_similarity,
            "genre_diversity": genre_diversity,
            "artist_diversity": artist_diversity,
            "mean_popularity": mean_popularity,
        }

        results.append(result)

        print(
            f"\nPreference strength: "
            f"{strength:.2f}"
        )

        print(
            f"  Genre preference hit rate: "
            f"{genre_hit_rate:.2f}"
        )

        print(
            f"  Artist preference hit rate: "
            f"{artist_hit_rate:.2f}"
        )

        print(
            f"  Combined preference hit rate: "
            f"{combined_hit_rate:.2f}"
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

    return results


def save_results(
    results: list[dict],
) -> None:
    output_path = Path(
        "docs/evidence/"
        "phase3-combined-preference-results.csv"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "scenario",
        "preference_strength",
        "preferred_genres",
        "preferred_artists",
        "genre_hit_rate",
        "artist_hit_rate",
        "combined_hit_rate",
        "audio_similarity",
        "genre_diversity",
        "artist_diversity",
        "mean_popularity",
    ]

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(results)

    print()
    print("=" * 80)
    print(
        f"Results saved to: "
        f"{output_path}"
    )


def main() -> None:
    print(
        "NextTrack Phase 3 "
        "Combined Preference "
        "Sensitivity Evaluation"
    )
    print("=" * 80)

    all_results = []

    for scenario in SCENARIOS:
        scenario_results = (
            evaluate_scenario(
                scenario
            )
        )

        all_results.extend(
            scenario_results
        )

    save_results(
        all_results
    )


if __name__ == "__main__":
    main()