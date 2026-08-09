from time import perf_counter

import pandas as pd

from app.enhanced_recommender import (
    recommend_tracks_enhanced,
)
from app.evaluation import (
    calculate_artist_diversity,
    calculate_genre_diversity,
    calculate_mean_audio_similarity,
    calculate_mean_popularity,
)
from app.metadata import load_tracks
from app.recommender import recommend_tracks


GENRES = [
    "acoustic",
    "rock",
    "hip-hop",
    "classical",
    "country",
    "electronic",
]

EXPLORATION_LEVELS = [
    0.0,
    0.5,
    1.0,
]

SEED_COUNT = 3
LIMIT = 10


def select_seed_tracks(df, genre):
    return (
        df[df["track_genre"] == genre]
        ["track_id"]
        .head(SEED_COUNT)
        .tolist()
    )


def timed_recommend(function, **kwargs):
    start = perf_counter()

    results = function(**kwargs)

    elapsed_ms = (
        perf_counter() - start
    ) * 1000

    return results, elapsed_ms


def evaluate(
    recent_tracks,
    recommendations,
):
    return {
        "audio_similarity":
            calculate_mean_audio_similarity(
                recent_tracks,
                recommendations,
            ),
        "genre_diversity":
            calculate_genre_diversity(
                recommendations
            ),
        "artist_diversity":
            calculate_artist_diversity(
                recommendations
            ),
        "mean_popularity":
            calculate_mean_popularity(
                recommendations
            ),
    }


