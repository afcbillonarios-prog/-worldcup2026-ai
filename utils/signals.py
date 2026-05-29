import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

class SignalGenerator:
    def __init__(self):
        self.time = 0
        self.signals = {}
        self._init_signals()

    def _init_signals(self):
        self.signals = {
            "xG_dynamics": {"value": 0.0, "base": 0.08, "volatility": 0.03},
            "possession": {"value": 50, "base": 50, "volatility": 5},
            "pressing_intensity": {"value": 65, "base": 65, "volatility": 8},
            "momentum": {"value": 50, "base": 50, "volatility": 10},
            "defensive_line": {"value": 35, "base": 35, "volatility": 5},
            "fatigue": {"value": 30, "base": 30, "volatility": 5},
            "attack_danger": {"value": 40, "base": 40, "volatility": 12},
            "control_index": {"value": 50, "base": 50, "volatility": 6},
            "expected_goals": {"value": 1.2, "base": 1.2, "volatility": 0.3},
            "shot_accuracy": {"value": 45, "base": 45, "volatility": 8},
        }

    def tick(self):
        self.time += 1
        events = []
        for name, sig in self.signals.items():
            change = np.random.normal(0, sig["volatility"])
            if self.time % 15 == 0:
                change += np.random.choice([-5, 5]) * np.random.uniform(0.5, 1.5)
            new_val = sig["value"] + change * 0.3
            if name in ["xG_dynamics", "expected_goals"]:
                new_val = max(0, new_val)
            elif name in ["possession", "pressing_intensity", "momentum",
                          "shot_accuracy", "attack_danger", "control_index"]:
                new_val = np.clip(new_val, 0, 100)
            elif name == "fatigue":
                new_val = min(100, new_val)
            sig["value"] = round(new_val, 2)

        if np.random.random() < 0.05:
            events.append({
                "minute": self.time,
                "type": "goal",
                "description": "¡GOL!",
                "impact": "high"
            })
            for name in ["momentum", "attack_danger"]:
                self.signals[name]["value"] = min(100,
                    self.signals[name]["value"] + 15)
            self.signals["expected_goals"]["value"] += 0.3

        elif np.random.random() < 0.08:
            events.append({
                "minute": self.time,
                "type": "shot",
                "description": "Tiro a puerta",
                "impact": "medium"
            })
            self.signals["shot_accuracy"]["value"] += np.random.uniform(2, 8)

        return events

    def get_state(self):
        return {name: sig["value"] for name, sig in self.signals.items()}

    def reset(self):
        self.time = 0
        self._init_signals()

def generate_historical_signals(n_points=500):
    gen = SignalGenerator()
    history = []
    events_log = []
    for _ in range(n_points):
        events = gen.tick()
        state = gen.get_state()
        state["minute"] = gen.time
        history.append(state)
        for e in events:
            e["time"] = gen.time
            events_log.append(e)
    return pd.DataFrame(history), events_log
