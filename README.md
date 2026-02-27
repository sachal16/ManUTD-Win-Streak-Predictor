# Win-Streak-Predictor-
If you ever for some reason want to find out if Man united will win 5 games? Just check the probability, it never good.. 

**Input:** Analyzes Manchester United remaining / current fixtures

**Output:** Per-match win probability, projected points, and probability United hits any 5-game win streak this season

After running: you get data/predictions.csv — next fixtures with p_home_win, p_draw, p_away_win, and United’s projected points per game

Terminal summary — “Best 5-game window …” and “Approx ANY 5-in-a-row …” for United


![img.png](img.png)

**Tools Used:** 
-   `pandas`, `numpy`, `pathlib`, `requests`
**Modeling:**
-   Simple **Elo** rating system (logistic transform, home-advantage, fixed draw share)

**Keeping data up to date**
- Run `python -m src.main fetch-data` to download the latest Premier League (E0) data from football-data.co.uk (2023-24, 2024-25, 2025-26).
- Run `python -m src.main refresh` to fetch data, rebuild clean matches, retrain Elo, and generate predictions in one go.
- You can also add multiple season CSVs manually to `data/raw/` (e.g. `E0_2425.csv`, `E0_2324.csv`); `init-data` merges all `E0*.csv` files.

**Artifacts:**
  - `data/raw/E0_*.csv` — raw match data (one per season)
  - `data/clean_matches.csv` — cleaned historical results (all seasons merged)
  - `data/ratings.csv` — team Elo scores
  - `data/predictions.csv` — next fixtures with win/draw/loss probs + projected points
