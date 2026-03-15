"""
File: ai_engine/trainer.py
Purpose: Train KMeans clustering model on customer features
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from datetime import datetime
from utils.logger import setup_logger
from utils.file_utils import ensure_dir, save_json


class ModelTrainer:

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.logger = setup_logger("trainer")
        self.model = None
        self.scaler = StandardScaler()
        ensure_dir("ai_engine/models")

    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        اختار الـ numeric features بس وشيل الـ columns
        اللي مش مفيدة للـ clustering
        """
        exclude_cols = ['customer_id', 'value_segment', 'purchase_regularity']
        feature_cols = [
            col for col in df.select_dtypes(include=[np.number]).columns
            if col not in exclude_cols
        ]

        self.logger.info(f"Training on features: {feature_cols}")
        return df[feature_cols].fillna(0)

    def find_best_k(self, X_scaled: np.ndarray,
                    k_range: range = range(2, 7)) -> int:
        """
        جرب قيم مختلفة لـ K واختار الأحسن
        عن طريق silhouette score
        """
        scores = {}
        for k in k_range:
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = km.fit_predict(X_scaled)
            score = silhouette_score(X_scaled, labels)
            scores[k] = round(score, 4)
            self.logger.info(f"K={k}, silhouette score: {score:.4f}")

        best_k = max(scores, key=scores.get)
        self.logger.info(f"Best K: {best_k} (score: {scores[best_k]})")
        return best_k

    def train(self, df: pd.DataFrame, n_clusters: int = None) -> pd.DataFrame:
        """
        Train KMeans and return df with cluster labels
        """
        # جهز الـ features
        X = self.prepare_data(df)

        # Scale
        X_scaled = self.scaler.fit_transform(X)

        # لو مش محدد K، دور على الأحسن
        if n_clusters is None:
            n_clusters = self.find_best_k(X_scaled)

        self.logger.info(f"Training KMeans with K={n_clusters}")

        # Train
        self.model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = self.model.fit_predict(X_scaled)

        # ضيف الـ cluster label على الـ df
        result_df = df.copy()
        result_df['cluster'] = labels

        # احسب إحصائيات كل cluster
        self._log_cluster_stats(result_df, X.columns.tolist())

        # احفظ الموديل
        self._save_model()

        return result_df

    def _log_cluster_stats(self, df: pd.DataFrame, feature_cols: list):
        """اطبع ملخص كل cluster"""
        self.logger.info("\n--- Cluster Summary ---")
        for cluster_id in sorted(df['cluster'].unique()):
            cluster_df = df[df['cluster'] == cluster_id]
            self.logger.info(
                f"Cluster {cluster_id}: {len(cluster_df)} customers | "
                f"avg_spent={cluster_df['total_spent'].mean():.0f} | "
                f"avg_purchases={cluster_df['total_purchases'].mean():.1f}"
            )

    def _save_model(self):
        """احفظ الموديل والـ scaler"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = f"ai_engine/models/kmeans_{timestamp}.pkl"
        scaler_path = f"ai_engine/models/scaler_{timestamp}.pkl"

        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)

        self.logger.info(f"Model saved: {model_path}")
        self.logger.info(f"Scaler saved: {scaler_path}")

        # احفظ الـ paths في ملف عشان الـ predictor يلاقيهم
        save_json(
            {"model": model_path, "scaler": scaler_path},
            "ai_engine/models/latest.json"
        )