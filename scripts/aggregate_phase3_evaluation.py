import csv
from pathlib import Path
from statistics import mean


PREFERENCE_STRENGTHS = [
    0.0,
    0.25,
    0.5,
    0.75,
    1.0,
]


# ---------------------------------------------------------------------
# Genre-only preference experiment
# Final configuration: maximum preference weight = 20%
# ---------------------------------------------------------------------

GENRE_ONLY_RESULTS = {
    "Acoustic -> Rock": {
        "hit_rate": [
            0.00,
            0.10,
            0.30,
            0.70,
            1.00,
        ],
        "audio_similarity": [
            0.9366,
            0.9407,
            0.9264,
            0.8772,
            0.8618,
        ],
    },
    "Rock -> Electronic": {
        "hit_rate": [
            0.00,
            0.00,
            0.60,
            1.00,
            1.00,
        ],
        "audio_similarity": [
            0.8940,
            0.8940,
            0.9272,
            0.9304,
            0.9304,
        ],
    },
    "Hip-hop -> Country": {
        "hit_rate": [
            0.00,
            0.00,
            0.20,
            0.90,
            1.00,
        ],
        "audio_similarity": [
            0.9414,
            0.9430,
            0.9421,
            0.9043,
            0.8919,
        ],
    },
}


# ---------------------------------------------------------------------
# Artist-only preference experiment
# Final configuration: maximum preference weight = 20%
# ---------------------------------------------------------------------

ARTIST_ONLY_RESULTS = {
    "Acoustic -> Bryan Adams": {
        "hit_rate": [
            0.00,
            0.00,
            0.10,
            0.30,
            0.70,
        ],
        "audio_similarity": [
            0.9366,
            0.9366,
            0.9363,
            0.9259,
            0.8701,
        ],
    },
    "Rock -> Miranda!": {
        "hit_rate": [
            0.00,
            0.00,
            0.10,
            0.60,
            0.90,
        ],
        "audio_similarity": [
            0.8940,
            0.8940,
            0.9015,
            0.9098,
            0.9010,
        ],
    },
    "Hip-hop -> Kacey Musgraves": {
        "hit_rate": [
            0.00,
            0.00,
            0.00,
            0.10,
            0.10,
        ],
        "audio_similarity": [
            0.9414,
            0.9430,
            0.9430,
            0.9298,
            0.9298,
        ],
    },
}


# ---------------------------------------------------------------------
# Combined genre + artist experiment
# ---------------------------------------------------------------------

COMBINED_RESULTS = {
    "Acoustic -> Rock + Bryan Adams": {
        "genre_hit_rate": [
            0.00,
            0.00,
            0.10,
            0.20,
            0.80,
        ],
        "artist_hit_rate": [
            0.00,
            0.00,
            0.00,
            0.00,
            0.10,
        ],
        "combined_hit_rate": [
            0.00,
            0.00,
            0.00,
            0.00,
            0.10,
        ],
        "audio_similarity": [
            0.9366,
            0.9366,
            0.9407,
            0.9375,
            0.8571,
        ],
    },
    "Rock -> Electronic + Miranda!": {
        "genre_hit_rate": [
            0.00,
            0.00,
            0.10,
            0.70,
            1.00,
        ],
        "artist_hit_rate": [
            0.00,
            0.00,
            0.10,
            0.20,
            0.70,
        ],
        "combined_hit_rate": [
            0.00,
            0.00,
            0.10,
            0.20,
            0.70,
        ],
        "audio_similarity": [
            0.8940,
            0.8940,
            0.9015,
            0.9316,
            0.9244,
        ],
    },
    "Hip-hop -> Country + Kacey Musgraves": {
        "genre_hit_rate": [
            0.00,
            0.00,
            0.10,
            0.20,
            0.80,
        ],
        "artist_hit_rate": [
            0.00,
            0.00,
            0.00,
            0.00,
            0.10,
        ],
        "combined_hit_rate": [
            0.00,
            0.00,
            0.00,
            0.00,
            0.10,
        ],
        "audio_similarity": [
            0.9414,
            0.9430,
            0.9447,
            0.9421,
            0.9050,
        ],
    },
}


def mean_for_strength(
    results: dict,
    metric: str,
    index: int,
) -> float:
    """
    Calculate the mean value of a metric across
    all scenarios at one preference strength.
    """
    values = [
        scenario[metric][index]
        for scenario in results.values()
    ]

    return mean(values)


def build_summary() -> list[dict]:
    """
    Build an aggregate Phase 3 result for every
    preference-strength level.
    """
    summary = []

    for index, strength in enumerate(
        PREFERENCE_STRENGTHS
    ):
        row = {
            "preference_strength": strength,

            "genre_only_hit_rate":
                mean_for_strength(
                    GENRE_ONLY_RESULTS,
                    "hit_rate",
                    index,
                ),

            "genre_only_audio_similarity":
                mean_for_strength(
                    GENRE_ONLY_RESULTS,
                    "audio_similarity",
                    index,
                ),

            "artist_only_hit_rate":
                mean_for_strength(
                    ARTIST_ONLY_RESULTS,
                    "hit_rate",
                    index,
                ),

            "artist_only_audio_similarity":
                mean_for_strength(
                    ARTIST_ONLY_RESULTS,
                    "audio_similarity",
                    index,
                ),

            "combined_genre_hit_rate":
                mean_for_strength(
                    COMBINED_RESULTS,
                    "genre_hit_rate",
                    index,
                ),

            "combined_artist_hit_rate":
                mean_for_strength(
                    COMBINED_RESULTS,
                    "artist_hit_rate",
                    index,
                ),

            "combined_exact_hit_rate":
                mean_for_strength(
                    COMBINED_RESULTS,
                    "combined_hit_rate",
                    index,
                ),

            "combined_audio_similarity":
                mean_for_strength(
                    COMBINED_RESULTS,
                    "audio_similarity",
                    index,
                ),
        }

        summary.append(row)

    return summary


