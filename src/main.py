
import matplotlib
import pandas as pd # CSV data
import numpy as np # math / stats
import matplotlib.pyplot as plt # visulize results
import requests # to fetch live data
import sys


from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

RAW_PATH = BASE_DIR / "data" / "raw" / "E0.csv"
CLEAN_PATH = BASE_DIR / "data" / "clean_matches.csv"
SEASON_LABEL = "2025-26"


# parsing e0 csv for new clean_matches
def clean_raw_csv(raw_path: Path = RAW_PATH, clean_path: Path = CLEAN_PATH, season: str = SEASON_LABEL):
    #read csv
    df = pd.read_csv(RAW_PATH)
    #what we need
    keep = df[["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"]].copy()
    keep = keep.rename(columns={
        "Date": "date",
        "HomeTeam": "home_team",
        "AwayTeam": "away_team",
        "FTHG": "home_goals",
        "FTAG": "away_goals"
    })

    # getting rid of / in the date
    keep["date"] = pd.to_datetime(keep["date"], dayfirst=True).dt.strftime("%Y-%m-%d")
    #season column
    keep["season"] = season

    clean_path.parent.mkdir(parents=True, exist_ok=True)
    keep.to_csv(clean_path, index=False)
    print(f"✅ Cleaned file written to {clean_path} ({len(keep)} rows)")



if __name__ == "__main__":
    # TEMP: call the cleaner directly
    clean_raw_csv()