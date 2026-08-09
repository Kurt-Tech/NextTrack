from statistics import mean

from app.enhanced_recommender import (
    recommend_tracks_enhanced,
)
from app.metadata import load_tracks


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
    return (
        df[df["track_genre"] == genre]
        ["track_id"]
        .head(SEED_COUNT)
        .tolist()
    )


def calculate_jaccard(first, second):
    first_set = set(first)
    second_set = set(second)

    union = first_set | second_set

    if not union:
        return 0.0

    return (
        len(first_set & second_set)
        / len(union)
    )


def main():
    df = load_tracks()

    all_overlaps = []
    all_jaccards = []
    same_set_count = 0
    same_order_count = 0
    comparison_count = 0

    print(
        "NextTrack Exploration Response Diagnostic"
    )
    print("=" * 72)

    for genre in GENRES:
        seed_tracks = select_seed_tracks(
            df,
            genre,
        )

        results_by_level = {}

        for exploration in EXPLORATION_LEVELS:
            recommendations = (
                recommend_tracks_enhanced(
                    recent_tracks=seed_tracks,
                    exploration_level=exploration,
                    limit=LIMIT,
                )
            )

            results_by_level[exploration] = [
                track["track_id"]
                for track in recommendations
            ]

        unique_lists = len({
            tuple(track_ids)
            for track_ids
            in results_by_level.values()
        })

        print()
        print("=" * 72)
        print(f"Context: {genre}")
        print(
            f"Distinct ranked lists: "
            f"{unique_lists}/"
            f"{len(EXPLORATION_LEVELS)}"
        )
        print("-" * 72)

        for first_level, second_level in zip(
            EXPLORATION_LEVELS,
            EXPLORATION_LEVELS[1:],
        ):
            first_ids = (
                results_by_level[first_level]
            )

            second_ids = (
                results_by_level[second_level]
            )

            overlap = len(
                set(first_ids)
                & set(second_ids)
            )

            jaccard = calculate_jaccard(
                first_ids,
                second_ids,
            )

            same_set = (
                set(first_ids)
                == set(second_ids)
            )

            same_order = (
                first_ids
                == second_ids
            )

            comparison_count += 1

            all_overlaps.append(
                overlap / LIMIT
            )

            all_jaccards.append(
                jaccard
            )

            if same_set:
                same_set_count += 1

            if same_order:
                same_order_count += 1

            print(
                f"{first_level:.2f} -> "
                f"{second_level:.2f}"
            )

            print(
                f"  Track overlap: "
                f"{overlap}/{LIMIT}"
            )

            print(
                f"  Jaccard similarity: "
                f"{jaccard:.4f}"
            )

            print(
                f"  Same recommendation set: "
                f"{same_set}"
            )

            print(
                f"  Same ranking: "
                f"{same_order}"
            )

    print()
    print("=" * 72)
    print("AGGREGATE RESPONSE")
    print("-" * 72)

    print(
        f"Adjacent comparisons: "
        f"{comparison_count}"
    )

    print(
        f"Mean track overlap: "
        f"{mean(all_overlaps):.4f}"
    )

    print(
        f"Mean Jaccard similarity: "
        f"{mean(all_jaccards):.4f}"
    )

    print(
        f"Identical recommendation sets: "
        f"{same_set_count}/"
        f"{comparison_count}"
    )

    print(
        f"Identical ranked lists: "
        f"{same_order_count}/"
        f"{comparison_count}"
    )


if __name__ == "__main__":
    main()