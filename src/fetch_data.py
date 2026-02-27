"""
Fetch Premier League (E0) match data from football-data.co.uk.
Downloads multiple seasons to keep ratings up to date.
"""
import io
import time
from pathlib import Path
from typing import List, Optional

import pandas as pd
import requests

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"

# Season code on football-data.co.uk -> our label
SEASONS = [
    ("2324", "2023-24"),
    ("2425", "2024-25"),
    ("2526", "2025-26"),
]
BASE_URL = "https://www.football-data.co.uk/mmz4281"
REQUIRED_COLUMNS = ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"]


def fetch_season(season_code: str, season_label: str):
    """Download one season E0.csv. Returns DataFrame or None on failure."""
    url = f"{BASE_URL}/{season_code}/E0.csv"
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "WinStreakPredictor/1.0"})
        r.raise_for_status()
        try:
            df = pd.read_csv(io.BytesIO(r.content), encoding="utf-8", encoding_errors="ignore")
        except TypeError:
            df = pd.read_csv(io.BytesIO(r.content), encoding="utf-8")
        if not all(c in df.columns for c in REQUIRED_COLUMNS):
            print(f"  {season_label}: missing columns, skip")
            return None
        return df
    except Exception as e:
        print(f"  {season_label}: {e}")
        return None


def fetch_all(out_dir: Optional[Path] = None) -> List[Path]:
    """Download all seasons to data/raw/. Returns list of saved file paths."""
    out_dir = out_dir or RAW_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []

    print("Fetching Premier League (E0) data from football-data.co.uk ...")
    for code, label in SEASONS:
        df = fetch_season(code, label)
        if df is not None:
            path = out_dir / f"E0_{code}.csv"
            df.to_csv(path, index=False)
            saved.append(path)
            print(f"  {label}: saved {len(df)} rows -> {path.name}")
        time.sleep(0.5)

    if not saved:
        print("No data downloaded. You can add CSVs manually to data/raw/ (e.g. E0_2425.csv).")
    return saved


if __name__ == "__main__":
    fetch_all()
