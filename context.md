# NextTrack Application Context

## 1. Project Overview

| Area | Details |
| --- | --- |
| Application | NextTrack API, a diversity-aware music recommendation service. |
| Audience | Developers or client applications that need music recommendations from a local Spotify-style track dataset. |
| Primary use case | Accept a list of recently played track IDs and return recommended tracks balanced between familiarity and exploration. |
| Runtime | Python FastAPI application served by Uvicorn. |
| Data layer | Local CSV files loaded with pandas; no database or ORM is currently used. |
| Core libraries | FastAPI, Pydantic, pandas, numpy, uvicorn. |
| Current API version | `0.1.0` in `app/main.py`. |

## 2. Repository Layout

```text
NextTrack/
|-- app/
|   |-- __init__.py
|   |-- main.py                  # FastAPI app, request model, and active HTTP routes.
|   |-- metadata.py              # CSV loading and dataset lookup/search helpers.
|   |-- recommender.py           # Recommendation scoring and selection logic.
|   |-- models.py                # Placeholder; currently empty.
|   |-- routes.py                # Placeholder; currently empty.
|   `-- data/
|       |-- spotify_tracks_clean.csv  # Main runtime dataset loaded by metadata.py.
|       |-- spotify_tracks_raw.csv    # Raw source dataset used by clean_dataset.py.
|       |-- Raw dataset.csv           # Additional raw dataset copy.
|       `-- tracks.csv                # Small sample/auxiliary track data file.
|-- scripts/
|   |-- clean_dataset.py         # Cleans raw CSV into spotify_tracks_clean.csv.
|   |-- test_metadata.py         # Script-style smoke checks for metadata helpers.
|   |-- test_recommender.py      # Script-style smoke check for recommendations.
|   `-- __init__.py
|-- requirements.txt             # Pinned Python dependencies.
|-- .gitignore
`-- context.md
```

## 3. Domain Model

This project does not define database tables. The domain model is represented by rows in `app/data/spotify_tracks_clean.csv`, loaded into a pandas `DataFrame`.

### Track Entity

| Field | Role | Notes |
| --- | --- | --- |
| `track_id` | Primary key | Spotify-style track identifier; used for lookup, exclusion, and recommendation input. |
| `track_name` | Display field | Track title. |
| `artists` | Display/scoring field | Artist names stored as text. Recommendation logic splits multiple artists on `;`. |
| `album_name` | Display field | Album title. |
| `track_genre` | Scoring/search field | Normalized to lowercase by cleaning/loading code. |
| `popularity` | Scoring field | Expected numeric 0-100; converted to `popularity_score` during recommendation. |
| Audio feature columns | Metadata | Includes `duration_ms`, `explicit`, `danceability`, `energy`, `key`, `loudness`, `mode`, `speechiness`, `acousticness`, `instrumentalness`, `liveness`, `valence`, `tempo`, and `time_signature`. |
| `search_text` | Runtime helper | Added in `load_tracks()` by combining title, artists, and genre. Not persisted as a source column. |

### ASCII ERD

```text
+------------------------------+
| Track                        |
+------------------------------+
| PK track_id                  |
| track_name                   |
| artists                      |
| album_name                   |
| track_genre                  |
| popularity                   |
| audio feature columns...     |
+------------------------------+
```

There are currently no foreign key relationships, user accounts, playlists, sessions, or persisted recommendation records.

## 4. API Surface And Application Boundaries

The active API is declared in `app/main.py`.

| Method | Path | Request | Response |
| --- | --- | --- | --- |
| `GET` | `/` | None | `{"message": "NextTrack API is running"}` |
| `POST` | `/recommend` | `RecommendationRequest` JSON | Input echo plus `recommendations` list. |

### Request Model

```json
{
  "recent_tracks": ["5SuOikwiRyPMVoIQDJUgSV"],
  "exploration_level": 0.3
}
```

| Field | Type | Default | Notes |
| --- | --- | --- | --- |
| `recent_tracks` | `list[str]` | Required | Track IDs used as the taste seed. Unknown IDs are ignored. |
| `exploration_level` | `float` | `0.3` | Clamped inside `recommend_tracks()` to the range `0.0` through `1.0`. |

### Recommendation Response Shape

```json
{
  "recent_tracks": ["5SuOikwiRyPMVoIQDJUgSV"],
  "exploration_level": 0.3,
  "recommendations": [
    {
      "track_id": "string",
      "track_name": "string",
      "artists": "string",
      "album_name": "string",
      "track_genre": "string",
      "popularity": 73,
      "score": 0.1234
    }
  ]
}
```

## 5. Architectural Patterns And Conventions

