import pandas as pd
import numpy as np
from data.teams import TEAMS

POSITIONS = {
    "POR": {"role": "goalkeeper", "avg_height": 188, "avg_weight": 82},
    "DEF": {"role": "defender", "avg_height": 183, "avg_weight": 78},
    "MED": {"role": "midfielder", "avg_height": 178, "avg_weight": 73},
    "DEL": {"role": "forward", "avg_height": 180, "avg_weight": 74},
    "EXT": {"role": "winger", "avg_height": 175, "avg_weight": 70},
}

PLAYER_NAMES = {
    "Argentina": ["Messi", "Di María", "Álvarez", "De Paul", "Mac Allister",
                  "Enzo Fernández", "Romero", "Otamendi", "Tagliafico", "Molina", "Martínez"],
    "Francia": ["Mbappé", "Griezmann", "Dembélé", "Tchouaméni", "Camavinga",
                "Rabiot", "Upamecano", "Saliba", "Hernández", "Koundé", "Maignan"],
    "Brasil": ["Vini Jr", "Rodrygo", "Raphinha", "Paquetá", "Casemiro",
               "Guimarães", "Marquinhos", "Militao", "Danilo", "Lodi", "Alisson"],
    "Inglaterra": ["Kane", "Bellingham", "Foden", "Rice", "Saka",
                   "Maddison", "Stones", "Maguire", "Chilwell", "Alexander-Arnold", "Pickford"],
    "España": ["Morata", "Pedri", "Gavi", "Rodri", "Olmo",
               "Ruiz", "Laporte", "García", "Carvajal", "Grimaldo", "Simón"],
    "Alemania": ["Havertz", "Musiala", "Wirtz", "Kimmich", "Gündoğan",
                 "Andrich", "Rüdiger", "Schlotterbeck", "Raum", "Henrichs", "Neuer"],
}

def generate_players(n_players=100):
    np.random.seed(42)
    players = []
    teams_list = list(TEAMS.keys())

    for i in range(n_players):
        team = np.random.choice(teams_list)
        pos = np.random.choice(list(POSITIONS.keys()), p=[0.1, 0.3, 0.3, 0.2, 0.1])
        pinfo = POSITIONS[pos]

        age = int(np.random.normal(26, 4))
        age = max(18, min(38, age))

        height = int(np.random.normal(pinfo["avg_height"], 5))
        weight = int(np.random.normal(pinfo["avg_weight"], 5))

        pace = int(np.random.normal(70, 15))
        shooting = int(np.random.normal(65, 15))
        passing = int(np.random.normal(68, 15))
        dribbling = int(np.random.normal(65, 15))
        defending = int(np.random.normal(60, 18))
        physical = int(np.random.normal(70, 12))

        overall = int((pace + shooting + passing + dribbling + defending + physical) / 6)
        overall = max(55, min(99, overall))

        market_val = round(np.exp((overall - 50) / 12) * 0.5 + np.random.uniform(0, 10), 1)
        market_val = max(0.5, min(200, market_val))

        goals_ratio = max(0, np.random.normal(0.15, 0.1) if pos in ["DEL", "EXT"] else np.random.normal(0.03, 0.03))
        assists_ratio = max(0, np.random.normal(0.1, 0.07) if pos in ["EXT", "MED"] else np.random.normal(0.03, 0.03))

        name = f"Player_{i+1}"
        if team in PLAYER_NAMES and i < len(PLAYER_NAMES[team]):
            name = PLAYER_NAMES[team][i % len(PLAYER_NAMES[team])]
            if i // len(PLAYER_NAMES[team]) > 0:
                name += f"_{i//len(PLAYER_NAMES[team])}"

        players.append({
            "id": i + 1,
            "name": name,
            "age": age,
            "team": team,
            "position": pos,
            "height": height,
            "weight": weight,
            "overall": overall,
            "pace": pace,
            "shooting": shooting,
            "passing": passing,
            "dribbling": dribbling,
            "defending": defending,
            "physical": physical,
            "market_value": market_val,
            "goals_per_90": round(goals_ratio, 2),
            "assists_per_90": round(assists_ratio, 2),
        })

    return pd.DataFrame(players)

def get_similar_players(df, player_name, n=5):
    target = df[df["name"] == player_name]
    if target.empty:
        return df.head(n)
    target = target.iloc[0]
    features = ["overall", "pace", "shooting", "passing", "dribbling", "defending", "physical", "age"]
    X = df[features].values
    target_vec = target[features].values.reshape(1, -1)
    from sklearn.metrics.pairwise import euclidean_distances
    dists = euclidean_distances(X, target_vec).flatten()
    similar_idx = np.argsort(dists)[1:n+1]
    return df.iloc[similar_idx]
