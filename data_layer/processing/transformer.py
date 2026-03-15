"""
File: data_layer/processing/transformer.py
Purpose: Feature engineering and export for AI engine
"""

import pandas as pd
import numpy as np
from datetime import datetime
from utils.logger import setup_logger
from utils.file_utils import ensure_dir, save_json
from utils.helpers import safe_divide, parse_date_column


class DataTransformer:

    def __init__(self, dataframe: pd.DataFrame, config: dict = None):
        self.df = dataframe.copy()
        self.config = config or {}
        self.logger = setup_logger("transformer")
        self.features = None
        ensure_dir("outputs")

    def transform(self) -> pd.DataFrame:
        """Execute all feature engineering steps"""
        self.logger.info("Starting feature engineering")
        self.features = self.df.copy()

        column_mappings = self.config.get('features', {}).get('column_mappings', {})
        features_config = self.config.get('features', {})

        if features_config.get('create_days_since_last_purchase', True):
            self._add_last_purchase_features(column_mappings)

        if features_config.get('create_avg_purchase_amount', True):
            self._add_average_features(column_mappings)

        if features_config.get('create_customer_value_segments', True):
            self._add_value_features(column_mappings)

        if features_config.get('create_purchase_frequency', True):
            self._add_frequency_features(column_mappings)

        self.logger.info(f"Built {len(self.features.columns)} features")
        return self.features

    def export(self, format: str = "csv") -> str:
        """Save transformed features to outputs/"""
        if self.features is None:
            self.features = self.transform()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format == "csv":
            path = f"outputs/features_{timestamp}.csv"
            self.features.to_csv(path, index=False)
        elif format == "json":
            path = f"outputs/features_{timestamp}.json"
            self.features.to_json(path, orient="records")
        else:
            raise ValueError(f"Unsupported format: {format}")

        self.logger.info(f"Saved features to: {path}")
        self._save_metadata(timestamp, path)
        return path

    def _save_metadata(self, timestamp: str, filename: str):
        metadata = {
            "export_time": datetime.now().isoformat(),
            "total_rows": len(self.features),
            "total_columns": len(self.features.columns),
            "columns": list(self.features.columns),
            "file": filename,
            "data_types": {
                col: str(dtype)
                for col, dtype in self.features.dtypes.items()
            },
            "memory_usage_mb": round(
                self.features.memory_usage(deep=True).sum() / (1024 * 1024), 4
            )
        }
        save_json(metadata, f"outputs/metadata_{timestamp}.json")

        sample_size = self.config.get('export', {}).get('sample_size', 5)
        self.features.head(sample_size).to_csv(
            f"outputs/sample_{timestamp}.csv", index=False
        )

    # ─── Feature methods (نفس الكود القديم بالظبط) ───────────────────

    def _add_last_purchase_features(self, column_mappings: dict):
        date_col = column_mappings.get('last_purchase_date')

        if date_col and date_col in self.df.columns:
            try:
                df_with_date = parse_date_column(self.df, date_col)
                self.features['days_since_last_purchase'] = (
                    datetime.now() - df_with_date[date_col]
                ).dt.days.clip(lower=0)
                mean_days = self.features['days_since_last_purchase'].mean()
                self.logger.info(f"Added 'days_since_last_purchase' (mean: {mean_days:.1f} days)")
            except Exception as e:
                self.logger.warning(f"Could not parse dates: {e}")
                self.features['days_since_last_purchase'] = 0
        else:
            self.logger.warning(f"Date column '{date_col}' not found, defaulting to 0")
            self.features['days_since_last_purchase'] = 0

    def _add_average_features(self, column_mappings: dict):
        total_spent_col = column_mappings.get('total_spent')
        total_purchases_col = column_mappings.get('total_purchases')

        if total_spent_col and total_purchases_col:
            if total_spent_col in self.df.columns and total_purchases_col in self.df.columns:
                self.features['avg_purchase_amount'] = (
                    self.df[total_spent_col] / self.df[total_purchases_col].clip(lower=1)
                ).round(2)
                mean_avg = self.features['avg_purchase_amount'].mean()
                self.logger.info(f"Added 'avg_purchase_amount' (mean: ${mean_avg:.2f})")
            else:
                self.logger.warning("Required columns not found for avg_purchase_amount")
                self.features['avg_purchase_amount'] = 0
        else:
            self.logger.warning("Column mappings not configured for average features")
            self.features['avg_purchase_amount'] = 0

    def _add_value_features(self, column_mappings: dict):
        total_spent_col = column_mappings.get('total_spent')

        if total_spent_col and total_spent_col in self.df.columns:
            self.features['customer_lifetime_value'] = self.df[total_spent_col]

            segments_config = self.config.get('features', {}).get('value_segments', {})
            low    = segments_config.get('low', 0)
            medium = segments_config.get('medium', 100)
            high   = segments_config.get('high', 500)

            self.features['value_segment'] = pd.cut(
                self.features['customer_lifetime_value'],
                bins=[low, medium, high, float('inf')],
                labels=['Low', 'Medium', 'High']
            )
            segment_counts = self.features['value_segment'].value_counts().to_dict()
            self.logger.info(f"Added value segments: {segment_counts}")
        else:
            self.logger.warning("total_spent not found, estimating LTV")
            self.features['customer_lifetime_value'] = (
                self.features.get('avg_purchase_amount', 0) * 5
            )

    def _add_frequency_features(self, column_mappings: dict):
        total_purchases_col = column_mappings.get('total_purchases')

        if total_purchases_col and total_purchases_col in self.df.columns:
            self.features['purchase_frequency'] = self.df[total_purchases_col]
            # TODO: حسابها من تواريخ حقيقية لما يبقى فيه date column
            self.features['purchase_regularity'] = np.random.uniform(
                0.5, 1.0, len(self.df)
            ).round(2)
            mean_freq = self.features['purchase_frequency'].mean()
            self.logger.info(f"Added 'purchase_frequency' (mean: {mean_freq:.1f})")
        else:
            self.logger.warning("total_purchases not found, using simulated values")
            self.features['purchase_frequency'] = np.random.randint(1, 20, len(self.df))
            self.features['purchase_regularity'] = np.random.uniform(
                0.3, 1.0, len(self.df)
            ).round(2)