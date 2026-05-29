import pandas as pd
import numpy as np

TEAMS = {
    "Argentina": {"rank": 1, "elo": 2100, "style": "possession", "strength": 95},
    "Francia": {"rank": 2, "elo": 2080, "style": "transition", "strength": 94},
    "Brasil": {"rank": 3, "elo": 2050, "style": "attack", "strength": 93},
    "Inglaterra": {"rank": 4, "elo": 2040, "style": "possession", "strength": 92},
    "España": {"rank": 5, "elo": 2020, "style": "tiki-taka", "strength": 91},
    "Alemania": {"rank": 6, "elo": 2000, "style": "pressing", "strength": 90},
    "Portugal": {"rank": 7, "elo": 1980, "style": "versatile", "strength": 89},
    "Países Bajos": {"rank": 8, "elo": 1960, "style": "total", "strength": 88},
    "Italia": {"rank": 9, "elo": 1940, "style": "defensive", "strength": 87},
    "Uruguay": {"rank": 10, "elo": 1920, "style": "fight", "strength": 86},
    "Croacia": {"rank": 11, "elo": 1900, "style": "midfield", "strength": 85},
    "Marruecos": {"rank": 12, "elo": 1880, "style": "compact", "strength": 84},
    "Colombia": {"rank": 13, "elo": 1860, "style": "attack", "strength": 83},
    "México": {"rank": 14, "elo": 1840, "style": "dynamic", "strength": 82},
    "Japón": {"rank": 15, "elo": 1820, "style": "technical", "strength": 81},
    "Senegal": {"rank": 16, "elo": 1800, "style": "athletic", "strength": 80},
    "Estados Unidos": {"rank": 17, "elo": 1780, "style": "intense", "strength": 79},
    "Corea del Sur": {"rank": 18, "elo": 1760, "style": "dynamic", "strength": 78},
    "Suiza": {"rank": 19, "elo": 1740, "style": "solid", "strength": 77},
    "Serbia": {"rank": 20, "elo": 1720, "style": "physical", "strength": 76},
}

STYLES = {
    "possession": {"pace": 0.4, "pressing": 0.6, "long_balls": 0.3, "xg_per_shot": 0.12},
    "transition": {"pace": 0.8, "pressing": 0.7, "long_balls": 0.5, "xg_per_shot": 0.14},
    "attack": {"pace": 0.7, "pressing": 0.5, "long_balls": 0.4, "xg_per_shot": 0.13},
    "tiki-taka": {"pace": 0.3, "pressing": 0.7, "long_balls": 0.2, "xg_per_shot": 0.11},
    "pressing": {"pace": 0.6, "pressing": 0.9, "long_balls": 0.4, "xg_per_shot": 0.12},
    "versatile": {"pace": 0.6, "pressing": 0.6, "long_balls": 0.4, "xg_per_shot": 0.13},
    "total": {"pace": 0.7, "pressing": 0.7, "long_balls": 0.4, "xg_per_shot": 0.13},
    "defensive": {"pace": 0.3, "pressing": 0.8, "long_balls": 0.5, "xg_per_shot": 0.10},
    "fight": {"pace": 0.6, "pressing": 0.8, "long_balls": 0.5, "xg_per_shot": 0.11},
    "midfield": {"pace": 0.5, "pressing": 0.6, "long_balls": 0.3, "xg_per_shot": 0.11},
    "compact": {"pace": 0.5, "pressing": 0.8, "long_balls": 0.4, "xg_per_shot": 0.10},
    "dynamic": {"pace": 0.7, "pressing": 0.7, "long_balls": 0.4, "xg_per_shot": 0.12},
    "technical": {"pace": 0.5, "pressing": 0.5, "long_balls": 0.3, "xg_per_shot": 0.12},
    "athletic": {"pace": 0.8, "pressing": 0.7, "long_balls": 0.5, "xg_per_shot": 0.11},
    "intense": {"pace": 0.7, "pressing": 0.8, "long_balls": 0.4, "xg_per_shot": 0.11},
    "solid": {"pace": 0.4, "pressing": 0.6, "long_balls": 0.4, "xg_per_shot": 0.10},
    "physical": {"pace": 0.6, "pressing": 0.7, "long_balls": 0.6, "xg_per_shot": 0.11},
}

def get_team_stats(team_name):
    t = TEAMS.get(team_name, TEAMS["Argentina"])
    s = STYLES.get(t["style"], STYLES["possession"])
    return {**t, **s}

def simulate_match(team_a, team_b, seed=None):
    if seed is not None:
        np.random.seed(seed)
    ta = get_team_stats(team_a)
    tb = get_team_stats(team_b)
    elo_diff = ta["elo"] - tb["elo"]
    win_prob = 1 / (1 + 10 ** (-elo_diff / 400))
    home_adv = np.random.normal(1.0, 0.1)
    win_prob = np.clip(win_prob * home_adv, 0.1, 0.9)

    avg_goals_a = ta["strength"] / 30 * (1 - win_prob * 0.3)
    avg_goals_b = tb["strength"] / 30 * (win_prob * 0.3)

    goals_a = max(0, int(np.random.poisson(avg_goals_a)))
    goals_b = max(0, int(np.random.poisson(avg_goals_b)))

    total_shots = np.random.randint(8, 25)
    shots_a = int(total_shots * win_prob)
    shots_b = total_shots - shots_a

    possession_a = 50 + (ta["strength"] - tb["strength"]) * 0.5 + np.random.normal(0, 5)
    possession_a = np.clip(possession_a, 30, 70)
    possession_b = 100 - possession_a

    xg_a = shots_a * ta["xg_per_shot"] * (1 + (ta["strength"] - 75) / 100)
    xg_b = shots_b * tb["xg_per_shot"] * (1 + (tb["strength"] - 75) / 100)

    return {
        "team_a": team_a, "team_b": team_b,
        "goals_a": goals_a, "goals_b": goals_b,
        "shots_a": shots_a, "shots_b": shots_b,
        "possession_a": round(possession_a, 1),
        "possession_b": round(possession_b, 1),
        "xg_a": round(xg_a, 2), "xg_b": round(xg_b, 2),
        "win_prob_a": round(win_prob, 3),
        "win_prob_b": round(1 - win_prob, 3),
        "style_a": ta["style"], "style_b": tb["style"],
    }
