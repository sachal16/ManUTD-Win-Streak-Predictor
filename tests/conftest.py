"""Pytest fixtures for Win-Streak-Predictor tests."""
import tempfile
from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def tmp_path_dir(tmp_path):
    """Return tmp_path as Path (for consistency)."""
    return tmp_path


@pytest.fixture
def sample_raw_csv(tmp_path):
    """Minimal E0-style raw CSV (football-data.co.uk columns)."""
    content = """Date,HomeTeam,AwayTeam,FTHG,FTAG
15/08/2024,TeamA,TeamB,2,1
16/08/2024,TeamB,TeamC,0,0
17/08/2024,TeamA,TeamC,1,2
"""
    p = tmp_path / "E0.csv"
    p.write_text(content.strip(), encoding="utf-8")
    return p


@pytest.fixture
def sample_clean_matches(tmp_path):
    """Minimal clean_matches.csv with FINISHED games for Elo training."""
    rows = [
        ("2024-08-15", "2024-25", "TeamA", "TeamB", 2, 1, "FINISHED"),
        ("2024-08-16", "2024-25", "TeamB", "TeamC", 0, 0, "FINISHED"),
        ("2024-08-17", "2024-25", "TeamA", "TeamC", 1, 2, "FINISHED"),
    ]
    df = pd.DataFrame(
        rows,
        columns=["date", "season", "home_team", "away_team", "home_goals", "away_goals", "status"],
    )
    df["match_id"] = (
        df["date"] + "_" + df["home_team"].str.replace(" ", "", regex=False) + "_" + df["away_team"].str.replace(" ", "", regex=False)
    )
    cols = ["match_id", "date", "season", "home_team", "away_team", "home_goals", "away_goals", "status"]
    df = df[cols]
    p = tmp_path / "clean_matches.csv"
    df.to_csv(p, index=False)
    return p


@pytest.fixture
def sample_ratings(tmp_path):
    """Minimal ratings.csv for prediction tests."""
    df = pd.DataFrame({"team": ["TeamA", "TeamB", "TeamC"], "elo": [1550.0, 1500.0, 1450.0]})
    p = tmp_path / "ratings.csv"
    df.to_csv(p, index=False)
    return p
