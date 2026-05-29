import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

class XGModel:
    def __init__(self):
        self.model = None
        self._train()

    def _generate_shots(self, n=2000):
        np.random.seed(42)
        data = []
        for _ in range(n):
            distance = np.random.uniform(0, 35)
            angle = np.random.uniform(0, 90)
            pressure = np.random.uniform(0, 1)
            speed = np.random.uniform(0, 30)
            is_header = np.random.randint(0, 2)
            is_through_ball = np.random.randint(0, 2)
            foot = np.random.choice([0, 1], p=[0.6, 0.4])

            base_prob = 0.5 * np.exp(-distance / 15) * np.cos(np.radians(angle))
            base_prob *= (1 - pressure * 0.5)
            base_prob *= (1 + speed / 100 * 0.3)
            if is_header:
                base_prob *= 0.5
            if is_through_ball:
                base_prob *= 1.3
            if foot:
                base_prob *= 1.1

            prob = np.clip(base_prob, 0.001, 0.9)
            goal = 1 if np.random.random() < prob else 0

            data.append({
                "distance": distance, "angle": angle,
                "pressure": pressure, "speed": speed,
                "header": is_header, "through_ball": is_through_ball,
                "strong_foot": foot, "goal": goal
            })
        return pd.DataFrame(data)

    def _train(self):
        df = self._generate_shots()
        features = ["distance", "angle", "pressure", "speed",
                    "header", "through_ball", "strong_foot"]
        X = df[features]
        y = df["goal"]
        self.model = LogisticRegression(C=0.5, max_iter=1000, random_state=42)
        self.model.fit(X, y)

    def predict_xg(self, distance, angle, pressure=0.3, speed=15,
                   is_header=False, through_ball=False, strong_foot=True):
        features = pd.DataFrame([[
            distance, angle, pressure, speed,
            int(is_header), int(through_ball), int(strong_foot)
        ]], columns=["distance", "angle", "pressure", "speed",
                      "header", "through_ball", "strong_foot"])
        prob = self.model.predict_proba(features)[0, 1]
        return round(prob, 4)

    def simulate_shot(self):
        dist = np.random.uniform(5, 30)
        ang = np.random.uniform(0, 60)
        pres = np.random.uniform(0, 0.8)
        spd = np.random.uniform(10, 28)
        xg = self.predict_xg(dist, ang, pres, spd)
        return {
            "distance": round(dist, 1),
            "angle": round(ang, 1),
            "pressure": round(pres, 2),
            "speed": round(spd, 1),
            "xG": xg,
            "goal": np.random.random() < xg
        }
