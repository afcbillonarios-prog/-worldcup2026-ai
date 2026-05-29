import numpy as np
import pandas as pd
from data.teams import simulate_match

class TournamentSimulator:
    def __init__(self):
        self.groups = {
            "A": ["Argentina", "Japón", "Senegal", "Suiza"],
            "B": ["Francia", "Países Bajos", "Corea del Sur", "Serbia"],
            "C": ["Brasil", "Croacia", "México", "Estados Unidos"],
            "D": ["Inglaterra", "Uruguay", "Colombia", "Marruecos"],
            "E": ["España", "Portugal", "Italia", "Alemania"],
        }

    def simulate_group_stage(self, seed=42):
        np.random.seed(seed)
        results = {}
        for grp, teams in self.groups.items():
            group_results = {t: {"pts": 0, "gf": 0, "ga": 0, "gd": 0, "w": 0, "d": 0, "l": 0}
                             for t in teams}
            for i in range(len(teams)):
                for j in range(i + 1, len(teams)):
                    match = simulate_match(teams[i], teams[j])
                    ga, gb = match["goals_a"], match["goals_b"]
                    group_results[teams[i]]["gf"] += ga
                    group_results[teams[i]]["ga"] += gb
                    group_results[teams[j]]["gf"] += gb
                    group_results[teams[j]]["ga"] += ga
                    if ga > gb:
                        group_results[teams[i]]["pts"] += 3
                        group_results[teams[i]]["w"] += 1
                        group_results[teams[j]]["l"] += 1
                    elif ga == gb:
                        group_results[teams[i]]["pts"] += 1
                        group_results[teams[j]]["pts"] += 1
                        group_results[teams[i]]["d"] += 1
                        group_results[teams[j]]["d"] += 1
                    else:
                        group_results[teams[j]]["pts"] += 3
                        group_results[teams[j]]["w"] += 1
                        group_results[teams[i]]["l"] += 1
            for t in teams:
                group_results[t]["gd"] = group_results[t]["gf"] - group_results[t]["ga"]
            sorted_teams = sorted(group_results.items(),
                                  key=lambda x: (x[1]["pts"], x[1]["gd"], x[1]["gf"]),
                                  reverse=True)
            results[grp] = [{"team": t, **stats} for t, stats in sorted_teams]
        return results

    def monte_carlo(self, n_simulations=1000):
        results = {team: {"wins": 0, "finals": 0, "semis": 0, "quarters": 0,
                          "group_stage": 0, "avg_goals": 0, "total_goals": 0}
                   for grp in self.groups.values() for team in grp}

        for sim in range(n_simulations):
            if sim % 100 == 0 and sim > 0:
                pass
            group_winners = []
            group_seconds = []

            for grp, teams in self.groups.items():
                group_results = []
                group_data = {t: {"pts": 0, "gf": 0, "ga": 0} for t in teams}
                for i in range(len(teams)):
                    for j in range(i + 1, len(teams)):
                        match = simulate_match(teams[i], teams[j], seed=sim + j * 10 + i)
                        group_data[teams[i]]["gf"] += match["goals_a"]
                        group_data[teams[i]]["ga"] += match["goals_b"]
                        group_data[teams[j]]["gf"] += match["goals_b"]
                        group_data[teams[j]]["ga"] += match["goals_a"]
                        if match["goals_a"] > match["goals_b"]:
                            group_data[teams[i]]["pts"] += 3
                        elif match["goals_a"] == match["goals_b"]:
                            group_data[teams[i]]["pts"] += 1
                            group_data[teams[j]]["pts"] += 1
                        else:
                            group_data[teams[j]]["pts"] += 3
                sorted_teams = sorted(group_data.items(),
                                      key=lambda x: (x[1]["pts"], x[1]["gf"] - x[1]["ga"], x[1]["gf"]),
                                      reverse=True)
                group_winners.append(sorted_teams[0][0])
                group_seconds.append(sorted_teams[1][0])

            for t in group_winners:
                results[t]["group_stage"] += 1
            for t in group_seconds:
                results[t]["group_stage"] += 1

            qf_teams = group_winners + group_seconds
            for t in qf_teams:
                results[t]["quarters"] += 1

            np.random.shuffle(qf_teams)
            semis_teams = []
            for k in range(0, len(qf_teams), 2):
                if k + 1 < len(qf_teams):
                    winner = qf_teams[k] if np.random.random() > 0.4 else qf_teams[k + 1]
                    semis_teams.append(winner)
            for t in semis_teams:
                results[t]["semis"] += 1

            finalists = []
            for k in range(0, len(semis_teams), 2):
                if k + 1 < len(semis_teams):
                    winner = semis_teams[k] if np.random.random() > 0.4 else semis_teams[k + 1]
                    finalists.append(winner)
            for t in finalists:
                results[t]["finals"] += 1

            if len(finalists) == 2:
                winner = finalists[0] if np.random.random() > 0.4 else finalists[1]
                results[winner]["wins"] += 1

        for team in results:
            results[team]["avg_goals"] = round(results[team]["total_goals"] / n_simulations, 2)

        df = pd.DataFrame.from_dict(results, orient="index")
        df.index.name = "team"
        df = df.reset_index()
        for col in ["wins", "finals", "semis", "quarters", "group_stage"]:
            df[f"{col}_pct"] = (df[col] / n_simulations * 100).round(1)
        df = df.sort_values("wins", ascending=False)
        return df
