# Win-Streak Predictor

Predict **Manchester United** match outcomes and the chance of a 5-game win streak using an Elo-based model and Premier League (E0) data.

If you ever want to know whether United will win five in a row—spoiler: the probability is rarely... kind—this tool gives you per-match win/draw/loss odds, projected points, and an approximate “any 5-in-a-row” probability.

---

## What it does

| Input | Output |
|-------|--------|
| Premier League fixtures (raw or fetched) | **Per match:** `p_home_win`, `p_draw`, `p_away_win`, and United’s projected points |
| Focus: Man United remaining/current fixtures | **Terminal:** “Best 5-game window” and “Approx ANY 5-in-a-row” for United |

After a run you get **`data/predictions.csv`** with all fixtures, three-way probabilities, and United’s expected points per game.

---

## Quick start

**1. Clone and install**

```bash
cd Win-Streak-Predictor-
pip install -r requirements.txt
```

**2. One-shot: fetch data, train, predict**

```bash
python -m src.main refresh
```

This will:

- Download latest E0 data (2023–24, 2024–25, 2025–26) from [football-data.co.uk](https://www.football-data.co.uk/)
- Build `data/clean_matches.csv` from all `E0*.csv` in `data/raw/`
- Train Elo ratings → `data/ratings.csv`
- Generate `data/predictions.csv` and print the 5-game streak summary

**3. Or run step by step**

```bash
python -m src.main fetch-data   # download E0 CSVs to data/raw/
python -m src.main init-data   # clean & merge → clean_matches.csv
python -m src.main train-elo   # Elo ratings → ratings.csv
python -m src.main predict     # predictions.csv + terminal summary
```

---

## Project structure

```
Win-Streak-Predictor-
├── src/
│   ├── main.py           # CLI: fetch-data, init-data, train-elo, predict, refresh
│   ├── fetch_data.py     # Download E0 CSVs from football-data.co.uk
│   ├── elo_model.py      # Elo training on finished matches
│   └── simulate_upcoming.py   # Win/draw/loss probs + United projected points
├── data/
│   ├── raw/              # E0.csv, E0_2324.csv, E0_2425.csv, E0_2526.csv
│   ├── clean_matches.csv # All seasons, FINISHED + SCHEDULED
│   ├── ratings.csv       # Team Elo scores
│   └── predictions.csv   # Fixtures with probabilities and United proj. points
├── tests/
│   ├── test_elo_model.py
│   ├── test_simulate_upcoming.py
│   └── test_main.py
├── requirements.txt
└── README.md
```

---

## Model (brief)

- **Elo:** Logistic curve, home advantage (+60), default K=25, start 1500.
- **Three-way probs:** 2-way Elo outcome is turned into home/draw/away with a fixed draw share (~24%).
- **United focus:** `simulate_upcoming` uses `FOCUS_TEAM = "Man United"` for projected points and 5-game windows; team names must match `ratings.csv` / raw data.

---

## Data and artifacts

| File | Description |
|------|--------------|
| `data/raw/E0*.csv` | Raw match data (one file per season). Same columns as [football-data.co.uk](https://www.football-data.co.uk/) E0 (Date, HomeTeam, AwayTeam, FTHG, FTAG). |
| `data/clean_matches.csv` | Cleaned, merged matches; columns: `match_id`, `date`, `season`, `home_team`, `away_team`, `home_goals`, `away_goals`, `status` (FINISHED / SCHEDULED). |
| `data/ratings.csv` | Elo ratings: `team`, `elo`. |
| `data/predictions.csv` | Next fixtures with `p_home_win`, `p_draw`, `p_away_win`, `Man United_side`, `Man United_proj_points`. |

**Keeping data up to date**

- **`fetch-data`** downloads 2023-24, 2024-25, 2025-26 E0 CSVs. If the site is down, add CSVs manually to `data/raw/` (e.g. `E0_2425.csv`). See `data/raw/README.txt`.
- **`init-data`** merges every `E0*.csv` in `data/raw/` and infers season from the filename (e.g. `E0_2425` → 2024-25).

---

## Tests

From the project root:

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

Tests cover: Elo trainer, probability helpers (`logistic_expected`, `three_way_probs`, `projected_points`), clean-CSV pipeline, and prediction output.

---

## Tech stack

- **Python 3**
- **Libraries:** `pandas`, `numpy`, `requests`, `matplotlib`, `pytest`

---

## Usage summary

| Command | Action |
|---------|--------|
| `python -m src.main fetch-data` | Download E0 data into `data/raw/` |
| `python -m src.main init-data` | Build `clean_matches.csv` from all raw E0 CSVs |
| `python -m src.main train-elo` | Train Elo from finished matches → `ratings.csv` |
| `python -m src.main predict` | Generate `predictions.csv` and 5-game streak summary |
| `python -m src.main refresh` | fetch-data → init-data → train-elo → predict |