| Concern | Current convention |
| --- | --- |
| App entrypoint | `app/main.py` owns the `FastAPI` instance and currently defines all active routes inline. |
| Request validation | Pydantic models are used directly in `app/main.py`. `app/models.py` exists but is empty. |
| Data access | `app/metadata.py` loads `spotify_tracks_clean.csv` with pandas. It exposes helper functions such as `get_track()`, `search_tracks()`, and `get_dataset_summary()`. |
| Data caching | `load_tracks()` is decorated with `@lru_cache(maxsize=1)`, so CSV data is loaded once per Python process. |
| Business logic | Recommendation scoring lives in `app/recommender.py`; it calls metadata helpers rather than reading files directly except through `load_tracks()`. |
| Recommendation algorithm | Scores candidates using popularity, genre familiarity, artist familiarity, diversity, and an exploration-level weighting. Recently supplied track IDs are excluded from candidates. |
| Error handling | Minimal. Missing dataset raises `FileNotFoundError`; unknown input track IDs are ignored; if none of the input IDs are found, recommendations return `[]`. |
| Route organization | `app/routes.py` exists but is empty, so do not assume router modules are wired yet. |
| Naming | Track fields follow the CSV column names, mostly snake_case. |
| Data normalization | Text fields are stripped; `track_genre` is lowercased during load and cleaning. |
| Persistence | No writes occur during normal API requests. Dataset generation is handled separately by `scripts/clean_dataset.py`. |

When extending the application, preserve the separation between metadata/dataframe helpers and recommendation scoring. If adding more routes, either keep the current inline style in `app/main.py` for small changes or deliberately wire `app/routes.py` with an `APIRouter`.

## 6. Build, Run, And Test Commands

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Smoke-test helper modules:

```powershell
python scripts\test_metadata.py
python scripts\test_recommender.py
```

Regenerate the cleaned dataset from the raw dataset:

```powershell
python scripts\clean_dataset.py
```

Example API call once the server is running:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/recommend -ContentType "application/json" -Body '{"recent_tracks":["5SuOikwiRyPMVoIQDJUgSV","4qPNDBW1i3p13qLCt0Ki3A"],"exploration_level":0.3}'
```

## 7. Environment Variables

No environment variables are currently read by the application code.

| Variable | Default | Description |
| --- | --- | --- |
| None | N/A | Configuration is currently hard-coded in Python modules. `DATA_PATH` points to `app/data/spotify_tracks_clean.csv`. |

`python-dotenv` is present in `requirements.txt`, but no `.env` loading is currently implemented.

## 8. Testing Strategy

The repo currently uses script-style smoke tests rather than a formal test framework.

| Area | Current approach |
| --- | --- |
| Metadata helpers | `python scripts\test_metadata.py` prints dataset summary, genres, searches, genre lookup, artist lookup, and random tracks. |
| Recommender | `python scripts\test_recommender.py` calls `recommend_tracks()` with known track IDs and prints results. |
| API routes | No automated route tests currently exist. |
| Test framework | No pytest/unittest tests are currently present. |
| Fixtures | No test fixtures; scripts use the real CSV dataset in `app/data/spotify_tracks_clean.csv`. |
| Mocking | No mocking strategy is currently in place. |
| Test database | None; the app is CSV-backed. |

For future tests, prefer focused pytest tests around `metadata.py`, `recommender.py`, and FastAPI route behavior using `TestClient`. Consider clearing `load_tracks.cache_clear()` in tests if data-loading behavior is changed or monkeypatched.

## 9. Known Gaps And Constraints

| Gap or constraint | Impact |
| --- | --- |
| No authentication or authorization | All routes are public when served. |
| No database | Track data is static CSV data loaded into memory. There are no migrations, transactions, or relational constraints. |
| Empty `app/models.py` and `app/routes.py` | Do not assume a layered model/router architecture already exists. |
| Minimal input validation | `recent_tracks` is typed but not constrained for length; `exploration_level` is clamped in business logic, not rejected by request validation. |
| No formal error response design | Exceptions such as missing dataset files are not converted into custom HTTP errors. |
| No API tests | Route regressions would currently be caught manually unless tests are added. |
| Real dataset used in smoke tests | Tests depend on local CSV files being present and can be slower than fixture-based tests. |
| In-memory cache | Dataset changes on disk are not picked up until process restart or `load_tracks.cache_clear()`. |
| Recommendation output may include pandas/numpy scalar types | If serialization issues appear, convert values to native Python types before returning responses. |
| Artist parsing assumes semicolon delimiters | Any dataset rows using a different multi-artist delimiter may reduce artist-match accuracy. |
