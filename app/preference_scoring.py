def _normalize_values(
    values: list[str] | None,
) -> set[str]:
    if not values:
        return set()

    return {
        str(value).strip().lower()
        for value in values
        if str(value).strip()
    }


def _artist_names(
    artists: str,
) -> set[str]:
    return {
        artist.strip().lower()
        for artist in str(artists).split(";")
        if artist.strip()
    }


def calculate_preference_score(
    track_genre: str,
    artists: str,
    preferred_genres: list[str] | None = None,
    preferred_artists: list[str] | None = None,
) -> float:
    """
    Calculate an explicit preference score between 0 and 1.

    Genre preferences contribute 60% and artist preferences
    contribute 40% when both preference types are supplied.

    If only one preference type is supplied, that signal is
    normalized to the full 0-1 range.
    """
    genres = _normalize_values(
        preferred_genres
    )

    artists_preference = _normalize_values(
        preferred_artists
    )

    if not genres and not artists_preference:
        return 0.0

    genre_match = (
        1.0
        if str(track_genre).strip().lower()
        in genres
        else 0.0
    )

    candidate_artists = _artist_names(
        artists
    )

    artist_match = (
        1.0
        if candidate_artists
        & artists_preference
        else 0.0
    )

    genre_weight = (
        0.6
        if genres
        else 0.0
    )

    artist_weight = (
        0.4
        if artists_preference
        else 0.0
    )

    total_weight = (
        genre_weight
        + artist_weight
    )

    return (
        genre_weight * genre_match
        + artist_weight * artist_match
    ) / total_weight


def apply_preference_weight(
    contextual_relevance: float,
    preference_score: float,
    preference_strength: float,
    has_preferences: bool = True,
) -> float:
    """
    Blend contextual relevance with explicit preferences.

    Preference strength is clamped to 0-1 and can contribute
    a maximum of 35% of the resulting relevance score.
    """
    if not has_preferences:
        return contextual_relevance

    preference_strength = max(
        0.0,
        min(1.0, preference_strength),
    )

    preference_weight = (
        0.20 * preference_strength
    )

    contextual_weight = (
        1.0 - preference_weight
    )

    return (
        contextual_weight
        * contextual_relevance
        + preference_weight
        * preference_score
    )