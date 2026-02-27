Premier League (E0) raw data
============================

- Run:  python -m src.main fetch-data   to download latest seasons from football-data.co.uk
- Or add CSV files manually. Name them E0.csv (current season) or E0_2425.csv, E0_2324.csv etc.
- Same columns required: Date, HomeTeam, AwayTeam, FTHG, FTAG
- Then:  python -m src.main init-data   (merges all E0*.csv and builds clean_matches.csv)