def main():
    df = load_tracks()

    rows = []

    for genre in GENRES:
        seed_tracks = select_seed_tracks(
            df,
            genre,
        )

        if len(seed_tracks) < SEED_COUNT:
            continue

        for exploration in EXPLORATION_LEVELS:
            baseline, baseline_time = (
                timed_recommend(
                    recommend_tracks,
                    recent_tracks=seed_tracks,
                    exploration_level=exploration,
                    limit=LIMIT,
                )
            )

            enhanced, enhanced_time = (
                timed_recommend(
                    recommend_tracks_enhanced,
                    recent_tracks=seed_tracks,
                    exploration_level=exploration,
                    limit=LIMIT,
                )
            )

            baseline_metrics = evaluate(
                seed_tracks,
                baseline,
            )

            enhanced_metrics = evaluate(
                seed_tracks,
                enhanced,
            )

            rows.append({
                "context_genre": genre,
                "exploration_level": exploration,

                "baseline_audio_similarity":
                    baseline_metrics[
                        "audio_similarity"
                    ],
                "enhanced_audio_similarity":
                    enhanced_metrics[
                        "audio_similarity"
                    ],

                "baseline_genre_diversity":
                    baseline_metrics[
                        "genre_diversity"
                    ],
                "enhanced_genre_diversity":
                    enhanced_metrics[
                        "genre_diversity"
                    ],

                "baseline_artist_diversity":
                    baseline_metrics[
                        "artist_diversity"
                    ],
                "enhanced_artist_diversity":
                    enhanced_metrics[
                        "artist_diversity"
                    ],

                "baseline_mean_popularity":
                    baseline_metrics[
                        "mean_popularity"
                    ],
                "enhanced_mean_popularity":
                    enhanced_metrics[
                        "mean_popularity"
                    ],

                "baseline_runtime_ms":
                    baseline_time,
                "enhanced_runtime_ms":
                    enhanced_time,
            })

    results = pd.DataFrame(rows)

    results.to_csv(
        "docs/evidence/"
        "phase2-aggregate-results.csv",
        index=False,
    )

    metrics = [
        (
            "Audio similarity",
            "baseline_audio_similarity",
            "enhanced_audio_similarity",
        ),
        (
            "Genre diversity",
            "baseline_genre_diversity",
            "enhanced_genre_diversity",
        ),
        (
            "Artist diversity",
            "baseline_artist_diversity",
            "enhanced_artist_diversity",
        ),
        (
            "Mean popularity",
            "baseline_mean_popularity",
            "enhanced_mean_popularity",
        ),
        (
            "Runtime (ms)",
            "baseline_runtime_ms",
            "enhanced_runtime_ms",
        ),
    ]

    print(
        "NextTrack Phase 2 Aggregate Evaluation"
    )
    print("=" * 72)
    print(
        f"Contexts evaluated: {len(GENRES)}"
    )
    print(
        f"Exploration levels: "
        f"{len(EXPLORATION_LEVELS)}"
    )
    print(
        f"Total conditions: {len(results)}"
    )
    print()

    print("OVERALL RESULTS")
    print("-" * 72)

    for (
        label,
        baseline_column,
        enhanced_column,
    ) in metrics:
        baseline_mean = results[
            baseline_column
        ].mean()

        enhanced_mean = results[
            enhanced_column
        ].mean()

        difference = (
            enhanced_mean
            - baseline_mean
        )

        print(
            f"{label:<22}"
            f"Baseline: {baseline_mean:>8.4f}  "
            f"Enhanced: {enhanced_mean:>8.4f}  "
            f"Difference: {difference:>+8.4f}"
        )

    print()
    print("RESULT COUNTS")
    print("-" * 72)

    similarity_wins = (
        results[
            "enhanced_audio_similarity"
        ]
        >
        results[
            "baseline_audio_similarity"
        ]
    ).sum()

    genre_better = (
        results[
            "enhanced_genre_diversity"
        ]
        >
        results[
            "baseline_genre_diversity"
        ]
    ).sum()

    genre_equal = (
        results[
            "enhanced_genre_diversity"
        ]
        ==
        results[
            "baseline_genre_diversity"
        ]
    ).sum()

    genre_lower = (
        results[
            "enhanced_genre_diversity"
        ]
        <
        results[
            "baseline_genre_diversity"
        ]
    ).sum()

    artist_better = (
        results[
            "enhanced_artist_diversity"
        ]
        >
        results[
            "baseline_artist_diversity"
        ]
    ).sum()

    lower_popularity = (
        results[
            "enhanced_mean_popularity"
        ]
        <
        results[
            "baseline_mean_popularity"
        ]
    ).sum()

    print(
        "Enhanced audio similarity higher: "
        f"{similarity_wins}/{len(results)}"
    )

    print(
        "Enhanced genre diversity higher: "
        f"{genre_better}/{len(results)}"
    )

    print(
        "Genre diversity equal: "
        f"{genre_equal}/{len(results)}"
    )

    print(
        "Enhanced genre diversity lower: "
        f"{genre_lower}/{len(results)}"
    )

    print(
        "Enhanced artist diversity higher: "
        f"{artist_better}/{len(results)}"
    )

    print(
        "Enhanced mean popularity lower: "
        f"{lower_popularity}/{len(results)}"
    )

    print()
    print("BY EXPLORATION LEVEL")
    print("-" * 72)

    grouped = (
        results
        .groupby("exploration_level")
        .mean(numeric_only=True)
    )

    for exploration, row in grouped.iterrows():
        print()
        print(
            f"Exploration: {exploration}"
        )

        print(
            "  Audio similarity: "
            f"{row['baseline_audio_similarity']:.4f}"
            " -> "
            f"{row['enhanced_audio_similarity']:.4f}"
        )

        print(
            "  Genre diversity: "
            f"{row['baseline_genre_diversity']:.4f}"
            " -> "
            f"{row['enhanced_genre_diversity']:.4f}"
        )

        print(
            "  Artist diversity: "
            f"{row['baseline_artist_diversity']:.4f}"
            " -> "
            f"{row['enhanced_artist_diversity']:.4f}"
        )

        print(
            "  Mean popularity: "
            f"{row['baseline_mean_popularity']:.2f}"
            " -> "
            f"{row['enhanced_mean_popularity']:.2f}"
        )

    grouped.to_csv(
        "docs/evidence/"
        "phase2-summary-by-exploration.csv"
    )


if __name__ == "__main__":
    main()