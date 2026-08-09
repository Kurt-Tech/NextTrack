from statistics import mean
from time import perf_counter

from app.evaluation import (
    calculate_artist_diversity,
    calculate_genre_diversity,
    calculate_mean_audio_similarity,
    calculate_mean_popularity,
)

from app.metadata import load_tracks
from app.recommender import recommend_tracks
from app.enhanced_recommender import recommend_tracks_enhanced

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

LIMIT = 10



def artist_names(artists):
    return {
        artist.strip().lower()
        for artist in str(artists).split(";")
        if artist.strip()
    }


def calculate_list_metrics(results):
    genres = {
        track["track_genre"]
        for track in results
    }

    artists = set()

    for track in results:
        artists.update(
            artist_names(track["artists"])
        )

    popularities = [
        float(track["popularity"])
        for track in results
    ]

    metrics = {
        "unique_genres": len(genres),
        "unique_artists": len(artists),
        "mean_popularity": mean(popularities),
    }

    if results and "audio_similarity" in results[0]:
        similarities = [
            float(track["audio_similarity"])
            for track in results
        ]

        metrics["mean_audio_similarity"] = mean(
            similarities
        )

    return metrics


def timed_call(function, **kwargs):
    start = perf_counter()

    results = function(**kwargs)

    elapsed_ms = (
        perf_counter() - start
    ) * 1000

    return results, elapsed_ms


def print_results(title, results):
    print(title)
    print("-" * 80)

    for position, track in enumerate(
        results,
        start=1,
    ):
        similarity = track.get(
            "audio_similarity"
        )

        similarity_text = (
            f" | Audio similarity: "
            f"{similarity:.4f}"
            if similarity is not None
            else ""
        )

        print(
            f"{position:2}. "
            f"{track['track_name']} "
            f"- {track['artists']} "
            f"| Genre: {track['track_genre']} "
            f"| Score: {track['score']:.4f}"
            f"{similarity_text}"
        )

    print()


def main():
    print(
        "NextTrack Baseline vs Enhanced Comparison"
    )
    print("=" * 80)

    # Warm the dataset/cache before comparison.
    load_tracks()

    for exploration_level in EXPLORATION_LEVELS:
        print()
        print("=" * 80)
        print(
            f"Exploration level: "
            f"{exploration_level}"
        )
        print("=" * 80)

        baseline, baseline_time = timed_call(
            recommend_tracks,
            recent_tracks=RECENT_TRACKS,
            exploration_level=exploration_level,
            limit=LIMIT,
        )

        enhanced, enhanced_time = timed_call(
            recommend_tracks_enhanced,
            recent_tracks=RECENT_TRACKS,
            exploration_level=exploration_level,
            limit=LIMIT,
        )

        print_results(
            "BASELINE",
            baseline,
        )

        print_results(
            "ENHANCED",
            enhanced,
        )

        baseline_ids = {
            track["track_id"]
            for track in baseline
        }

        enhanced_ids = {
            track["track_id"]
            for track in enhanced
        }

        overlap = (
            baseline_ids
            & enhanced_ids
        )

        baseline_metrics = (
            calculate_list_metrics(
                baseline
            )
        )

        enhanced_metrics = (
            calculate_list_metrics(
                enhanced
            )
        )

        baseline_audio_similarity = calculate_mean_audio_similarity(
            RECENT_TRACKS,
            baseline,
        )

        enhanced_audio_similarity = calculate_mean_audio_similarity(
            RECENT_TRACKS,
            enhanced,
        )        

        print("COMPARISON")
        print("-" * 80)

        print(
            f"Recommendation overlap: "
            f"{len(overlap)}/{LIMIT}"
        )

        print(
            f"Baseline unique genres: "
            f"{baseline_metrics['unique_genres']}"
        )

        print(
            f"Enhanced unique genres: "
            f"{enhanced_metrics['unique_genres']}"
        )

        print(
            f"Baseline unique artists: "
            f"{baseline_metrics['unique_artists']}"
        )

        print(
            f"Baseline artist diversity: "
            f"{calculate_artist_diversity(baseline):.2f}"
        )

        print(
            f"Enhanced artist diversity: "
            f"{calculate_artist_diversity(enhanced):.2f}"
        )

        print(
            f"Enhanced unique artists: "
            f"{enhanced_metrics['unique_artists']}"
        )

        print(
            f"Baseline genre diversity: "
            f"{calculate_genre_diversity(baseline):.2f}"
        )

        print(
            f"Enhanced genre diversity: "
            f"{calculate_genre_diversity(enhanced):.2f}"
        )

        print(
            f"Baseline mean popularity: "
            f"{baseline_metrics['mean_popularity']:.2f}"
        )

        print(
            f"Enhanced mean popularity: "
            f"{enhanced_metrics['mean_popularity']:.2f}"
        )

        if (
            "mean_audio_similarity"
            in enhanced_metrics
        ):
            print(
                f"Enhanced mean audio similarity: "
                f"{enhanced_metrics['mean_audio_similarity']:.4f}"
            )

        print(
            f"Baseline mean audio similarity: "
            f"{baseline_audio_similarity:.4f}"
        )

        print(
            f"Enhanced mean audio similarity: "
            f"{enhanced_audio_similarity:.4f}"
        )

        print(
            f"Baseline execution time: "
            f"{baseline_time:.2f} ms"
        )

        print(
            f"Enhanced execution time: "
            f"{enhanced_time:.2f} ms"
        )


if __name__ == "__main__":
    main()