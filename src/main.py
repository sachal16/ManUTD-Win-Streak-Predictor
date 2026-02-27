from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from .elo_model import train_elo
from .fetch_data import fetch_all
from .simulate_upcoming import compute_probs

# Base Paths
BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_PATH = BASE_DIR / "data" / "raw" / "E0.csv"
CLEAN_PATH = BASE_DIR / "data" / "clean_matches.csv"
SEASON_LABEL = "2025-26"

# Filename -> season label for multi-season data (e.g. E0_2324.csv -> 2023-24)
SEASON_FROM_FILENAME = {
    "E0_2324": "2023-24",
    "E0_2425": "2024-25",
    "E0_2526": "2025-26",
}


def _read_raw_with_season(path: Path, season: str) -> pd.DataFrame:
    """Read one raw E0 CSV and return DataFrame with required columns + season."""
    df = pd.read_csv(path)
    required = ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"]
    if not all(c in df.columns for c in required):
        return pd.DataFrame()
    keep = df[required].copy()
    keep["season"] = season
    return keep


def _gather_raw_frames() -> list[tuple[Path, str]]:
    """Find all E0*.csv in raw dir and return (path, season_label) sorted by season."""
    pairs: list[tuple[Path, str]] = []
    if not RAW_DIR.exists():
        if RAW_PATH.exists():
            pairs.append((RAW_PATH, SEASON_LABEL))
        return pairs
    for f in sorted(RAW_DIR.glob("E0*.csv")):
        stem = f.stem  # e.g. E0_2425 or E0
        season = SEASON_FROM_FILENAME.get(stem)
        if season is None and stem.startswith("E0_"):
            code = stem.replace("E0_", "")  # e.g. 2425
            if len(code) == 4 and code.isdigit():
                season = f"20{code[:2]}-{code[2:]}"  # 2425 -> 2024-25
        if season is None:
            season = SEASON_LABEL
        pairs.append((f, season))
    return sorted(pairs, key=lambda x: x[1])


# Parsing E0 CSV(s) into clean_matches (single or multi-season)
def clean_raw_csv(raw_path: Path | None = None, clean_path: Path = CLEAN_PATH):
    """Read all E0*.csv from data/raw (or single raw_path), merge by season, clean and write."""
    if raw_path is not None:
        # Single file: legacy behaviour
        frames = [_read_raw_with_season(raw_path, SEASON_LABEL)]
        if frames[0].empty:
            print(f"Invalid or missing columns in {raw_path}")
            return
    else:
        pairs = _gather_raw_frames()
        if not pairs:
            print("No E0*.csv found in data/raw/. Run fetch-data first or add E0.csv.")
            return
        frames = []
        for path, season in pairs:
            df = _read_raw_with_season(path, season)
            if not df.empty:
                frames.append(df)
        if not frames:
            print("No valid raw data found.")
            return

    df = pd.concat(frames, ignore_index=True)
    df = df.rename(columns={
        "Date": "date",
        "HomeTeam": "home_team",
        "AwayTeam": "away_team",
        "FTHG": "home_goals",
        "FTAG": "away_goals",
    })
    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce").dt.strftime("%Y-%m-%d")
    df = df[df["date"].notna()]

    df["home_goals"] = pd.to_numeric(df["home_goals"], errors="coerce")
    df["away_goals"] = pd.to_numeric(df["away_goals"], errors="coerce")
    df["status"] = np.where(
        df["home_goals"].notna() & df["away_goals"].notna(),
        "FINISHED",
        "SCHEDULED",
    )
    df["match_id"] = (
        df["date"].astype(str) + "_"
        + df["home_team"].astype(str).str.replace(" ", "", regex=False)
        + "_"
        + df["away_team"].astype(str).str.replace(" ", "", regex=False)
    )
    cols = ["match_id", "date", "season", "home_team", "away_team", "home_goals", "away_goals", "status"]
    keep = df[cols].sort_values(["date", "home_team", "away_team"]).drop_duplicates(
        subset=["date", "home_team", "away_team"], keep="first"
    )


    clean_path.parent.mkdir(parents=True, exist_ok=True)
    keep.to_csv(clean_path, index=False)

    n_total = len(keep)
    n_finished = int((keep["status"] == "FINISHED").sum())
    n_sched = n_total - n_finished
    n_teams = len(set(keep["home_team"]).union(set(keep["away_team"])))
    first_date = keep["date"].min() if n_total else "NA"
    last_date = keep["date"].max() if n_total else "NA"
    print(
        f"Wrote {clean_path} | rows={n_total} finished={n_finished} scheduled={n_sched} teams={n_teams} range={first_date} → {last_date}")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "init-data"

    if mode == "fetch-data":
        fetch_all()

    elif mode == "init-data":
        clean_raw_csv()

    elif mode == "train-elo":
        ratings_path = BASE_DIR / "data" / "ratings.csv"
        train_elo(clean_path=CLEAN_PATH, out_path=ratings_path)

    elif mode == "predict":
        compute_probs()

    elif mode == "refresh":
        # Fetch latest data, rebuild clean matches, retrain Elo, and predict
        fetch_all()
        clean_raw_csv()
        ratings_path = BASE_DIR / "data" / "ratings.csv"
        train_elo(clean_path=CLEAN_PATH, out_path=ratings_path)
        compute_probs()

    else:
        print(
            "Usage:\n"
            "  python -m src.main fetch-data   # download latest E0 data\n"
            "  python -m src.main init-data    # clean raw CSVs -> clean_matches.csv\n"
            "  python -m src.main train-elo     # train Elo -> ratings.csv\n"
            "  python -m src.main predict      # generate predictions.csv\n"
            "  python -m src.main refresh      # fetch + init + train + predict"
        )