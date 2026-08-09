import numpy as np

from app.audio_similarity import (
    AUDIO_FEATURES,
    build_context_vector,
    calculate_cosine_similarity,
    get_normalized_audio_features,
)


KNOWN_TRACKS = [
    "5SuOikwiRyPMVoIQDJUgSV",
    "4qPNDBW1i3p13qLCt0Ki3A",
    "1iJBSr7s7jYXzM8EGcbK5b",
]


def test_normalized_audio_features_load():
    normalized = get_normalized_audio_features()

    assert normalized is not None
    assert not normalized.empty


def test_normalized_audio_features_have_expected_columns():
    normalized = get_normalized_audio_features()

    assert list(normalized.columns) == AUDIO_FEATURES


def test_normalized_features_have_mean_near_zero():
    normalized = get_normalized_audio_features()

    means = normalized.mean()

    assert np.allclose(
        means.to_numpy(),
        0.0,
        atol=1e-10,
    )


def test_normalized_features_have_standard_deviation_near_one():
    normalized = get_normalized_audio_features()

    standard_deviations = normalized.std(ddof=0)

    assert np.allclose(
        standard_deviations.to_numpy(),
        1.0,
        atol=1e-10,
    )


def test_context_vector_has_correct_dimensions():
    context = build_context_vector(
        KNOWN_TRACKS
    )

    assert context is not None
    assert context.shape == (
        len(AUDIO_FEATURES),
    )


def test_context_vector_contains_finite_values():
    context = build_context_vector(
        KNOWN_TRACKS
    )

    assert context is not None
    assert np.all(np.isfinite(context))


def test_unknown_tracks_return_no_context():
    context = build_context_vector(
        ["not-a-real-track"]
    )

    assert context is None


def test_unknown_tracks_are_ignored_with_valid_tracks():
    mixed_context = build_context_vector(
        [
            "not-a-real-track",
            KNOWN_TRACKS[0],
        ]
    )

    valid_context = build_context_vector(
        [KNOWN_TRACKS[0]]
    )

    assert np.allclose(
        mixed_context,
        valid_context,
    )


def test_identical_vector_has_maximum_similarity():
    vector = np.array(
        [0.2, 0.5, -0.4, 1.0]
    )

    similarities = calculate_cosine_similarity(
        vector,
        np.array([vector]),
    )

    assert np.isclose(
        similarities[0],
        1.0,
    )


def test_similarity_is_between_zero_and_one():
    context = build_context_vector(
        KNOWN_TRACKS
    )

    normalized = get_normalized_audio_features()

    candidates = (
        normalized
        .head(100)
        .to_numpy()
    )

    similarities = calculate_cosine_similarity(
        context,
        candidates,
    )

    assert np.all(similarities >= 0.0)
    assert np.all(similarities <= 1.0)