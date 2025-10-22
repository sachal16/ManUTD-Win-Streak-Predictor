from itertools import dropwhile
from pathlib import Path
import pandas as pd

DEFAULT_K = 25  # rate of learning
DEFAULT_HOME_ADV = 60 # home advantage

def train_elo(clean_path: Path, out_path: Path, K: float = DEFAULT_K, HOME_ADV: float = DEFAULT_HOME_ADV):
    """read the finished matches, update Elo in chronological order
    Rh = home current elo rating,
    Ra = Away team elo rating
    home_adv = bonus elo for being home advantage(60 elo)
    D = rating difference (after home_adv)
    Eh = expected probability to win (0-1 range)
    Sh = means home teams actual scor ( win = 1; draw 0.5 , loss = 0.0)
    DEFUALT ELO = 1500 AND K = 25
    """

    df = pd.read_csv(clean_path)
    df = df[df["status"] == "FINISHED"].sort_values("date")

    ratings = {} # team -> current elo (1500 is deafult)

    def get(team: str) -> float:
        return ratings.get(team, 1500.0)

    # loop over each game row, pick home/away goals
    for _, r in df.iterrows():
        h = r["home_team"]; a = r["away_team"]
        hg = int(r["home_goals"])
        ag = int(r["away_goals"])

        Rh = get(h);
        Ra = get(a)

        # Expected score for home( standard elo logistic curve)
        D = (Rh + HOME_ADV) - Ra
        Eh = 1.0 / (1.0 + 10 ** (-D / 400.0))

        if hg > ag:
            Sh = 1.0
        elif hg == ag:
            Sh = 0.5
        else:
            Sh = 0.0

        # if home did better = delta is pos
        # if home did worse = delta is neg
        # Away gets the oppistie change

        delta = K * (Sh - Eh) # rating change
        ratings[h] = Rh + delta
        ratings[a] = Ra - delta # zero-sum

    out = (
        pd.DataFrame([{"team": t, "elo": round(v, 2) } for t, v in ratings.items()])
        .sort_values("elo", ascending =False)
        .reset_index(drop=True)
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False)
    print(f"Wrote {out_path} | teams={len(out)} (K={K}, home_adv={HOME_ADV})")





