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