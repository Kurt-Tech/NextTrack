from app.metadata import load_tracks, get_track


def _artist_names(artists: str) -> set[str]:
    return {
        artist.strip().lower()
        for artist in str(artists).split(";")
        if artist.strip()
    }


def recommend_tracks(
    recent_tracks: list[str],
    exploration_level: float = 0.3,
    limit: int = 10
) -> list[dict]:
    df = load_tracks()
    exploration_level = max(0.0, min(1.0, exploration_level))

    recent_track_data = []
    for track_id in recent_tracks:
        track = get_track(track_id)
        if track is not None:
            recent_track_data.append(track)

    if not recent_track_data:
        return []

    recent_genres = [track["track_genre"] for track in recent_track_data]
    recent_artist_names = set()
    for track in recent_track_data:
        recent_artist_names.update(_artist_names(track["artists"]))

    primary_genre = max(set(recent_genres), key=recent_genres.count)
    recent_genres_set = set(recent_genres)

    candidates = df[~df["track_id"].isin(recent_tracks)].copy()

    candidates["popularity_score"] = candidates["popularity"].fillna(0) / 100
    candidates["genre_match"] = candidates["track_genre"].apply(
        lambda genre: 1.0
        if genre == primary_genre
        else 0.65
        if genre in recent_genres_set
        else 0.0
    )
    candidates["artist_match"] = candidates["artists"].apply(
        lambda artists: 1.0
        if _artist_names(artists) & recent_artist_names
        else 0.0
    )

    candidates["familiarity_score"] = (
        0.7 * candidates["genre_match"]
        + 0.3 * candidates["artist_match"]
    )
    candidates["diversity_score"] = (
        0.6 * (1 - candidates["genre_match"])
        + 0.4 * (1 - candidates["artist_match"])
    )
    candidates["score"] = (
        (1 - exploration_level)
        * (
            0.55 * candidates["popularity_score"]
            + 0.45 * candidates["familiarity_score"]
        )
        + exploration_level
        * (
            0.45 * candidates["popularity_score"]
            + 0.55 * candidates["diversity_score"]
        )
    )

    response_columns = [
        "track_id",
        "track_name",
        "artists",
        "album_name",
        "track_genre",
        "popularity",
        "score"
    ]

    candidates = candidates.sort_values(
        by="score",
        ascending=False
    )

    selected = []
    selected_genres = set()
    selected_artists = set()

    for _, candidate in candidates.head(max(limit * 50, 100)).iterrows():
        candidate_artists = _artist_names(candidate["artists"])
        genre_repeat = candidate["track_genre"] in selected_genres
        artist_repeat = bool(candidate_artists & selected_artists)
        repeat_penalty = exploration_level * (
            0.08 * genre_repeat
            + 0.12 * artist_repeat
        )

        candidate = candidate.copy()
        candidate["score"] = round(candidate["score"] - repeat_penalty, 4)
        selected.append(candidate)

        selected_genres.add(candidate["track_genre"])
        selected_artists.update(candidate_artists)

    selected = sorted(
        selected,
        key=lambda track: track["score"],
        reverse=True
    )

    return [
        {column: track[column] for column in response_columns}
        for track in selected[:limit]
    ]

