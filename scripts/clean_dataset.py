from pathlib import Path
import pandas as pd

# ---------------------------------
# File Paths
# ---------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FOLDER = PROJECT_ROOT / "app" / "data"

RAW_DATA = DATA_FOLDER / "spotify_tracks_raw.csv"

CLEAN_DATA = DATA_FOLDER / "spotify_tracks_clean.csv"

# ---------------------------------
# Load Dataset
# ---------------------------------

print("Loading dataset...")

df = pd.read_csv(RAW_DATA)

print(f"Loaded {len(df):,} records.")

# ---------------------------------
# Dataset Information
# ---------------------------------

print("\nDataset Information")
print("-" * 40)

print(df.info())

print("\nMissing Values")

print(df.isnull().sum())

print("\nDuplicate Track IDs")

duplicates = df.duplicated(subset="track_id").sum()

print(duplicates)

# ---------------------------------
# Remove Duplicate Tracks
# ---------------------------------

print("\nRemoving duplicate tracks...")

before = len(df)

df = df.drop_duplicates(subset="track_id")

removed_duplicates = before - len(df)

print(f"Removed {removed_duplicates:,} duplicate tracks.")

# ---------------------------------
# Remove Missing Values
# ---------------------------------

print("\nRemoving incomplete records...")

before = len(df)

df = df.dropna(
    subset=[
        "track_id",
        "track_name",
        "artists",
        "track_genre"
    ]
)

removed_missing = before - len(df)

print(f"Removed {removed_missing:,} incomplete records.")

# ---------------------------------
# Clean Text
# ---------------------------------

print("\nCleaning text fields...")

text_columns = [
    "track_name",
    "artists",
    "album_name",
    "track_genre"
]

for column in text_columns:
    df[column] = (
        df[column]
        .astype(str)
        .str.strip()
    )

df["track_genre"] = df["track_genre"].str.lower()

# ---------------------------------
# Standardize Column Names
# ---------------------------------

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
)

# ---------------------------------
# Save Clean Dataset
# ---------------------------------

df.to_csv(CLEAN_DATA, index=False)

print("\nDataset saved successfully!")

print(CLEAN_DATA)

print("\nCleaning Summary")
print("-" * 40)

print(f"Final Records : {len(df):,}")

print(f"Columns       : {len(df.columns)}")