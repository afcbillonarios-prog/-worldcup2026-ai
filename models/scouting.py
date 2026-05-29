import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

class ScoutingEngine:
    def __init__(self, players_df):
        self.df = players_df
        self.scaler = StandardScaler()
        self.kmeans = None
        self.pca = PCA(n_components=2)
        self._cluster_players()

    def _cluster_players(self):
        features = ["overall", "pace", "shooting", "passing",
                    "dribbling", "defending", "physical", "age"]
        X = self.df[features].values
        X_scaled = self.scaler.fit_transform(X)
        self.kmeans = KMeans(n_clusters=6, random_state=42, n_init=10)
        self.df["role_cluster"] = self.kmeans.fit_predict(X_scaled)

        pca_result = self.pca.fit_transform(X_scaled)
        self.df["pca_x"] = pca_result[:, 0]
        self.df["pca_y"] = pca_result[:, 1]

        cluster_labels = {
            0: "Creadores", 1: "Finalizadores", 2: "Destructores",
            3: "Velocistas", 4: "Técnicos", 5: "Versátiles"
        }
        self.df["cluster_name"] = self.df["role_cluster"].map(cluster_labels)

    def find_similar(self, player_name, n=5):
        target = self.df[self.df["name"] == player_name]
        if target.empty:
            return self.df.head(n)
        target_idx = target.index[0]
        features = ["overall", "pace", "shooting", "passing",
                    "dribbling", "defending", "physical", "age"]
        X = self.df[features].values
        target_vec = X[target_idx].reshape(1, -1)
        from sklearn.metrics.pairwise import euclidean_distances
        dists = euclidean_distances(X, target_vec).flatten()
        similar_idx = np.argsort(dists)[1:n+1]
        result = self.df.iloc[similar_idx].copy()
        result["similarity"] = 100 - (dists[similar_idx] / dists[similar_idx].max() * 30)
        result["similarity"] = result["similarity"].clip(0, 100).round(1)
        return result

    def get_cluster_summary(self):
        summary = self.df.groupby("cluster_name").agg(
            count=("id", "count"),
            avg_overall=("overall", "mean"),
            avg_age=("age", "mean"),
            avg_value=("market_value", "mean"),
        ).round(1)
        return summary

    def find_undervalued(self, min_overall=75, n=10):
        candidates = self.df[self.df["overall"] >= min_overall].copy()
        candidates["value_ratio"] = candidates["overall"] / (candidates["market_value"] + 1)
        return candidates.nlargest(n, "value_ratio")
