import json
from pathlib import Path

from app.enhanced_recommender import (
    recommend_tracks_enhanced,
)


REFERENCE_PATH = Path(
    "docs/evidence/"
    "phase4-functional-reference.json"
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


EXPLORATION_LEVELS = [
    0.0,
    0.25,
    0.50,
    0.75,
    1.0,
]


def main():
    with REFERENCE_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        reference = json.load(
            file
        )

    failures = []

    total = 0

    for (
        context_name,
        recent_tracks,
    ) in CONTEXTS.items():
        for exploration in (
            EXPLORATION_LEVELS
        ):
            total += 1

            current = (
                recommend_tracks_enhanced(
                    recent_tracks=(
                        recent_tracks
                    ),
                    exploration_level=(
                        exploration
                    ),
                    limit=10,
                )
            )

            expected = (
                reference[
                    context_name
                ][
                    str(
                        exploration
                    )
                ]
            )

            current_ids = [
                item["track_id"]
                for item in current
            ]

            expected_ids = [
                item["track_id"]
                for item in expected
            ]

            if (
                current_ids
                != expected_ids
            ):
                failures.append(
                    (
                        context_name,
                        exploration,
                    )
                )

                print(
                    "FAIL "
                    f"{context_name:<12} "
                    f"{exploration:.2f}"
                )

            else:
                print(
                    "PASS "
                    f"{context_name:<12} "
                    f"{exploration:.2f}"
                )

    print()
    print("=" * 70)

    if failures:
        print(
            f"FAILED: "
            f"{len(failures)}/{total} "
            "conditions changed."
        )

        raise SystemExit(
            1
        )

    print(
        f"PASS: {total}/{total} "
        "recommendation rankings "
        "match the frozen reference."
    )


if __name__ == "__main__":
    main()