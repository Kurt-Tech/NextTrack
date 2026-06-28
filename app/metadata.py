import pandas as pd 
from pathlib import Path 

DATA_PATH = Path(__file__).parent / "data" / "tracks.csv" 

def load_tracks(): 
    return pd.read_csv(DATA_PATH) 

def get_track_by_id(track_id: str): 
    tracks = load_tracks() 
    result = tracks[tracks["track_id"] == track_id] 
    
    if result.empty: return None 
    
    return result.iloc[0].to_dict()