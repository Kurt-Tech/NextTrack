from app.metadata import (
    get_dataset_summary,
    get_track,
    get_tracks_by_genre,
    get_tracks_by_artist,
    search_tracks,
    get_random_tracks,
    get_all_genres,
)

print("\nDataset Summary")
print(get_dataset_summary())

print("\nFirst 10 Genres")
print(get_all_genres()[:10])

print("\nSearch: comedy")
for track in search_tracks("comedy", limit=3):
    print(track["track_id"], "-", track["track_name"], "-", track["artists"])

print("\nGenre: acoustic")
for track in get_tracks_by_genre("acoustic", limit=3):
    print(track["track_id"], "-", track["track_name"], "-", track["artists"])

print("\nArtist: Gen Hoshino")
for track in get_tracks_by_artist("Gen Hoshino", limit=3):
    print(track["track_id"], "-", track["track_name"], "-", track["artists"])

print("\nRandom Tracks")
for track in get_random_tracks(limit=3):
    print(track["track_id"], "-", track["track_name"], "-", track["artists"])