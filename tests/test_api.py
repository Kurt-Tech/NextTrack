from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "NextTrack API is running"
    }


def test_recommend_endpoint_valid_request():
    payload = {
        "recent_tracks": [
            "5SuOikwiRyPMVoIQDJUgSV",
            "4qPNDBW1i3p13qLCt0Ki3A",
        ],
        "exploration_level": 0.3,
    }

    response = client.post(
        "/recommend",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert "recent_tracks" in data
    assert "exploration_level" in data
    assert "recommendations" in data

    assert isinstance(data["recommendations"], list)
    assert len(data["recommendations"]) > 0


def test_recommendations_have_expected_fields():
    payload = {
        "recent_tracks": [
            "5SuOikwiRyPMVoIQDJUgSV",
        ],
        "exploration_level": 0.3,
    }

    response = client.post(
        "/recommend",
        json=payload,
    )

    assert response.status_code == 200

    recommendations = response.json()["recommendations"]

    assert len(recommendations) > 0

    required_fields = {
        "track_id",
        "track_name",
        "artists",
        "album_name",
        "track_genre",
        "popularity",
        "score",
    }

    assert required_fields.issubset(
        recommendations[0].keys()
    )


def test_recent_tracks_are_excluded():
    recent_tracks = [
        "5SuOikwiRyPMVoIQDJUgSV",
        "4qPNDBW1i3p13qLCt0Ki3A",
    ]

    payload = {
        "recent_tracks": recent_tracks,
        "exploration_level": 0.3,
    }

    response = client.post(
        "/recommend",
        json=payload,
    )

    assert response.status_code == 200

    recommendations = response.json()["recommendations"]

    recommended_ids = {
        recommendation["track_id"]
        for recommendation in recommendations
    }

    assert recommended_ids.isdisjoint(recent_tracks)


def test_missing_recent_tracks_is_rejected():
    payload = {
        "exploration_level": 0.3,
    }

    response = client.post(
        "/recommend",
        json=payload,
    )

    assert response.status_code == 422

def test_recommend_endpoint_accepts_preferences():
    response = client.post(
        "/recommend",
        json={
            "recent_tracks": [
                "5SuOikwiRyPMVoIQDJUgSV"
            ],
            "exploration_level": 0.3,
            "preferred_genres": [
                "rock"
            ],
            "preferred_artists": [
                "Bryan Adams"
            ],
            "preference_strength": 0.75,
        },
    )

    assert response.status_code == 200

def test_recommend_endpoint_preferences_are_optional():
    response = client.post(
        "/recommend",
        json={
            "recent_tracks": [
                "5SuOikwiRyPMVoIQDJUgSV"
            ],
            "exploration_level": 0.3,
        },
    )

    assert response.status_code == 200

def test_zero_preference_strength_preserves_api_results():
    without_preferences = client.post(
        "/recommend",
        json={
            "recent_tracks": [
                "5SuOikwiRyPMVoIQDJUgSV"
            ],
            "exploration_level": 0.3,
        },
    )

    zero_strength = client.post(
        "/recommend",
        json={
            "recent_tracks": [
                "5SuOikwiRyPMVoIQDJUgSV"
            ],
            "exploration_level": 0.3,
            "preferred_genres": [
                "rock"
            ],
            "preference_strength": 0.0,
        },
    )

    assert (
        zero_strength.json()
        == without_preferences.json()
    )

def test_active_preference_changes_api_results():
    without_preferences = client.post(
        "/recommend",
        json={
            "recent_tracks": [
                "5SuOikwiRyPMVoIQDJUgSV"
            ],
            "exploration_level": 0.3,
        },
    )

    with_preferences = client.post(
        "/recommend",
        json={
            "recent_tracks": [
                "5SuOikwiRyPMVoIQDJUgSV"
            ],
            "exploration_level": 0.3,
            "preferred_genres": [
                "rock"
            ],
            "preference_strength": 1.0,
        },
    )

    assert (
        with_preferences.json()
        != without_preferences.json()
    )

def test_evaluation_contexts_returns_six_contexts():
    response = client.get("/evaluation/contexts")

    assert response.status_code == 200

    data = response.json()

    assert "contexts" in data
    assert len(data["contexts"]) == 6

    context_ids = {
        context["id"]
        for context in data["contexts"]
    }

    assert context_ids == {
        "acoustic",
        "rock",
        "hip-hop",
        "classical",
        "country",
        "electronic",
    }


def test_evaluation_contexts_have_three_valid_tracks():
    response = client.get("/evaluation/contexts")

    assert response.status_code == 200

    contexts = response.json()["contexts"]

    for context in contexts:
        assert len(context["recent_tracks"]) == 3

        for track in context["recent_tracks"]:
            assert track["track_id"]
            assert track["track_name"]
            assert track["artists"]
            assert track["track_genre"]

def test_evaluation_page_loads():
    response = client.get("/evaluation")

    assert response.status_code == 200
    assert "NextTrack" in response.text
    assert "Music Recommendation Evaluation" in response.text


def test_evaluation_stylesheet_loads():
    response = client.get(
        "/static/evaluation.css"
    )

    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]

def test_evaluation_javascript_loads():
    response = client.get(
        "/static/evaluation.js"
    )

    assert response.status_code == 200
    assert (
        "javascript"
        in response.headers["content-type"]
    )

def test_evaluation_page_loads():
    response = client.get("/evaluation")

    assert response.status_code == 200
    assert "NextTrack" in response.text
    assert "Music Recommendation Evaluation" in response.text
    assert 'id="exploration-level"' in response.text
    assert 'step="0.25"' in response.text

def test_evaluation_page_has_generate_controls():
    response = client.get("/evaluation")

    assert response.status_code == 200

    assert (
        'id="generate-button"'
        in response.text
    )

    assert (
        'id="recommendation-results"'
        in response.text
    )

    assert (
        'id="recommendation-status"'
        in response.text
    )

def test_evaluation_javascript_contains_spotify_links():
    response = client.get(
        "/static/evaluation.js"
    )

    assert response.status_code == 200

    assert (
        "https://open.spotify.com/track/"
        in response.text
    )

def test_evaluation_genres_returns_genres():
    response = client.get(
        "/evaluation/genres"
    )

    assert response.status_code == 200

    data = response.json()

    assert "genres" in data
    assert len(data["genres"]) > 0

    assert "rock" in data["genres"]
    assert "acoustic" in data["genres"]
    assert "electronic" in data["genres"]

def test_evaluation_page_has_preference_controls():
    response = client.get("/evaluation")

    assert response.status_code == 200

    assert (
        'id="preferred-genre"'
        in response.text
    )

    assert (
        'id="preference-strength"'
        in response.text
    )