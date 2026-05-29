import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

class MatchPredictor:
    def __init__(self):
        self.model = None
        self._train()

    def _generate_training_data(self, n_samples=5000):
        np.random.seed(42)
        X = []
        y = []

        for _ in range(n_samples):
            elo_a = np.random.uniform(1700, 2100)
            elo_b = np.random.uniform(1700, 2100)
            str_a = np.random.uniform(75, 95)
            str_b = np.random.uniform(75, 95)
            form_a = np.random.uniform(0, 1)
            form_b = np.random.uniform(0, 1)
            fatigue_a = np.random.uniform(0, 1)
            fatigue_b = np.random.uniform(0, 1)
            home = np.random.randint(0, 2)

            elo_diff = elo_a - elo_b
            str_diff = str_a - str_b
            form_diff = form_a - form_b
            fatigue_diff = fatigue_a - fatigue_b

            win_prob = 1 / (1 + 10 ** (-elo_diff / 400))
            win_prob += (str_diff / 100) * 0.2
            win_prob += (form_diff / 2) * 0.15
            win_prob -= (fatigue_diff / 2) * 0.1
            if home:
                win_prob += 0.08
            win_prob = np.clip(win_prob, 0.05, 0.95)

            X.append([elo_a, elo_b, str_a, str_b, form_a, form_b,
                      fatigue_a, fatigue_b, home])
            y.append(1 if np.random.random() < win_prob else 0)

        X = pd.DataFrame(X, columns=["elo_a", "elo_b", "str_a", "str_b",
                                      "form_a", "form_b", "fatigue_a",
                                      "fatigue_b", "home"])
        return X, np.array(y)

    def _train(self):
        X, y = self._generate_training_data()
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        self.model = XGBClassifier(
            n_estimators=100, max_depth=4, learning_rate=0.1,
            eval_metric="logloss", random_state=42
        )
        self.model.fit(X_train, y_train)
        self.test_score = self.model.score(X_test, y_test)

    def predict(self, team_a_stats, team_b_stats, home=0):
        features = pd.DataFrame([[
            team_a_stats.get("elo", 1900),
            team_b_stats.get("elo", 1900),
            team_a_stats.get("strength", 80),
            team_b_stats.get("strength", 80),
            team_a_stats.get("form", 0.5),
            team_b_stats.get("form", 0.5),
            team_a_stats.get("fatigue", 0.3),
            team_b_stats.get("fatigue", 0.3),
            home
        ]], columns=["elo_a", "elo_b", "str_a", "str_b", "form_a",
                      "form_b", "fatigue_a", "fatigue_b", "home"])
        prob = self.model.predict_proba(features)[0, 1]
        return prob

    def feature_importance(self):
        if self.model is None:
            return {}
        imp = self.model.feature_importances_
        cols = ["elo_a", "elo_b", "str_a", "str_b", "form_a",
                "form_b", "fatigue_a", "fatigue_b", "home"]
        return dict(sorted(zip(cols, imp), key=lambda x: x[1], reverse=True))
