"""Tests for main pipeline (clean_raw_csv, gather raw frames)."""
from pathlib import Path

import pandas as pd
import pytest

from src.main import (
    CLEAN_PATH,
    RAW_DIR,
    _gather_raw_frames,
    _read_raw_with_season,
    clean_raw_csv,
)


def test_read_raw_with_season_valid(sample_raw_csv):
    """_read_raw_with_season returns DataFrame with Date, HomeTeam, AwayTeam, FTHG, FTAG, season."""
    df = _read_raw_with_season(sample_raw_csv, "2024-25")
    assert not df.empty
    assert "Date" in df.columns
    assert "HomeTeam" in df.columns
    assert "season" in df.columns
    assert df["season"].iloc[0] == "2024-25"
    assert len(df) == 3


def test_read_raw_with_season_missing_columns(tmp_path):
    """_read_raw_with_season returns empty DataFrame when required columns are missing."""
    bad = tmp_path / "bad.csv"
    bad.write_text("Date,HomeTeam\n01/01/2024,A\n")
    df = _read_raw_with_season(bad, "2024-25")
    assert df.empty


def test_clean_raw_csv_single_file(sample_raw_csv, tmp_path):
    """clean_raw_csv with explicit raw_path produces clean_matches with expected columns and status."""
    clean_path = tmp_path / "clean_matches.csv"
    clean_raw_csv(raw_path=sample_raw_csv, clean_path=clean_path)

    assert clean_path.exists()
    df = pd.read_csv(clean_path)
    cols = ["match_id", "date", "season", "home_team", "away_team", "home_goals", "away_goals", "status"]
    for c in cols:
        assert c in df.columns
    assert len(df) == 3
    assert (df["status"] == "FINISHED").all()
    assert df["date"].iloc[0].startswith("2024-08")


def test_clean_raw_csv_deduplicates(tmp_path):
    """Duplicate rows (same date, home, away) are dropped."""
    raw = tmp_path / "E0.csv"
    raw.write_text(
        "Date,HomeTeam,AwayTeam,FTHG,FTAG\n"
        "15/08/2024,TeamA,TeamB,2,1\n"
        "15/08/2024,TeamA,TeamB,2,1\n",
        encoding="utf-8",
    )
    clean_path = tmp_path / "clean.csv"
    clean_raw_csv(raw_path=raw, clean_path=clean_path)
    df = pd.read_csv(clean_path)
    assert len(df) == 1


def test_clean_raw_csv_scheduled_from_missing_goals(tmp_path):
    """Rows with missing FTHG/FTAG get status SCHEDULED."""
    raw = tmp_path / "E0.csv"
    raw.write_text(
        "Date,HomeTeam,AwayTeam,FTHG,FTAG\n"
        "15/08/2024,TeamA,TeamB,2,1\n"
        "20/09/2024,TeamB,TeamC,,\n",
        encoding="utf-8",
    )
    clean_path = tmp_path / "clean.csv"
    clean_raw_csv(raw_path=raw, clean_path=clean_path)
    df = pd.read_csv(clean_path)
    assert len(df) == 2
    statuses = set(df["status"])
    assert "FINISHED" in statuses
    assert "SCHEDULED" in statuses


def test_gather_raw_frames_finds_e0_csv(tmp_path, monkeypatch):
    """_gather_raw_frames returns (path, season) for E0*.csv in raw dir."""
    monkeypatch.setattr("src.main.RAW_DIR", tmp_path)
    (tmp_path / "E0.csv").write_text("Date,HomeTeam,AwayTeam,FTHG,FTAG\n")
    (tmp_path / "E0_2425.csv").write_text("Date,HomeTeam,AwayTeam,FTHG,FTAG\n")

    pairs = _gather_raw_frames()
    assert len(pairs) >= 2
    stems = [p[0].stem for p in pairs]
    assert "E0" in stems
    seasons = [p[1] for p in pairs]
    assert "2024-25" in seasons
