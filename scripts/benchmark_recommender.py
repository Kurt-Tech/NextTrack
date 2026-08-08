from statistics import mean, median
from time import perf_counter

import numpy as np

from app.metadata import load_tracks
from app.recommender import recommend_tracks


RECENT_TRACKS = [
    "5SuOikwiRyPMVoIQDJUgSV",
    "4qPNDBW1i3p13qLCt0Ki3A",
    "1iJBSr7s7jYXzM8EGcbK5b",
]

EXPLORATION_LEVELS = [
    0.0,
    0.5,
    1.0,
]

RUNS = 30
LIMIT = 10


def timed_recommendation(exploration_level):
    start = perf_counter()

    recommend_tracks(
        RECENT_TRACKS,
        exploration_level=exploration_level,
        limit=LIMIT,
    )

    end = perf_counter()

    return (end - start) * 1000


def main():
    print("NextTrack Recommendation Benchmark")
    print("=" * 40)

    # Measure cold start separately.
    load_tracks.cache_clear()

    cold_start = timed_recommendation(0.3)

    print(
        f"Cold-start response time: "
        f"{cold_start:.2f} ms"
    )

    print()

    # Ensure dataset remains cached for warm tests.
    load_tracks()

    for exploration_level in EXPLORATION_LEVELS:
        times = [
            timed_recommendation(exploration_level)
            for _ in range(RUNS)
        ]

        print(
            f"Exploration level: {exploration_level}"
        )
        print(f"Runs:    {RUNS}")
        print(f"Minimum: {min(times):.2f} ms")
        print(f"Mean:    {mean(times):.2f} ms")
        print(f"Median:  {median(times):.2f} ms")
        print(f"P95:     {np.percentile(times, 95):.2f} ms")
        print(f"Maximum: {max(times):.2f} ms")
        print()


if __name__ == "__main__":
    main()