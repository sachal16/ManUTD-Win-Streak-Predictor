from pathlib import Path
import pandas as pd

HOME_ADV = 60.0
DEFAULT_DRAW_RATE = 0.24
FOCUS_TEAM = "Man United"  # must match team name in ratings.csv

BASE_DIR = Path(__file__).resolve().parents[1]
RATINGS_PATH = BASE_DIR / "data" / "ratings.csv"
UPCOMING_PATH = BASE_DIR / "data" / "upcoming.csv"
PREDICTIONS_PATH = BASE_DIR / "data" / "predictions.csv"


# --- Elo -> probabilities helpers ---
def logistic_expected(home_elo: float, away_elo: float, home_adv: float = HOME_ADV) -> float:
    """Return the raw 2-way home-win prob from Elo (before adding draw)."""
    diff = (home_elo + home_adv) - away_elo
    return 1.0 / (1.0 + 10 ** (-diff / 400.0))


def three_way_probs(p_home_raw: float, draw_rate: float = DEFAULT_DRAW_RATE):
    """Convert 2-way (home/away) probs into 3-way by allocating a fixed draw share."""
    p_away_raw = 1.0 - p_home_raw
    scale = 1.0 - draw_rate
    p_home = p_home_raw * scale
    p_away = p_away_raw * scale
    p_draw = draw_rate
    s = p_home + p_draw + p_away
    return p_home / s, p_draw / s, p_away / s


def projected_points(p_home: float, p_draw: float, p_away: float, is_home_for_team: bool) -> float:
    """Expected points for the focus team in this fixture."""
    if is_home_for_team:
        return 3.0 * p_home + 1.0 * p_draw
    else:
        return 3.0 * p_away + 1.0 * p_draw


# --- IO helpers ---
def load_ratings() -> dict:
    """Load your trained Elo ratings as a dict: team -> elo."""
    df = pd.read_csv(RATINGS_PATH)
    return dict(zip(df["team"], df["elo"]))


def load_fixtures() -> pd.DataFrame:
    """Prefer data/upcoming.csv; otherwise use a small hardcoded list."""
    if UPCOMING_PATH.exists():
        return pd.read_csv(UPCOMING_PATH)

    fixtures = [
        ("2025-10-25", "Man United", "Brentford"),
        ("2025-11-02", "Bournemouth", "Man United"),
        ("2025-11-09", "Man United", "Chelsea"),
        ("2025-11-16", "Brentford", "Man United"),
        ("2025-11-23", "Man United", "Fulham"),
        ("2025-11-30", "Man City", "Man United"),
        ("2025-12-07", "Man United", "Leeds"),
        ("2025-12-14", "Tottenham", "Man United"),
    ]
    return pd.DataFrame(fixtures, columns=["date", "home_team", "away_team"])


def compute_probs() -> pd.DataFrame:
    ratings = load_ratings()
    fixtures = load_fixtures()

    rows = []
    utd_win_probs = []

    for _, r in fixtures.iterrows():
        h, a = r["home_team"], r["away_team"]
        Rh = ratings.get(h, 1500.0)
        Ra = ratings.get(a, 1500.0)

        p_home_raw = logistic_expected(Rh, Ra)
        p_home, p_draw, p_away = three_way_probs(p_home_raw)

        # projected points for the focus team (home/away aware)
        is_utd_home = (h == FOCUS_TEAM)
        is_utd_away = (a == FOCUS_TEAM)
        if is_utd_home or is_utd_away:
            utd_win_probs.append(p_home if is_utd_home else p_away)

        pp = projected_points(p_home, p_draw, p_away, is_utd_home)

        rows.append({
            "date": r["date"],
            "home_team": h,
            "away_team": a,
            "p_home_win": round(p_home, 3),
            "p_draw": round(p_draw, 3),
            "p_away_win": round(p_away, 3),
            f"{FOCUS_TEAM}_side": "home" if is_utd_home else ("away" if is_utd_away else "none"),
            f"{FOCUS_TEAM}_proj_points": round(pp, 2),
        })

    out = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    PREDICTIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(PREDICTIONS_PATH, index=False)
    print(f"✅ Wrote {PREDICTIONS_PATH} | rows={len(out)}")

    # quick 5-in-a-row window check (approx)
    if len(utd_win_probs) >= 5:
        windows = [utd_win_probs[i] * utd_win_probs[i+1] * utd_win_probs[i+2] * utd_win_probs[i+3] * utd_win_probs[i+4]
                   for i in range(len(utd_win_probs) - 4)]
        best = max(windows)
        any_prob = 1.0
        for w in windows:
            any_prob *= (1.0 - w)
        any_prob = 1.0 - any_prob
        print(f"Best 5-game window P(win all 5) ≈ {best*100:.2f}% | Approx ANY 5-in-a-row ≈ {any_prob*100:.2f}%")
    else:
        print("Not enough fixtures to evaluate a 5-game window.")

    return out


if __name__ == "__main__":
    compute_probs()