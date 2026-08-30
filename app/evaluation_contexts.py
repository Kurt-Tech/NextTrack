"""Predefined listening contexts used by the evaluation interface.

These contexts reuse the fixed recent-track seeds used during the
offline recommendation evaluation so that participant evaluation can
be compared directly with the project's existing technical results.
"""


EVALUATION_CONTEXTS = {
    "acoustic": {
        "name": "Acoustic",
        "recent_tracks": [
            "5SuOikwiRyPMVoIQDJUgSV",
            "4qPNDBW1i3p13qLCt0Ki3A",
            "1iJBSr7s7jYXzM8EGcbK5b",
        ],
    },
    "rock": {
        "name": "Rock",
        "recent_tracks": [
            "2nLtzopw4rPReszdYBJU6h",
            "4TMhakloPMPS84lNHNTSa3",
            "1AhDOtG9vPSOmsWgNW0BEY",
        ],
    },
    "hip-hop": {
        "name": "Hip-Hop",
        "recent_tracks": [
            "20XdEFyaUR9C7aDIdq2OAd",
            "68pWLkspLFIfIPPtzyTkQy",
            "2lUirvUhqfBqJzUvk4tLoK",
        ],
    },
    "classical": {
        "name": "Classical",
        "recent_tracks": [
            "7wrYBASu0OoxoDErd4Edxd",
            "72HdutlIHBZJ7WT1xVAAZT",
            "7JGgKHHDgJCJkQCQxyHHdl",
        ],
    },
    "country": {
        "name": "Country",
        "recent_tracks": [
            "7hxZF4jETnE5Q75rKQnMjE",
            "51wQovDO0hf05pkZYvu1GI",
            "6gRACp2CvsIhc7hyw8CecQ",
        ],
    },
    "electronic": {
        "name": "Electronic",
        "recent_tracks": [
            "57kR5SniQIbsbVoIjjOUDa",
            "5SpGYwR8nzi9eMaHL5Ucyq",
            "7GlCU1ImbOyED4BW6H1TSH",
        ],
    },
}