from collections import Counter

from app.audio_similarity import (
    calculate_cosine_similarity,
    get_normalized_audio_features,
)
from app.metadata import (
    get_track,
    load_tracks,
)


CONTEXTS = {
    "acoustic": [
        "5SuOikwiRyPMVoIQDJUgSV",
        "4qPNDBW1i3p13qLCt0Ki3A",
        "1iJBSr7s7jYXzM8EGcbK5b",
    ],
    "rock": [
        "7DbdUf8aHSYoliSjO6LZv6",
        "1zB4vmk8tFRmM9UULNzbLB",
        "0pqnGHJpmpxLKifKRmU6WP",
    ],
    "hip-hop": [
        "1aL9518P5G72N92b48tuKw",
        "08Isz2ETWSBhvIl8UpKYsp",
        "42TMa2hgBNjte4uV7jNCnQ",
    ],
    "classical": [
        "7wrYBASu0OoxoDErd4Edxd",
        "72HdutlIHBZJ7WT1xVAAZT",
        "7JGgKHHDgJCJkQCQxyHHdl",
    ],
    "country": [
        "2wrJq5XKLnmhRXHIAf9xBa",
        "6AHJTA1BN7ePfChCwqph3z",
        "5eUtyONoPyfZYGrFHmZzlc",
    ],
    "electronic": [
        "57kR5SniQIbsbVoIjjOUDa",
        "5SpGYwR8nzi9eMaHL5Ucyq",
        "7GlCU1ImbOyED4BW6H1TSH",
    ],
}


POOL_SIZES = [
    100,
    250,
    500,
    1000,
    2000,
]


def artist_names(
    artists: str,
) -> set[str]:
    return {
        artist.strip().lower()
        for artist in str(artists).split(";")
        if artist.strip()
    }


def primary_genre(
    genres: list[str],
) -> str:
    return Counter(
        genres
    ).most_common(1)[0][0]


def build_scored_candidates(
    recent_tracks: list[str],
):
    df = load_tracks()

    recent_track_data = []

    for track_id in recent_tracks:
        track = get_track(track_id)

        if track is not None:
            recent_track_data.append(
                track
            )

    valid_recent_ids = [
        track["track_id"]
        for track in recent_track_data
    ]

    recent_genres = [
        track["track_genre"]
        for track in recent_track_data
    ]

    recent_genres_set = set(
        recent_genres
    )

    context_primary_genre = (
        primary_genre(
            recent_genres
        )
    )

    recent_artists = set()

    for track in recent_track_data:
        recent_artists.update(
            artist_names(
                track["artists"]
            )
        )

    normalized_features = (
        get_normalized_audio_features()
    )

    recent_vectors = (
        normalized_features.loc[
            valid_recent_ids
        ]
    )

    context_vector = (
        recent_vectors
        .mean(axis=0)
        .to_numpy(dtype=float)
    )

    candidates = df[
        ~df["track_id"].isin(
            valid_recent_ids
        )
    ].copy()

    candidate_vectors = (
        normalized_features
        .loc[
            candidates["track_id"]
        ]
        .to_numpy(dtype=float)
    )

    candidates[
        "audio_similarity"
    ] = calculate_cosine_similarity(
        context_vector,
        candidate_vectors,
    )

    candidates[
        "popularity_score"
    ] = (
        candidates["popularity"]
        .fillna(0)
        / 100
    )

    candidates[
        "genre_match"
    ] = (
        candidates["track_genre"]
        .apply(
            lambda genre:
            1.0
            if genre
            == context_primary_genre
            else 0.65
            if genre
            in recent_genres_set
            else 0.0
        )
    )

    candidates[
        "artist_match"
    ] = (
        candidates["artists"]
        .apply(
            lambda artists:
            1.0
            if (
                artist_names(
                    artists
                )
                & recent_artists
            )
            else 0.0
        )
    )

    candidates[
        "familiarity_score"
    ] = (
        0.70
        * candidates[
            "genre_match"
        ]
        + 0.30
        * candidates[
            "artist_match"
        ]
    )

    candidates[
        "relevance_score"
    ] = (
        0.60
        * candidates[
            "audio_similarity"
        ]
        + 0.25
        * candidates[
            "familiarity_score"
        ]
        + 0.15
        * candidates[
            "popularity_score"
        ]
    )

    return (
        candidates.sort_values(
            by="relevance_score",
            ascending=False,
        ),
        context_primary_genre,
    )


def diagnose_context(
    context_name: str,
    recent_tracks: list[str],
):
    candidates, context_genre = (
        build_scored_candidates(
            recent_tracks
        )
    )

    print()
    print("=" * 88)
    print(
        f"Context: {context_name}"
    )
    print(
        f"Primary genre: {context_genre}"
    )
    print("-" * 88)

    for pool_size in POOL_SIZES:
        pool = candidates.head(
            pool_size
        )

        genre_counts = (
            pool["track_genre"]
            .value_counts()
        )

        unique_genres = int(
            pool[
                "track_genre"
            ].nunique()
        )

        primary_count = int(
            genre_counts.get(
                context_genre,
                0,
            )
        )

        primary_percentage = (
            primary_count
            / len(pool)
            * 100
        )

        other_genres = (
            genre_counts[
                genre_counts.index
                != context_genre
            ]
            .head(5)
        )

        print(
            f"\nPool size: {pool_size}"
        )

        print(
            "  Unique genres: "
            f"{unique_genres}"
        )

        print(
            "  Primary genre tracks: "
            f"{primary_count}/{len(pool)} "
            f"({primary_percentage:.1f}%)"
        )

        print(
            "  Most common genres:"
        )

        for (
            genre,
            count,
        ) in genre_counts.head(
            6
        ).items():
            print(
                f"    {genre:<20} "
                f"{count}"
            )

        if len(
            other_genres
        ) == 0:
            print(
                "  No alternative genres "
                "in this pool."
            )


def main():
    print(
        "NextTrack Phase 4 "
        "Candidate Pool Diagnostic"
    )

    print("=" * 88)

    for (
        context_name,
        recent_tracks,
    ) in CONTEXTS.items():
        diagnose_context(
            context_name,
            recent_tracks,
        )


if __name__ == "__main__":
    main()