def print_summary(
    summary: list[dict],
) -> None:
    print(
        "NextTrack Phase 3 "
        "Aggregate Preference Evaluation"
    )
    print("=" * 104)

    print("EXPERIMENT COVERAGE")
    print("-" * 104)

    print(
        f"Preference strengths evaluated: "
        f"{len(PREFERENCE_STRENGTHS)}"
    )

    print(
        f"Genre-only scenarios: "
        f"{len(GENRE_ONLY_RESULTS)}"
    )

    print(
        f"Artist-only scenarios: "
        f"{len(ARTIST_ONLY_RESULTS)}"
    )

    print(
        f"Combined scenarios: "
        f"{len(COMBINED_RESULTS)}"
    )

    total_conditions = (
        len(PREFERENCE_STRENGTHS)
        * (
            len(GENRE_ONLY_RESULTS)
            + len(ARTIST_ONLY_RESULTS)
            + len(COMBINED_RESULTS)
        )
    )

    print(
        f"Total evaluated conditions: "
        f"{total_conditions}"
    )

    print()
    print("AGGREGATE RESULTS BY PREFERENCE STRENGTH")
    print("-" * 104)

    header = (
        f"{'Strength':<10}"
        f"{'Genre Hit':<12}"
        f"{'Artist Hit':<12}"
        f"{'Comb Genre':<12}"
        f"{'Comb Artist':<13}"
        f"{'Comb Exact':<12}"
        f"{'Genre Audio':<13}"
        f"{'Artist Audio':<14}"
        f"{'Comb Audio':<12}"
    )

    print(header)
    print("-" * 104)

    for row in summary:
        print(
            f"{row['preference_strength']:<10.2f}"
            f"{row['genre_only_hit_rate']:<12.4f}"
            f"{row['artist_only_hit_rate']:<12.4f}"
            f"{row['combined_genre_hit_rate']:<12.4f}"
            f"{row['combined_artist_hit_rate']:<13.4f}"
            f"{row['combined_exact_hit_rate']:<12.4f}"
            f"{row['genre_only_audio_similarity']:<13.4f}"
            f"{row['artist_only_audio_similarity']:<14.4f}"
            f"{row['combined_audio_similarity']:<12.4f}"
        )

    print()
    print("KEY FINDINGS")
    print("-" * 104)

    final = summary[-1]
    middle = summary[2]
    high = summary[3]

    print(
        "1. Genre-only preferences show a clear "
        "increase in influence as preference "
        "strength rises."
    )

    print(
        "   Mean genre hit rate: "
        f"{summary[0]['genre_only_hit_rate']:.4f} "
        f"at strength 0.00 -> "
        f"{final['genre_only_hit_rate']:.4f} "
        f"at strength 1.00."
    )

    print()

    print(
        "2. Artist-only preferences also become "
        "more influential, but the response is "
        "more dependent on contextual compatibility."
    )

    print(
        "   Mean artist hit rate: "
        f"{summary[0]['artist_only_hit_rate']:.4f} "
        f"at strength 0.00 -> "
        f"{final['artist_only_hit_rate']:.4f} "
        f"at strength 1.00."
    )

    print()

    print(
        "3. Combined preferences increasingly "
        "favour the requested genre while exact "
        "genre-and-artist matches remain more "
        "selective."
    )

    print(
        "   Combined genre hit rate at strength "
        f"1.00: "
        f"{final['combined_genre_hit_rate']:.4f}"
    )

    print(
        "   Combined artist hit rate at strength "
        f"1.00: "
        f"{final['combined_artist_hit_rate']:.4f}"
    )

    print(
        "   Exact combined hit rate at strength "
        f"1.00: "
        f"{final['combined_exact_hit_rate']:.4f}"
    )

    print()

    print(
        "4. The refined 20% preference weighting "
        "provides separation between medium and "
        "high preference strengths."
    )

    print(
        "   Genre-only hit rate: "
        f"{middle['genre_only_hit_rate']:.4f} "
        f"at 0.50 -> "
        f"{high['genre_only_hit_rate']:.4f} "
        f"at 0.75 -> "
        f"{final['genre_only_hit_rate']:.4f} "
        f"at 1.00."
    )

    print()

    print(
        "5. Contextual audio similarity remains "
        "strong even at maximum preference strength."
    )

    print(
        "   Genre-only audio similarity at 1.00: "
        f"{final['genre_only_audio_similarity']:.4f}"
    )

    print(
        "   Artist-only audio similarity at 1.00: "
        f"{final['artist_only_audio_similarity']:.4f}"
    )

    print(
        "   Combined audio similarity at 1.00: "
        f"{final['combined_audio_similarity']:.4f}"
    )


def save_summary(
    summary: list[dict],
) -> None:
    output_path = Path(
        "docs/evidence/"
        "phase3-final-aggregate-results.csv"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "preference_strength",
        "genre_only_hit_rate",
        "genre_only_audio_similarity",
        "artist_only_hit_rate",
        "artist_only_audio_similarity",
        "combined_genre_hit_rate",
        "combined_artist_hit_rate",
        "combined_exact_hit_rate",
        "combined_audio_similarity",
    ]

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for row in summary:
            writer.writerow(row)

    print()
    print("=" * 104)
    print(
        f"Aggregate CSV saved to: "
        f"{output_path}"
    )


def main() -> None:
    summary = build_summary()

    print_summary(
        summary
    )

    save_summary(
        summary
    )


if __name__ == "__main__":
    main()