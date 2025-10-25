# src/simulate_upcoming.py
import math
import pandas as pd
from pathlib import Path

HOME_ADV = 60.0
DEFAULT_DRAW_RATE = 0.24

def logistic_expected(Rh, Ra, home_adv=HOME_ADV):
    D = (Rh + home_adv) - Ra
    return 1.0 / (1.0 + 10 ** (-D / 400.0))

def three_way_probs(home_win_raw, draw_rate=DEFAULT_DRAW_RATE):
    away_win_raw = 1.0 - home_win_raw
    scale = 1.0 - draw_rate
    p_home = home_win_raw * scale
    p_away = away_win_raw * scale
    p_draw = draw_rate
    s = p_home + p_draw + p_away
    return p_home / s, p_draw / s, p_away / s

def projected_points(p_home, p_draw, p_away, is_home_for_team):
    if is_home_for_team:
        win = p_home
        draw = p_draw
        loss = p_away
    else:
        win = p_away
        draw = p_draw
        loss = p_home
    return 3.0 * win + 1.0 * draw

def load_ratings():
    # small manual example — replace with your data/ratings.csv if you have it
    return {
        "Man United": 1750,
        "Brentford": 1550,
        "Bournemouth": 1500,
        "Chelsea": 1680,
        "Fulham": 1520,
        "Man City": 1850,
        "Leeds": 1500,
        "Tottenham": 1700,
        "Newcastle": 1650,
        "Aston Villa": 1600,
        "West Ham": 1620,
        "Liverpool": 1800,
    }

def tag_united_side(row):
    if row["home_team"] == "Man United":
        return "home"
    elif row["away_team"] == "Man United":
        return "away"
    else:
        return "none"

def compute_probs():
    ratings = load_ratings()

    # 💥 Here is your clean hardcoded fixture list
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

    df = pd.DataFrame(fixtures, columns=["date", "home_team", "away_team"])

    rows = []
    for _, r in df.iterrows():
        h, a = r["home_team"], r["away_team"]
        Rh, Ra = ratings[h], ratings[a]

        p_home_raw = logistic_expected(Rh, Ra)
        p_home, p_draw, p_away = three_way_probs(p_home_raw)

        side = tag_united_side(r)
        pp = projected_points(p_home, p_draw, p_away, side == "home")

        rows.append({
            "date": r["date"],
            "home_team": h,
            "away_team": a,
            "p_home_win": round(p_home, 3),
            "p_draw": round(p_draw, 3),
            "p_away_win": round(p_away, 3),
            "united_side": side,
            "united_proj_points": round(pp, 2)
        })

    out = pd.DataFrame(rows)
    print(out)
    return out

if __name__ == "__main__":
    compute_probs()
