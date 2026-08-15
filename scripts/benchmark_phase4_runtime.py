from statistics import mean
from time import perf_counter

from app.enhanced_recommender import (
    recommend_tracks_enhanced,
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
}

EXPLORATION_LEVELS = [
    0.0,
    0.25,
    0.50,
    0.75,
    1.0,
]

RUNS = 5


def measure(
    recent_tracks: list[str],
    exploration_level: float,
) -> float:
    start = perf_counter()

    recommend_tracks_enhanced(
        recent_tracks=recent_tracks,
        exploration_level=exploration_level,
        limit=10,
    )

    end = perf_counter()

    return (
        end - start
    ) * 1000


def main():
    print(
        "NextTrack Phase 4 Runtime Benchmark"
    )
    print("=" * 78)

    all_results = []

    # Warm the dataset/cache before measurements.
    recommend_tracks_enhanced(
        recent_tracks=CONTEXTS["acoustic"],
        exploration_level=0.0,
        limit=10,
    )

    for context_name, tracks in CONTEXTS.items():
        print()
        print(
            f"Context: {context_name}"
        )
        print("-" * 78)

        for exploration in EXPLORATION_LEVELS:
            times = [
                measure(
                    recent_tracks=tracks,
                    exploration_level=exploration,
                )
                for _ in range(RUNS)
            ]

            average = mean(times)

            all_results.append(
                (
                    context_name,
                    exploration,
                    average,
                )
            )

            print(
                f"Exploration {exploration:>4.2f}: "
                f"{average:>8.2f} ms "
                f"(runs: "
                f"{', '.join(f'{value:.1f}' for value in times)})"
            )

    zero_times = [
        result[2]
        for result in all_results
        if result[1] == 0.0
    ]

    diversity_times = [
        result[2]
        for result in all_results
        if result[1] > 0.0
    ]

    zero_mean = mean(
        zero_times
    )

    diversity_mean = mean(
        diversity_times
    )

    print()
    print("=" * 78)
    print(
        "AGGREGATE"
    )
    print("-" * 78)

    print(
        f"Mean zero-exploration runtime: "
        f"{zero_mean:.2f} ms"
    )

    print(
        f"Mean diversity-aware runtime: "
        f"{diversity_mean:.2f} ms"
    )

    print(
        f"Runtime multiplier: "
        f"{diversity_mean / zero_mean:.2f}x"
    )


if __name__ == "__main__":
    main()