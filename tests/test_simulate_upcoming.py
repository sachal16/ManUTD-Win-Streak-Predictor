"""Tests for simulate_upcoming (probabilities and compute_probs)."""
from pathlib import Path

import pandas as pd
import pytest

from src.simulate_upcoming import (
    DEFAULT_DRAW_RATE,
    logistic_expected,
    projected_points,
    three_way_probs,
)


def test_logistic_expected_equal_elos():
    """Equal Elo + home adv => home win prob > 0.5."""
    p = logistic_expected(1500.0, 1500.0, home_adv=60.0)
    assert 0.5 < p < 1.0


def test_logistic_expected_stronger_home():
    """Higher home Elo => higher home win probability."""
    p_low = logistic_expected(1400.0, 1500.0)
    p_high = logistic_expected(1600.0, 1500.0)
    assert p_low < p_high


def test_three_way_probs_sum_to_one():
    """Probabilities should sum to 1."""
    p_home, p_draw, p_away = three_way_probs(0.5, draw_rate=0.24)
    assert abs((p_home + p_draw + p_away) - 1.0) < 1e-6


def test_three_way_probs_draw_rate():
    """Draw share should be present and positive."""
    p_home, p_draw, p_away = three_way_probs(0.6, draw_rate=DEFAULT_DRAW_RATE)
    assert p_draw > 0
    assert p_draw == pytest.approx(0.24, rel=0.1)  # roughly the draw_rate after scaling


def test_projected_points_home_team():
    """When focus team is home, points = 3*p_home + 1*p_draw."""
    pts = projected_points(0.5, 0.25, 0.25, is_home_for_team=True)
    assert pts == pytest.approx(3 * 0.5 + 1 * 0.25)


def test_projected_points_away_team():
    """When focus team is away, points = 3*p_away + 1*p_draw."""
    pts = projected_points(0.5, 0.25, 0.25, is_home_for_team=False)
    assert pts == pytest.approx(3 * 0.25 + 1 * 0.25)


def test_compute_probs_produces_predictions(tmp_path, sample_ratings):
    """compute_probs with patched paths writes predictions CSV with expected columns."""
    from src import simulate_upcoming

    # Point module at temp dir
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (tmp_path / "data" / "ratings.csv").write_text(sample_ratings.read_text())
    fixtures_df = pd.DataFrame(
        [("2025-10-01", "TeamA", "TeamB"), ("2025-10-02", "TeamB", "TeamA")],
        columns=["date", "home_team", "away_team"],
    )
    upcoming_path = data_dir / "upcoming.csv"
    fixtures_df.to_csv(upcoming_path, index=False)

    predictions_path = data_dir / "predictions.csv"
    simulate_upcoming.RATINGS_PATH = data_dir / "ratings.csv"
    simulate_upcoming.UPCOMING_PATH = upcoming_path
    simulate_upcoming.PREDICTIONS_PATH = predictions_path
    simulate_upcoming.CLEAN_MATCHES_PATH = data_dir / "clean_matches.csv"  # avoid loading real one

    out = simulate_upcoming.compute_probs()

    assert predictions_path.exists()
    pred = pd.read_csv(predictions_path)
    assert "p_home_win" in pred.columns
    assert "p_draw" in pred.columns
    assert "p_away_win" in pred.columns
    assert len(pred) == 2
    assert (pred["p_home_win"] + pred["p_draw"] + pred["p_away_win"]).apply(lambda s: abs(s - 1.0) < 1e-5).all()
