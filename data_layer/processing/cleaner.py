"""
File: data_layer/processing/cleaner.py
Purpose: Clean and preprocess raw data
"""

import pandas as pd
import numpy as np
from utils.logger import setup_logger


class DataCleaner:

    def __init__(self, dataframe: pd.DataFrame, config: dict = None):
        self.df = dataframe.copy()
        self.config = config or {}
        self.logger = setup_logger("data_cleaner")
        self.original_shape = dataframe.shape

    def clean(self) -> pd.DataFrame:
        self.logger.info("Starting data cleaning process")
        self.logger.info(f"Initial shape: {self.original_shape}")

        cleaning_config = self.config.get('cleaning', {})

        if cleaning_config.get('handle_missing', True):
            self._handle_missing_values()

        if cleaning_config.get('remove_duplicates', True):
            self._remove_duplicates()

        if cleaning_config.get('remove_outliers', False):
            self._remove_outliers()

        self.logger.info(f"Cleaning complete. Final shape: {self.df.shape}")
        return self.df

    def _handle_missing_values(self):
        missing_before = self.df.isnull().sum().sum()

        if missing_before > 0:
            self.logger.warning(f"Found {missing_before} missing values")

            strategy = self.config.get('cleaning', {}).get('missing_strategy', {})
            numeric_strategy = strategy.get('numeric', 'mean')
            categorical_fill = strategy.get('categorical', 'unknown')

            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if self.df[col].isnull().any():
                    if numeric_strategy == 'mean':
                        fill_value = self.df[col].mean()
                    elif numeric_strategy == 'median':
                        fill_value = self.df[col].median()
                    else:
                        fill_value = 0
                    self.df[col].fillna(fill_value, inplace=True)

            cat_cols = self.df.select_dtypes(include=['object']).columns
            for col in cat_cols:
                if self.df[col].isnull().any():
                    self.df[col].fillna(categorical_fill, inplace=True)

            missing_after = self.df.isnull().sum().sum()
            self.logger.info(f"Missing values: {missing_before} → {missing_after}")
        else:
            self.logger.info("No missing values found")

    def _remove_duplicates(self):
        before = len(self.df)
        self.df.drop_duplicates(inplace=True)
        after = len(self.df)
        if before > after:
            self.logger.info(f"Removed {before - after} duplicate rows")

    def _remove_outliers(self):
        threshold = self.config.get('cleaning', {}).get('outlier_threshold', 3.0)
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR

            outliers = ((self.df[col] < lower_bound) | (self.df[col] > upper_bound)).sum()
            if outliers > 0:
                self.logger.info(f"Capping {outliers} outliers in '{col}'")
                self.df[col] = self.df[col].clip(lower_bound, upper_bound)