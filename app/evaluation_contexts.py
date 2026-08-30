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
            "0FB5ILDICqwK6xj7W1RP9u",
            "1r9xUipOqoNwggBpENDsvJ",
            "4u7EnebtmKWzUH433cf5Qv",
        ],
    },
    "hip-hop": {
        "name": "Hip-Hop",
        "recent_tracks": [
            "038oBXqL9ttCHHZmNrYxQk",
            "7lQ8MOhq6IN2w8EYcFNSUk",
            "0VgkVdmE4gld66l8iyGjgx",
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
            "2SpEHTbUuebeLkgs9QB7Ue",
            "6foY66mWZN0pSRjZ408c00",
            "0HGpVO2aqh9Dadfs90S1mP",
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