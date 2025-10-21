
import matplotlib
import pandas as pd # CSV data
import numpy as np # math / stats
import matplotlib.pyplot as plt # visulize results
import requests # to fetch live data
import sys
from pathlib import Path
from .elo_model import train_elo



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

    #Goals are numbers and not containing errors( non-numeric values from csv into NaN)
    keep["home_goals"] = pd.to_numeric(keep["home_goals"], errors="coerce")
    keep["away_goals"] = pd.to_numeric(keep["away_goals"], errors="coerce")

    # check every row( labled : r) to check for NaN; if not then Finished , one or both missing means it's a future game labled SCHEDULEDkeep
    keep["status"] = np.where(
        keep["home_goals"].notna() & keep["away_goals"].notna(),
        "FINISHED",
        "SCHEDULED"
    )

    # making match id's ( easy to refrence / remove spaces / random symbols)
    keep["match_id"] = (
        keep["date"] + "_" +
        keep["home_team"].str.replace(" ","",regex=False) + "_" +
        keep["away_team"].str.replace(" ","",regex=False)
    )

    #reording coloums and sorting / removing dupes
    cols = ["match_id","date", "season", "home_team", "away_team", "home_goals", "away_goals", "status"]
    keep = keep[cols].sort_values(["date","home_team","away_team"])
    #dupes
    keep = keep.drop_duplicates(subset=["date","home_team","away_team"], keep="first")


    #allows to see summary
    n_total = len(keep)
    n_finished = int((keep["status"] == "FINISHED").sum())
    n_sched = n_total - n_finished
    n_teams = len(set(keep["home_team"]).union(set(keep["away_team"])))
    first_date = keep["date"].min() if n_total else "NA"
    last_date = keep["date"].max() if n_total else "NA"
    print(
        f" Wrote {clean_path} | rows={n_total} finished={n_finished} scheduled={n_sched} teams={n_teams} range={first_date} → {last_date}")




    clean_path.parent.mkdir(parents=True, exist_ok=True)
    keep.to_csv(clean_path, index=False)

if __name__ == "__main__":
    # add mode
    mode = sys.argv[1] if len(sys.argv) > 1 else "init-data"
    if mode == "init-data":
        clean_raw_csv()
    elif mode == "train-elo":
        ratings_path = BASE_DIR / "data"  / "ratings.csv"
        train_elo(clean_path=CLEAN_PATH, out_path=ratings_path)
    else:
        print("Usage:\n python -m src.main init-data\n python -m src.main train-elo")