from collections import Counter

from app.audio_similarity import (
    calculate_cosine_similarity,
    get_normalized_audio_features,
)
from app.diversity_reranking import (
    rerank_for_diversity,
)
from app.metadata import (
    get_track,
    load_tracks,
)
from app.preference_scoring import (
    apply_preference_weight,
    calculate_preference_score,
)

from app.candidate_pool import (
    build_candidate_pool,
)


def _artist_names(
    artists: str,
) -> set[str]:
    """
    Convert the semicolon-separated artist field into
    a normalized set of artist names.
    """

    return {
        artist.strip().lower()
        for artist in str(artists).split(";")
        if artist.strip()
    }


def _get_primary_genre(
    genres: list[str],
) -> str:
    """
    Return the most frequently occurring genre.

    Counter.most_common preserves the first encountered
    value when counts are tied.
    """

    return Counter(
        genres
    ).most_common(1)[0][0]


def recommend_tracks_enhanced(
    recent_tracks: list[str],
    exploration_level: float = 0.3,
    limit: int = 10,
    preferred_genres: list[str] | None = None,
    preferred_artists: list[str] | None = None,
    preference_strength: float = 0.0,
) -> list[dict]:
    """
    Generate context-aware, preference-aware and
    diversity-aware music recommendations.

    Processing stages:

    1. Validate input.
    2. Build a listening-context vector from recent tracks.
    3. Calculate contextual relevance from:
       - audio similarity
       - familiarity
       - popularity
    4. Optionally apply explicit genre/artist preferences.
    5. Build a high-relevance candidate pool.
    6. At zero exploration, preserve the relevance ranking.
    7. At non-zero exploration, apply continuous
       diversity-aware greedy reranking.
    8. Return the public API recommendation fields.
    """

    # -----------------------------------------------------
    # Input validation
    # -----------------------------------------------------

    if limit < 1:
        raise ValueError(
            "limit must be at least 1"
        )

    exploration_level = max(
        0.0,
        min(
            1.0,
            exploration_level,
        ),
    )

    preference_strength = max(
        0.0,
        min(
            1.0,
            preference_strength,
        ),
    )

    # -----------------------------------------------------
    # Determine whether explicit preferences are active
    # -----------------------------------------------------

    has_genre_preferences = any(
        str(genre).strip()
        for genre in (
            preferred_genres
            or []
        )
    )

    has_artist_preferences = any(
        str(artist).strip()
        for artist in (
            preferred_artists
            or []
        )
    )

    has_preferences = (
        has_genre_preferences
        or has_artist_preferences
    )

    preference_active = (
        has_preferences
        and preference_strength > 0.0
    )

    # -----------------------------------------------------
    # Load dataset and resolve recent tracks
    # -----------------------------------------------------

    df = load_tracks()

    recent_track_data = []

    for track_id in recent_tracks:
        track = get_track(
            track_id
        )

        if track is not None:
            recent_track_data.append(
                track
            )

    if not recent_track_data:
        return []

    valid_recent_ids = [
        track["track_id"]
        for track in recent_track_data
    ]

    # -----------------------------------------------------
    # Build recent listening context
    # -----------------------------------------------------

    recent_genres = [
        track["track_genre"]
        for track in recent_track_data
    ]

    recent_genres_set = set(
        recent_genres
    )

    primary_genre = (
        _get_primary_genre(
            recent_genres
        )
    )

    recent_artist_names = set()

    for track in recent_track_data:
        recent_artist_names.update(
            _artist_names(
                track["artists"]
            )
        )

    # -----------------------------------------------------
    # Audio feature context
    # -----------------------------------------------------

    normalized_features = (
        get_normalized_audio_features()
    )

    recent_feature_vectors = (
        normalized_features.loc[
            valid_recent_ids
        ]
    )

    context_vector = (
        recent_feature_vectors
        .mean(axis=0)
        .to_numpy(dtype=float)
    )

    # -----------------------------------------------------
    # Candidate set
    # -----------------------------------------------------

    candidates = df[
        ~df["track_id"].isin(
            valid_recent_ids
        )
    ].copy()

    candidate_vectors = (
        normalized_features
        .loc[
            candidates["track_id"]
        ]
        .to_numpy(dtype=float)
    )

    # -----------------------------------------------------
    # Audio similarity
    # -----------------------------------------------------

    candidates[
        "audio_similarity"
    ] = calculate_cosine_similarity(
        context_vector,
        candidate_vectors,
    )

    # -----------------------------------------------------
    # Popularity
    # -----------------------------------------------------

    candidates[
        "popularity_score"
    ] = (
        candidates["popularity"]
        .fillna(0)
        / 100
    )

    # -----------------------------------------------------
    # Genre familiarity
    # -----------------------------------------------------

    candidates[
        "genre_match"
    ] = (
        candidates["track_genre"]
        .apply(
            lambda genre:
            1.0
            if genre == primary_genre
            else 0.65
            if genre in recent_genres_set
            else 0.0
        )
    )

    # -----------------------------------------------------
    # Artist familiarity
    # -----------------------------------------------------

    candidates[
        "artist_match"
    ] = (
        candidates["artists"]
        .apply(
            lambda artists:
            1.0
            if (
                _artist_names(
                    artists
                )
                & recent_artist_names
            )
            else 0.0
        )
    )

    candidates[
        "familiarity_score"
    ] = (
        0.70
        * candidates["genre_match"]
        + 0.30
        * candidates["artist_match"]
    )

    # -----------------------------------------------------
    # Phase 2 contextual relevance
    #
    # IMPORTANT:
    # Preserve this formula unchanged so that the
    # established Phase 2 contextual model remains intact.
    # -----------------------------------------------------

    candidates[
        "contextual_relevance_score"
    ] = (
        0.60
        * candidates[
            "audio_similarity"
        ]
        + 0.25
        * candidates[
            "familiarity_score"
        ]
        + 0.15
        * candidates[
            "popularity_score"
        ]
    )

    # -----------------------------------------------------
    # Phase 3 explicit preference weighting
    # -----------------------------------------------------

    if preference_active:
        candidates[
            "preference_score"
        ] = [
            calculate_preference_score(
                track_genre=genre,
                artists=artists,
                preferred_genres=(
                    preferred_genres
                ),
                preferred_artists=(
                    preferred_artists
                ),
            )
            for genre, artists
            in zip(
                candidates[
                    "track_genre"
                ],
                candidates[
                    "artists"
                ],
            )
        ]

        candidates[
            "relevance_score"
        ] = apply_preference_weight(
            contextual_relevance=(
                candidates[
                    "contextual_relevance_score"
                ]
            ),
            preference_score=(
                candidates[
                    "preference_score"
                ]
            ),
            preference_strength=(
                preference_strength
            ),
            has_preferences=True,
        )

    else:
        candidates[
            "preference_score"
        ] = 0.0

        candidates[
            "relevance_score"
        ] = (
            candidates[
                "contextual_relevance_score"
            ]
        )

    # -----------------------------------------------------
    # Phase 4 candidate pool
    #
    # Only high-relevance candidates are passed into the
    # greedy diversity reranker. This keeps the reranker
    # computationally practical while preventing highly
    # irrelevant tracks from entering the recommendation
    # list purely because they are different.
    # -----------------------------------------------------

    candidate_pool = (
    build_candidate_pool(
        candidates=candidates,
        primary_genre=primary_genre,
        exploration_level=(
            exploration_level
        ),
        limit=limit,
    )
)

    # -----------------------------------------------------
    # Zero-exploration invariant
    #
    # At exploration_level == 0, bypass the diversity
    # reranker completely. This gives an explicit
    # architectural guarantee that zero exploration uses
    # the relevance ranking without a diversity penalty.
    # -----------------------------------------------------

    if exploration_level == 0.0:
        selected = (
            candidate_pool
            .head(limit)
            .to_dict(
                orient="records"
            )
        )

        for track in selected:
            track["score"] = round(
                float(
                    track[
                        "relevance_score"
                    ]
                ),
                4,
            )

    # -----------------------------------------------------
    # Continuous diversity-aware reranking
    # -----------------------------------------------------

    else:
        # The reranker requires each candidate's
        # normalized audio vector so it can calculate
        # pairwise audio redundancy between candidates
        # already selected and those still remaining.

        candidate_pool[
            "audio_vector"
        ] = [
            normalized_features
            .loc[track_id]
            .to_numpy(
                dtype=float
            )
            for track_id
            in candidate_pool[
                "track_id"
            ]
        ]

        candidate_records = (
            candidate_pool
            .to_dict(
                orient="records"
            )
        )

        selected = (
            rerank_for_diversity(
                candidates=(
                    candidate_records
                ),
                exploration_level=(
                    exploration_level
                ),
                limit=limit,
                maximum_diversity_weight=0.35,
            )
        )

        # The greedy reranker evaluates each track against
        # a different selected-list state. Therefore the
        # returned selection order itself is the ranking.
        #
        # DO NOT sort this list again by score.

        for track in selected:
            track["score"] = round(
                float(
                    track[
                        "diversity_selection_score"
                    ]
                ),
                4,
            )

    # -----------------------------------------------------
    # Public response
    #
    # Internal values such as:
    # - audio_vector
    # - relevance_score
    # - redundancy_score
    # - diversity_selection_score
    #
    # are intentionally excluded from the API response.
    # -----------------------------------------------------

    response_columns = [
        "track_id",
        "track_name",
        "artists",
        "album_name",
        "track_genre",
        "popularity",
        "audio_similarity",
        "score",
    ]

    return [
        {
            column: (
                float(
                    track[column]
                )
                if column in {
                    "audio_similarity",
                    "score",
                }
                else track[column]
            )
            for column
            in response_columns
        }
        for track in selected
    ]