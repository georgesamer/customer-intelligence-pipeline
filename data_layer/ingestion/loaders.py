"""
File: data_layer/ingestion/loaders.py
Purpose: Load raw data from CSV and JSON sources
"""

import os
import pandas as pd
from utils.logger import setup_logger


class CSVLoader:

    def __init__(self, file_path: str, config: dict = None):
        self.file_path = file_path
        self.config = config or {}
        self.logger = setup_logger("csv_loader")
        self.data = None

    def load(self) -> pd.DataFrame | None:
        try:
            self.logger.info(f"Loading CSV from: {self.file_path}")
            sep      = self.config.get('csv', {}).get('separator', ',')
            encoding = self.config.get('csv', {}).get('encoding', 'utf-8')
            self.data = pd.read_csv(self.file_path, sep=sep, encoding=encoding)
            self.logger.info(f"Loaded {len(self.data)} rows, {len(self.data.columns)} columns")
            return self.data
        except FileNotFoundError:
            self.logger.error(f"File not found: {self.file_path}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to load CSV: {e}")
            return None


class JSONLoader:

    def __init__(self, file_path: str, config: dict = None):
        self.file_path = file_path
        self.config = config or {}
        self.logger = setup_logger("json_loader")
        self.data = None

    def load(self) -> pd.DataFrame | None:
        try:
            if not os.path.exists(self.file_path):
                self.logger.error(f"File not found: {self.file_path}")
                return None

            self.logger.info(f"Loading JSON from: {self.file_path}")
            orient = self.config.get('json', {}).get('orient', 'records')
            self.data = pd.read_json(self.file_path, orient=orient)
            self.logger.info(f"Loaded {len(self.data)} rows, {len(self.data.columns)} columns")
            return self.data
        except Exception as e:
            self.logger.error(f"Failed to load JSON: {e}")
            return None

    def get_info(self) -> dict:
        if self.data is None:
            return {"status": "No data loaded"}
        return {
            "rows": len(self.data),
            "columns": list(self.data.columns),
            "file": self.file_path
        }