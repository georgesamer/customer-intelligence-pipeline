"""
File: ai_engine/predictor.py
Purpose: Load trained model and run inference on new data
"""

import os
import joblib
import pandas as pd
import numpy as np
from utils.logger import setup_logger
from utils.file_utils import ensure_dir, save_json


class ModelPredictor:

    def __init__(self, model_path: str = None, config: dict = None):
        self.config = config or {}
        self.logger = setup_logger("predictor")
        self.model = None
        self.model_path = model_path

        if model_path:
            self.load_model(model_path)

    def load_model(self, model_path: str) -> bool:
        """Load trained model from disk"""
        if not os.path.exists(model_path):
            self.logger.error(f"Model file not found: {model_path}")
            return False

        try:
            self.model = joblib.load(model_path)
            self.model_path = model_path
            self.logger.info(f"Model loaded from: {model_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            return False

    def predict(self, df: pd.DataFrame) -> np.ndarray | None:
        """
        Run prediction on new data

        Args:
            df: DataFrame with same features used in training

        Returns:
            numpy array of predictions, or None if model not loaded
        """
        if self.model is None:
            self.logger.error("No model loaded — call load_model() first")
            return None

        try:
            self.logger.info(f"Running prediction on {len(df)} rows")
            predictions = self.model.predict(df)
            self.logger.info(f"Predictions done: {len(predictions)} results")
            return predictions
        except Exception as e:
            self.logger.error(f"Prediction failed: {e}")
            return None

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray | None:
        """
        Return prediction probabilities (for classifiers only)

        Args:
            df: DataFrame with same features used in training

        Returns:
            numpy array of probabilities, or None
        """
        if self.model is None:
            self.logger.error("No model loaded")
            return None

        if not hasattr(self.model, 'predict_proba'):
            self.logger.warning("Model doesn't support predict_proba")
            return None

        try:
            proba = self.model.predict_proba(df)
            self.logger.info(f"Probabilities computed: shape {proba.shape}")
            return proba
        except Exception as e:
            self.logger.error(f"predict_proba failed: {e}")
            return None

    def predict_and_save(self, df: pd.DataFrame,
                         output_path: str = "outputs/predictions.csv") -> str | None:
        """
        Predict and save results to CSV

        Args:
            df: Input DataFrame
            output_path: Where to save predictions

        Returns:
            Path to saved file, or None
        """
        predictions = self.predict(df)

        if predictions is None:
            return None

        ensure_dir(os.path.dirname(output_path))

        result_df = df.copy()
        result_df['prediction'] = predictions

        # لو الموديل بيدعم probabilities نضيفها
        proba = self.predict_proba(df)
        if proba is not None:
            result_df['confidence'] = proba.max(axis=1).round(4)

        result_df.to_csv(output_path, index=False)
        self.logger.info(f"Predictions saved to: {output_path}")

        return output_path

    def get_model_info(self) -> dict:
        """Return basic info about the loaded model"""
        if self.model is None:
            return {"status": "No model loaded"}

        return {
            "model_type": type(self.model).__name__,
            "model_path": self.model_path,
            "has_predict_proba": hasattr(self.model, 'predict_proba'),
            "params": self.model.get_params() if hasattr(self.model, 'get_params') else {}
        }