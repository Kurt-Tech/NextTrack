from collections import Counter

from app.enhanced_recommender import (
    recommend_tracks_enhanced,
)
from app.evaluation import (
    calculate_artist_diversity,
    calculate_artist_preference_hit_rate,
    calculate_genre_diversity,
    calculate_mean_audio_similarity,
    calculate_mean_popularity,
)
from app.metadata import get_track, load_tracks


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
            "Rock artist preference"
        ),
        "recent_tracks": [
            "5SuOikwiRyPMVoIQDJUgSV",
            "4qPNDBW1i3p13qLCt0Ki3A",
            "1iJBSr7s7jYXzM8EGcbK5b",
        ],
        "target_genre": "rock",
    },
    {
        "name": (
            "Rock context -> "
            "Electronic artist preference"
        ),
        "recent_tracks": [
            "7DbdUf8aHSYoliSjO6LZv6",
            "1zB4vmk8tFRmM9UULNzbLB",
            "0pqnGHJpmpxLKifKRmU6WP",
        ],
        "target_genre": "electronic",
    },
    {
        "name": (
            "Hip-hop context -> "
            "Country artist preference"
        ),
        "recent_tracks": [
            "1aL9518P5G72N92b48tuKw",
            "08Isz2ETWSBhvIl8UpKYsp",
            "42TMa2hgBNjte4uV7jNCnQ",
        ],
        "target_genre": "country",
    },
]


def _artist_names(
    artists: str,
) -> set[str]:
    return {
        artist.strip()
        for artist in str(artists).split(";")
        if artist.strip()
    }


def get_recent_artists(
    recent_tracks: list[str],
) -> set[str]:
    artists = set()

    for track_id in recent_tracks:
        track = get_track(track_id)

        if track is not None:
            artists.update(
                artist.lower()
                for artist in _artist_names(
                    track["artists"]
                )
            )

    return artists


def select_preferred_artist(
    target_genre: str,
    recent_tracks: list[str],
) -> tuple[str, int]:
    """
    Deterministically select an artist from the target
    genre with the largest number of available tracks.

    Artists already present in the recent listening
    context are excluded.
    """
    df = load_tracks()

    genre_tracks = df[
        df["track_genre"]
        .astype(str)
        .str.strip()
        .str.lower()
        == target_genre.strip().lower()
    ]

    recent_artists = get_recent_artists(
        recent_tracks
    )

    artist_counts = Counter()

    artist_display_names = {}

    for artists_value in genre_tracks["artists"]:
        for artist in _artist_names(
            artists_value
        ):
            normalized = artist.lower()

            if normalized in recent_artists:
                continue

            artist_counts[normalized] += 1

            artist_display_names[
                normalized
            ] = artist

    if not artist_counts:
        raise ValueError(
            f"No suitable artist found "
            f"for genre: {target_genre}"
        )

    selected_normalized = sorted(
        artist_counts,
        key=lambda artist: (
            -artist_counts[artist],
            artist,
        ),
    )[0]

    return (
        artist_display_names[
            selected_normalized
        ],
        artist_counts[
            selected_normalized
        ],
    )


def evaluate_scenario(
    scenario: dict,
) -> None:
    preferred_artist, track_count = (
        select_preferred_artist(
            target_genre=(
                scenario["target_genre"]
            ),
            recent_tracks=(
                scenario["recent_tracks"]
            ),
        )
    )

    print("=" * 80)
    print(scenario["name"])

    print(
        f"Target genre used for artist "
        f"selection: "
        f"{scenario['target_genre']}"
    )

    print(
        f"Selected preferred artist: "
        f"{preferred_artist}"
    )

    print(
        f"Artist tracks in target genre: "
        f"{track_count}"
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
                preferred_artists=[
                    preferred_artist
                ],
                preference_strength=strength,
            )
        )

        preference_hit_rate = (
            calculate_artist_preference_hit_rate(
                recommendations,
                [preferred_artist],
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
            f"  Artist preference "
            f"hit rate: "
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
        "Artist Preference "
        "Sensitivity Evaluation"
    )
    print("=" * 80)

    for scenario in SCENARIOS:
        evaluate_scenario(
            scenario
        )


if __name__ == "__main__":
    main()