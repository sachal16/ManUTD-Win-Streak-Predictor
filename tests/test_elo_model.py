"""Tests for Elo model (train_elo)."""
from pathlib import Path

import pandas as pd
import pytest

from src.elo_model import DEFAULT_HOME_ADV, DEFAULT_K, train_elo


def test_train_elo_produces_ratings_file(sample_clean_matches, tmp_path):
    """train_elo reads clean_matches and writes ratings CSV with team and elo columns."""
    out_path = tmp_path / "ratings.csv"
    train_elo(clean_path=sample_clean_matches, out_path=out_path)

    assert out_path.exists()
    df = pd.read_csv(out_path)
    assert list(df.columns) == ["team", "elo"]
    assert len(df) == 3
    assert set(df["team"]) == {"TeamA", "TeamB", "TeamC"}
    assert df["elo"].dtype in (float, "float64")
    assert df["elo"].notna().all()


def test_train_elo_winner_gains_rating(sample_clean_matches, tmp_path):
    """After TeamA beats TeamB, TeamA should have elo > 1500 and TeamB < 1500 (with default 1500 start)."""
    out_path = tmp_path / "ratings.csv"
    train_elo(clean_path=sample_clean_matches, out_path=out_path)

    df = pd.read_csv(out_path)
    ratings = dict(zip(df["team"], df["elo"]))
    # First match: TeamA 2-1 TeamB -> TeamA wins
    assert ratings["TeamA"] > 1500
    assert ratings["TeamB"] < 1500


def test_train_elo_ignores_scheduled_and_missing_goals(tmp_path):
    """Only FINISHED rows with valid goals are used; SCHEDULED and NaN goals are skipped."""
    rows = [
        ("m1", "2024-08-15", "TeamA", "TeamB", 2, 1, "FINISHED"),
        ("m2", "2024-08-16", "TeamB", "TeamC", None, None, "SCHEDULED"),
    ]
    df = pd.DataFrame(
        rows,
        columns=["match_id", "date", "home_team", "away_team", "home_goals", "away_goals", "status"],
    )
    clean_path = tmp_path / "clean_matches.csv"
    df.to_csv(clean_path, index=False)

    out_path = tmp_path / "ratings.csv"
    train_elo(clean_path=clean_path, out_path=out_path)

    out = pd.read_csv(out_path)
    assert len(out) == 2  # only TeamA and TeamB from the one finished match
    assert "TeamC" not in out["team"].tolist()


def test_train_elo_respects_k_and_home_adv(tmp_path):
    """Custom K and HOME_ADV don't crash and change output magnitude."""
    df = pd.DataFrame(
        [
            ["m1", "2024-08-15", "TeamA", "TeamB", 1, 0, "FINISHED"],
        ],
        columns=["match_id", "date", "home_team", "away_team", "home_goals", "away_goals", "status"],
    )
    clean_path = tmp_path / "clean_matches.csv"
    df.to_csv(clean_path, index=False)

    out1 = tmp_path / "out1.csv"
    out2 = tmp_path / "out2.csv"
    train_elo(clean_path=clean_path, out_path=out1, K=25, HOME_ADV=60)
    train_elo(clean_path=clean_path, out_path=out2, K=10, HOME_ADV=0)

    r1 = pd.read_csv(out1)
    r2 = pd.read_csv(out2)
    # Different K/home_adv should yield different elo values
    assert r1["elo"].tolist() != r2["elo"].tolist()
