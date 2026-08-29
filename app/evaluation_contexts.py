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
            "7DbdUf8aHSYoliSjO6LZv6",
            "1zB4vmk8tFRmM9UULNzbLB",
            "0pqnGHJpmpxLKifKRmU6WP",
        ],
    },
    "hip-hop": {
        "name": "Hip-Hop",
        "recent_tracks": [
            "1aL9518P5G72N92b48tuKw",
            "08Isz2ETWSBhvIl8UpKYsp",
            "42TMa2hgBNjte4uV7jNCnQ",
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
            "2wrJq5XKLnmhRXHIAf9xBa",
            "6AHJTA1BN7ePfChCwqph3z",
            "5eUtyONoPyfZYGrFHmZzlc",
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