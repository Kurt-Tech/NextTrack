from collections import Counter

from app.audio_similarity import (
    calculate_cosine_similarity,
    get_normalized_audio_features,
)
from app.candidate_pool import (
    build_candidate_pool,
)
from app.diversity_reranking import (
    calculate_list_redundancy,
)
from app.diversity_scoring import (
    calculate_selection_score,
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

EXPLORATION_LEVEL = 1.0
DIVERSITY_WEIGHT = 0.25
LIMIT = 10


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


def build_candidates(
    recent_tracks: list[str],
):
    df = load_tracks()

    recent_data = []

    for track_id in recent_tracks:
        track = get_track(
            track_id
        )

        if track is not None:
            recent_data.append(
                track
            )

    valid_recent_ids = [
        track["track_id"]
        for track in recent_data
    ]

    recent_genres = [
        track["track_genre"]
        for track in recent_data
    ]

    recent_genres_set = set(
        recent_genres
    )

    context_genre = (
        primary_genre(
            recent_genres
        )
    )

    recent_artists = set()

    for track in recent_data:
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

    vectors = (
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
        vectors,
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
            if genre == context_genre
            else 0.65
            if genre in recent_genres_set
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
                artist_names(artists)
                & recent_artists
            )
            else 0.0
        )
    )

    candidates[
        "familiarity_score"
    ] = (
        0.70
        * candidates["genre_match"]
        + 0.30
        * candidates["artist_match"]
    )

    candidates[
        "relevance_score"
    ] = (
        0.60
        * candidates["audio_similarity"]
        + 0.25
        * candidates["familiarity_score"]
        + 0.15
        * candidates["popularity_score"]
    )

    pool = build_candidate_pool(
        candidates=candidates,
        primary_genre=context_genre,
        exploration_level=(
            EXPLORATION_LEVEL
        ),
        limit=LIMIT,
    )

    pool[
        "audio_vector"
    ] = [
        normalized_features
        .loc[track_id]
        .to_numpy(dtype=float)
        for track_id
        in pool["track_id"]
    ]

    return (
        pool.to_dict(
            orient="records"
        ),
        context_genre,
    )


def required_weight_to_overtake(
    chosen_relevance: float,
    chosen_redundancy: float,
    alternative_relevance: float,
    alternative_redundancy: float,
):
    """
    Estimate the diversity weight at which an alternative
    candidate would equal or exceed the currently chosen
    candidate.

    From:

        R_alt - w * D_alt
        >=
        R_chosen - w * D_chosen

    therefore:

        w >=
        (R_chosen - R_alt)
        /
        (D_chosen - D_alt)

    This is a local diagnostic rather than a guarantee,
    because changing the weight can change earlier greedy
    selections.
    """

    redundancy_difference = (
        chosen_redundancy
        - alternative_redundancy
    )

    if redundancy_difference <= 0:
        return None

    relevance_difference = (
        chosen_relevance
        - alternative_relevance
    )

    if relevance_difference <= 0:
        return 0.0

    return (
        relevance_difference
        / redundancy_difference
    )


def diagnose_context(
    context_name: str,
    recent_tracks: list[str],
):
    candidates, context_genre = (
        build_candidates(
            recent_tracks
        )
    )

    selected = []

    print()
    print("=" * 100)
    print(
        f"Context: {context_name}"
    )
    print(
        f"Primary genre: {context_genre}"
    )
    print(
        f"Candidate pool: {len(candidates)}"
    )
    print(
        f"Exploration level: "
        f"{EXPLORATION_LEVEL:.2f}"
    )
    print(
        f"Current diversity weight: "
        f"{DIVERSITY_WEIGHT:.2f}"
    )
    print("-" * 100)

    remaining = [
        candidate.copy()
        for candidate in candidates
    ]

    for position in range(
        1,
        LIMIT + 1,
    ):
        scored = []

        for candidate in remaining:
            redundancy = (
                calculate_list_redundancy(
                    candidate,
                    selected,
                )
            )

            score = (
                calculate_selection_score(
                    relevance_score=float(
                        candidate[
                            "relevance_score"
                        ]
                    ),
                    redundancy_score=float(
                        redundancy
                    ),
                    exploration_level=(
                        EXPLORATION_LEVEL
                    ),
                    maximum_diversity_weight=(
                        DIVERSITY_WEIGHT
                    ),
                )
            )

            scored.append(
                (
                    candidate,
                    float(redundancy),
                    float(score),
                )
            )

        scored.sort(
            key=lambda item:
            item[2],
            reverse=True,
        )

        chosen, chosen_redundancy, (
            chosen_score
        ) = scored[0]

        alternatives = [
            item
            for item in scored
            if (
                item[0]["track_genre"]
                != context_genre
            )
        ]

        best_alternative = (
            alternatives[0]
            if alternatives
            else None
        )

        print()
        print(
            f"Position {position}"
        )

        print(
            "  CHOSEN"
        )

        print(
            f"    Genre:       "
            f"{chosen['track_genre']}"
        )

        print(
            f"    Track:       "
            f"{chosen['track_name']}"
        )

        print(
            f"    Relevance:   "
            f"{chosen['relevance_score']:.4f}"
        )

        print(
            f"    Redundancy:  "
            f"{chosen_redundancy:.4f}"
        )

        print(
            f"    Select score:"
            f" {chosen_score:.4f}"
        )

        if best_alternative is not None:
            (
                alternative,
                alternative_redundancy,
                alternative_score,
            ) = best_alternative

            threshold = (
                required_weight_to_overtake(
                    chosen_relevance=float(
                        chosen[
                            "relevance_score"
                        ]
                    ),
                    chosen_redundancy=(
                        chosen_redundancy
                    ),
                    alternative_relevance=float(
                        alternative[
                            "relevance_score"
                        ]
                    ),
                    alternative_redundancy=(
                        alternative_redundancy
                    ),
                )
            )

            print(
                "  BEST ALTERNATIVE"
            )

            print(
                f"    Genre:       "
                f"{alternative['track_genre']}"
            )

            print(
                f"    Track:       "
                f"{alternative['track_name']}"
            )

            print(
                f"    Relevance:   "
                f"{alternative['relevance_score']:.4f}"
            )

            print(
                f"    Redundancy:  "
                f"{alternative_redundancy:.4f}"
            )

            print(
                f"    Select score:"
                f" {alternative_score:.4f}"
            )

            print(
                f"    Score gap:   "
                f"{chosen_score - alternative_score:.4f}"
            )

            if threshold is None:
                print(
                    "    Required weight: "
                    "not reachable through "
                    "redundancy advantage"
                )

            else:
                print(
                    f"    Approx required "
                    f"weight: {threshold:.4f}"
                )

        selected.append(
            chosen
        )

        remaining = [
            candidate
            for candidate in remaining
            if (
                candidate["track_id"]
                != chosen["track_id"]
            )
        ]


def main():
    print(
        "NextTrack Phase 4 "
        "Diversity Selection Diagnostic"
    )

    print("=" * 100)

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