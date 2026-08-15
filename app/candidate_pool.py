import pandas as pd


def build_candidate_pool(
    candidates: pd.DataFrame,
    primary_genre: str,
    exploration_level: float,
    limit: int,
    pool_multiplier: int = 50,
    maximum_reserve_fraction: float = 0.40,
) -> pd.DataFrame:
    """
    Build an exploration-aware recommendation candidate pool.

    At exploration level 0, the pool consists entirely of
    the highest-relevance candidates.

    As exploration increases, up to 40% of the pool is
    reserved for high-relevance candidates from genres
    other than the primary listening-context genre.

    Diversity-reserve candidates are selected in rounds
    across genres so that one genre cannot dominate the
    reserve.

    Parameters
    ----------
    candidates:
        Candidate tracks containing at least:
        - track_id
        - track_genre
        - relevance_score

    primary_genre:
        Dominant genre in the recent listening context.

    exploration_level:
        Exploration value between 0 and 1. Values outside
        this range are clamped.

    limit:
        Number of final recommendations requested.

    pool_multiplier:
        Candidate-pool size relative to recommendation
        limit. The default produces 500 candidates for
        a recommendation limit of 10.

    maximum_reserve_fraction:
        Maximum proportion of the candidate pool reserved
        for alternative genres at exploration level 1.
    """

    if limit < 1:
        raise ValueError(
            "limit must be at least 1"
        )

    if candidates.empty:
        return candidates.copy()

    exploration_level = max(
        0.0,
        min(
            1.0,
            exploration_level,
        ),
    )

    maximum_reserve_fraction = max(
        0.0,
        min(
            1.0,
            maximum_reserve_fraction,
        ),
    )

    pool_size = max(
        limit * pool_multiplier,
        100,
    )

    pool_size = min(
        pool_size,
        len(candidates),
    )

    ranked_candidates = (
        candidates
        .sort_values(
            by="relevance_score",
            ascending=False,
        )
        .copy()
    )

    # -----------------------------------------------------
    # Zero exploration
    #
    # Preserve the original relevance-ranked candidate
    # pool exactly.
    # -----------------------------------------------------

    if exploration_level == 0.0:
        return (
            ranked_candidates
            .head(pool_size)
            .copy()
        )

    # -----------------------------------------------------
    # Calculate the number of diversity-reserve positions.
    #
    # With the default 500-track pool and 40% maximum:
    #
    # 0.25 ->  50 reserve candidates
    # 0.50 -> 100 reserve candidates
    # 0.75 -> 150 reserve candidates
    # 1.00 -> 200 reserve candidates
    # -----------------------------------------------------

    reserve_fraction = (
        maximum_reserve_fraction
        * exploration_level
    )

    reserve_size = int(
        round(
            pool_size
            * reserve_fraction
        )
    )

    core_size = (
        pool_size
        - reserve_size
    )

    # -----------------------------------------------------
    # Relevance core
    # -----------------------------------------------------

    core = (
        ranked_candidates
        .head(core_size)
        .copy()
    )

    core_ids = set(
        core["track_id"]
    )

    # -----------------------------------------------------
    # Alternative-genre candidates
    #
    # Exclude:
    # - candidates already in the core
    # - candidates from the primary genre
    # -----------------------------------------------------

    alternatives = (
        ranked_candidates[
            ~ranked_candidates[
                "track_id"
            ].isin(core_ids)
            &
            (
                ranked_candidates[
                    "track_genre"
                ]
                != primary_genre
            )
        ]
        .copy()
    )

    if alternatives.empty:
        return (
            ranked_candidates
            .head(pool_size)
            .copy()
        )

    # -----------------------------------------------------
    # Round-robin genre ranking
    #
    # genre_rank = 0 represents the highest-relevance
    # candidate from each genre, genre_rank = 1 the second
    # highest, and so on.
    #
    # Sorting first by genre_rank means the reserve draws
    # broadly across genres before selecting multiple
    # tracks from the same genre.
    # -----------------------------------------------------

    alternatives[
        "_genre_rank"
    ] = (
        alternatives
        .groupby(
            "track_genre",
            sort=False,
        )
        .cumcount()
    )

    reserve = (
        alternatives
        .sort_values(
            by=[
                "_genre_rank",
                "relevance_score",
            ],
            ascending=[
                True,
                False,
            ],
        )
        .head(reserve_size)
        .drop(
            columns=[
                "_genre_rank"
            ]
        )
        .copy()
    )

    # -----------------------------------------------------
    # Combine relevance core and diversity reserve.
    # -----------------------------------------------------

    pool = pd.concat(
        [
            core,
            reserve,
        ],
        ignore_index=True,
    )

    pool = (
        pool
        .drop_duplicates(
            subset="track_id",
            keep="first",
        )
    )

    # -----------------------------------------------------
    # If there were too few alternative candidates,
    # backfill remaining positions using the next highest
    # relevance candidates.
    # -----------------------------------------------------

    if len(pool) < pool_size:
        selected_ids = set(
            pool["track_id"]
        )

        backfill = (
            ranked_candidates[
                ~ranked_candidates[
                    "track_id"
                ].isin(
                    selected_ids
                )
            ]
            .head(
                pool_size
                - len(pool)
            )
        )

        pool = pd.concat(
            [
                pool,
                backfill,
            ],
            ignore_index=True,
        )

    return (
        pool
        .head(pool_size)
        .copy()
    )