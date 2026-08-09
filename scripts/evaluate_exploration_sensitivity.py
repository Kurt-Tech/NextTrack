from statistics import mean
from time import perf_counter

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
    0.00,
    0.25,
    0.50,
    0.75,
    1.00,
]

SEED_COUNT = 3
LIMIT = 10


def select_seed_tracks(df, genre):
    matches = df[
        df["track_genre"] == genre
    ]

    return (
        matches["track_id"]
        .head(SEED_COUNT)
        .tolist()
    )


def timed_recommend(function, **kwargs):
    start = perf_counter()

    results = function(**kwargs)

    elapsed = (
        perf_counter() - start
    ) * 1000

    return results, elapsed


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

    summary = []

    print(
        "NextTrack Multi-Context Evaluation"
    )
    print("=" * 80)

    for genre in GENRES:
        seed_tracks = select_seed_tracks(
            df,
            genre,
        )

        if len(seed_tracks) < SEED_COUNT:
            print(
                f"Skipping {genre}: "
                f"insufficient tracks"
            )
            continue

        print()
        print("=" * 80)
        print(f"Context genre: {genre}")
        print(
            f"Seed tracks: {seed_tracks}"
        )

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

            row = {
                "genre": genre,
                "exploration": exploration,
                "baseline":
                    baseline_metrics,
                "enhanced":
                    enhanced_metrics,
                "baseline_time":
                    baseline_time,
                "enhanced_time":
                    enhanced_time,
            }

            summary.append(row)

            print()
            print(
                f"Exploration: {exploration}"
            )

            print(
                "  Audio similarity: "
                f"{baseline_metrics['audio_similarity']:.4f}"
                " -> "
                f"{enhanced_metrics['audio_similarity']:.4f}"
            )

            print(
                "  Genre diversity: "
                f"{baseline_metrics['genre_diversity']:.2f}"
                " -> "
                f"{enhanced_metrics['genre_diversity']:.2f}"
            )

            print(
                "  Artist diversity: "
                f"{baseline_metrics['artist_diversity']:.2f}"
                " -> "
                f"{enhanced_metrics['artist_diversity']:.2f}"
            )

            print(
                "  Mean popularity: "
                f"{baseline_metrics['mean_popularity']:.2f}"
                " -> "
                f"{enhanced_metrics['mean_popularity']:.2f}"
            )

            print(
                "  Runtime: "
                f"{baseline_time:.2f} ms"
                " -> "
                f"{enhanced_time:.2f} ms"
            )


if __name__ == "__main__":
    main()