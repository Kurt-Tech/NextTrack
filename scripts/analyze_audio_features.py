from app.metadata import load_tracks


AUDIO_FEATURES = [
    "danceability",
    "energy",
    "loudness",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
]


def main():
    df = load_tracks()

    print("NextTrack Audio Feature Analysis")
    print("=" * 60)
    print(f"Total tracks: {len(df)}")
    print()

    print("Feature availability")
    print("-" * 60)

    for feature in AUDIO_FEATURES:
        print(
            f"{feature}: "
            f"{'FOUND' if feature in df.columns else 'MISSING'}"
        )

    print()

    available_features = [
        feature
        for feature in AUDIO_FEATURES
        if feature in df.columns
    ]

    print("Missing values")
    print("-" * 60)

    print(
        df[available_features]
        .isna()
        .sum()
        .to_string()
    )

    print()

    print("Feature statistics")
    print("-" * 60)

    statistics = (
        df[available_features]
        .describe()
        .transpose()
    )

    print(
        statistics[
            [
                "count",
                "mean",
                "std",
                "min",
                "max",
            ]
        ].to_string()
    )


if __name__ == "__main__":
    main()