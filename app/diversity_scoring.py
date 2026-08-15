import math

def calculate_pair_redundancy(
    audio_similarity: float,
    same_genre: bool,
    shared_artist: bool,
) -> float:
    """
    Calculate redundancy between two tracks.

    Redundancy combines:
    - audio similarity: 50%
    - genre overlap:    30%
    - artist overlap:   20%

    The returned value is clamped to 0-1.
    """

    audio_similarity = max(
        0.0,
        min(
            1.0,
            audio_similarity,
        ),
    )

    genre_redundancy = (
        1.0
        if same_genre
        else 0.0
    )

    artist_redundancy = (
        1.0
        if shared_artist
        else 0.0
    )

    redundancy = (
        0.50 * audio_similarity
        + 0.30 * genre_redundancy
        + 0.20 * artist_redundancy
    )

    return max(
        0.0,
        min(
            1.0,
            redundancy,
        ),
    )


def calculate_selection_score(
    relevance_score: float,
    redundancy_score: float,
    exploration_level: float,
    maximum_diversity_weight: float = 0.35,
) -> float:
    """
    Calculate an MMR-style diversity-aware selection score.

    At zero exploration:

        score = relevance

    As exploration increases, relevance receives less
    weight while novelty (1 - redundancy) receives more.

    Formula:

        score =
            (1 - diversity_weight) * relevance
            + diversity_weight * (1 - redundancy)

    where:

        diversity_weight =
            maximum_diversity_weight
            * exploration_level

    With the default maximum diversity weight of 0.35,
    relevance still contributes 65% of the score at
    maximum exploration.
    """

    exploration_level = max(
        0.0,
        min(
            1.0,
            exploration_level,
        ),
    )

    redundancy_score = max(
        0.0,
        min(
            1.0,
            redundancy_score,
        ),
    )

    maximum_diversity_weight = max(
        0.0,
        min(
            1.0,
            maximum_diversity_weight,
        ),
    )

    diversity_weight = (
        maximum_diversity_weight
        * math.sqrt(
            exploration_level
        )
    )

    relevance_weight = (
        1.0
        - diversity_weight
    )

    novelty_score = (
        1.0
        - redundancy_score
    )

    return (
        relevance_weight
        * relevance_score
        + diversity_weight
        * novelty_score
    )