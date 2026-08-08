from app.metadata import load_tracks, get_dataset_summary, get_track


def test_dataset_loads():
    df = load_tracks()

    assert df is not None
    assert not df.empty


def test_dataset_contains_required_columns():
    df = load_tracks()

    required_columns = {
        "track_id",
        "track_name",
        "artists",
        "album_name",
        "track_genre",
        "popularity",
    }

    assert required_columns.issubset(df.columns)


def test_dataset_summary():
    summary = get_dataset_summary()

    assert summary["total_tracks"] > 0
    assert summary["total_genres"] > 0
    assert summary["total_artists"] > 0


def test_known_track_lookup():
    track = get_track("5SuOikwiRyPMVoIQDJUgSV")

    assert track is not None
    assert track["track_id"] == "5SuOikwiRyPMVoIQDJUgSV"