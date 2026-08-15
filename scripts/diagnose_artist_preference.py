import pandas as pd

from app.audio_similarity import (
    calculate_cosine_similarity,
    get_normalized_audio_features,
)
from app.metadata import get_track, load_tracks


SCENARIOS = [
    {
        "name": "Acoustic -> Bryan Adams",
        "recent_tracks": [
            "5SuOikwiRyPMVoIQDJUgSV",
            "4qPNDBW1i3p13qLCt0Ki3A",
            "1iJBSr7s7jYXzM8EGcbK5b",
        ],
        "preferred_artist": "Bryan Adams",
    },
    {
        "name": "Rock -> Miranda!",
        "recent_tracks": [
            "7DbdUf8aHSYoliSjO6LZv6",
            "1zB4vmk8tFRmM9UULNzbLB",
            "0pqnGHJpmpxLKifKRmU6WP",
        ],
        "preferred_artist": "Miranda!",
    },
    {
        "name": "Hip-hop -> Kacey Musgraves",
        "recent_tracks": [
            "1aL9518P5G72N92b48tuKw",
            "08Isz2ETWSBhvIl8UpKYsp",
            "42TMa2hgBNjte4uV7jNCnQ",
        ],
        "preferred_artist": "Kacey Musgraves",
    },
]


def artist_names(value: str) -> set[str]:
    return {
        artist.strip().lower()
        for artist in str(value).split(";")
        if artist.strip()
    }


def evaluate_scenario(
    scenario: dict,
) -> None:
    df = load_tracks().copy()

    recent_data = [
        get_track(track_id)
        for track_id in scenario["recent_tracks"]
    ]

    recent_data = [
        track
        for track in recent_data
        if track is not None
    ]

    recent_ids = [
        track["track_id"]
        for track in recent_data
    ]

    normalized = (
        get_normalized_audio_features()
    )

    context_vector = (
        normalized
        .loc[recent_ids]
        .mean(axis=0)
        .to_numpy(dtype=float)
    )

    candidates = df[
        ~df["track_id"].isin(recent_ids)
    ].copy()

    candidate_vectors = (
        normalized
        .loc[candidates["track_id"]]
        .to_numpy(dtype=float)
    )

    candidates["audio_similarity"] = (
        calculate_cosine_similarity(
            context_vector,
            candidate_vectors,
        )
    )

    recent_genres = {
        track["track_genre"]
        for track in recent_data
    }

    recent_artists = set()

    for track in recent_data:
        recent_artists.update(
            artist_names(
                track["artists"]
            )
        )

    candidates["genre_match"] = (
        candidates["track_genre"]
        .apply(
            lambda genre:
            1.0
            if genre in recent_genres
            else 0.0
        )
    )

    candidates["artist_match"] = (
        candidates["artists"]
        .apply(
            lambda artists:
            1.0
            if (
                artist_names(artists)
                & recent_artists
            )
            else 0.0
        )
    )

    candidates["familiarity_score"] = (
        0.7 * candidates["genre_match"]
        + 0.3 * candidates["artist_match"]
    )

    candidates["popularity_score"] = (
        candidates["popularity"]
        .fillna(0)
        / 100
    )

    candidates[
        "contextual_relevance"
    ] = (
        0.60
        * candidates["audio_similarity"]
        + 0.25
        * candidates["familiarity_score"]
        + 0.15
        * candidates["popularity_score"]
    )

    candidates = (
        candidates
        .sort_values(
            "contextual_relevance",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    candidates["contextual_rank"] = (
        candidates.index + 1
    )

    preferred = (
        scenario["preferred_artist"]
        .strip()
        .lower()
    )

    artist_candidates = candidates[
        candidates["artists"].apply(
            lambda artists:
            preferred
            in artist_names(artists)
        )
    ]

    print("=" * 80)
    print(scenario["name"])
    print(
        f"Preferred artist: "
        f"{scenario['preferred_artist']}"
    )
    print("-" * 80)

    print(
        f"Candidate tracks: "
        f"{len(artist_candidates)}"
    )

    if artist_candidates.empty:
        print(
            "No candidate tracks found."
        )
        return

    print(
        f"Mean audio similarity: "
        f"{artist_candidates['audio_similarity'].mean():.4f}"
    )

    print(
        f"Maximum audio similarity: "
        f"{artist_candidates['audio_similarity'].max():.4f}"
    )

    print(
        f"Mean contextual relevance: "
        f"{artist_candidates['contextual_relevance'].mean():.4f}"
    )

    print(
        f"Maximum contextual relevance: "
        f"{artist_candidates['contextual_relevance'].max():.4f}"
    )

    print(
        f"Best contextual rank: "
        f"{artist_candidates['contextual_rank'].min()}"
    )

    top_100_count = (
        artist_candidates[
            "contextual_rank"
        ]
        .le(100)
        .sum()
    )

    print(
        f"Tracks in contextual top 100: "
        f"{top_100_count}"
    )


def main() -> None:
    print(
        "NextTrack Phase 3 "
        "Artist Preference Diagnostic"
    )
    print("=" * 80)

    for scenario in SCENARIOS:
        evaluate_scenario(
            scenario
        )


if __name__ == "__main__":
    main()