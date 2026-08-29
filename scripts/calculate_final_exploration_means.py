import json
from pathlib import Path
from statistics import mean


REFERENCE_PATH = Path(
    "docs/evidence/phase4-functional-reference.json"
)

EXPLORATION_LEVELS = [
    0.0,
    0.25,
    0.5,
    0.75,
    1.0,
]


def genre_diversity(recommendations):
    if not recommendations:
        return 0.0

    genres = {
        str(item["track_genre"]).strip().lower()
        for item in recommendations
    }

    return (
        len(genres)
        / len(recommendations)
    )


def mean_audio_similarity(
    recommendations,
):
    if not recommendations:
        return 0.0

    return mean(
        float(item["audio_similarity"])
        for item in recommendations
    )


def main():
    with REFERENCE_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        reference = json.load(file)

    print(
        "Exploration | "
        "Mean Genre Diversity | "
        "Mean Audio Similarity"
    )
    print("-" * 65)

    for exploration in EXPLORATION_LEVELS:
        key = str(exploration)

        genre_values = []
        audio_values = []

        for (
            context_name,
            context_results,
        ) in reference.items():

            recommendations = (
                context_results[key]
            )

            genre_value = (
                genre_diversity(
                    recommendations
                )
            )

            audio_value = (
                mean_audio_similarity(
                    recommendations
                )
            )

            genre_values.append(
                genre_value
            )

            audio_values.append(
                audio_value
            )

            if exploration == 0.25:
                print(
                    f"  {context_name:<12} "
                    f"genre={genre_value:.4f}"
                )

        print(
            f"{exploration:<11.2f} | "
            f"{mean(genre_values):<20.4f} | "
            f"{mean(audio_values):.4f}"
        )


if __name__ == "__main__":
    main()