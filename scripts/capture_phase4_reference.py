import json
from pathlib import Path

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


OUTPUT_PATH = Path(
    "docs/evidence/"
    "phase4-functional-reference.json"
)


def main():
    results = {}

    for (
        context_name,
        recent_tracks,
    ) in CONTEXTS.items():
        results[
            context_name
        ] = {}

        for exploration in (
            EXPLORATION_LEVELS
        ):
            recommendations = (
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

            results[
                context_name
            ][
                str(exploration)
            ] = recommendations

            print(
                f"{context_name:<12} "
                f"{exploration:.2f} "
                f"captured"
            )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            results,
            file,
            indent=2,
        )

    print()
    print(
        "Reference written to:"
    )
    print(
        OUTPUT_PATH
    )


if __name__ == "__main__":
    main()