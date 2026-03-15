"""
File: core/config.py
Purpose: Central config loader — reads both YAML files
"""

import os
from utils.file_utils import load_config

CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config')

PIPELINE_CONFIG_PATH = os.path.join(CONFIG_DIR, 'pipeline_config.yaml')
FEATURES_CONFIG_PATH = os.path.join(CONFIG_DIR, 'features_config.yaml')


class Config:

    def __init__(self, pipeline_path: str = None, features_path: str = None):
        self._pipeline = load_config(pipeline_path or PIPELINE_CONFIG_PATH)
        self._features = load_config(features_path or FEATURES_CONFIG_PATH)

    # ─── General ──────────────────────────────────────────────
    @property
    def project_name(self) -> str:
        return self._pipeline.get('general', {}).get('project_name', 'Customer Pipeline')

    @property
    def environment(self) -> str:
        return self._pipeline.get('general', {}).get('environment', 'development')

    # ─── Ingestion ────────────────────────────────────────────
    @property
    def ingestion(self) -> dict:
        return self._pipeline.get('ingestion', {})

    # ─── Cleaning ─────────────────────────────────────────────
    @property
    def cleaning(self) -> dict:
        return self._pipeline.get('cleaning', {})

    # ─── Features (pipeline switches) ─────────────────────────
    @property
    def features(self) -> dict:
        return self._pipeline.get('features', {})

    # ─── Feature definitions + groups (من features_config) ────
    @property
    def feature_definitions(self) -> dict:
        return self._features.get('feature_definitions', {})

    @property
    def feature_groups(self) -> dict:
        return self._features.get('feature_groups', {})

    @property
    def targets(self) -> dict:
        return self._features.get('targets', {})

    def get_feature_group(self, group: str = 'all_features') -> list:
        """مثلاً: config.get_feature_group('basic_features')"""
        return self._features.get('feature_groups', {}).get(group, [])

    # ─── Export ───────────────────────────────────────────────
    @property
    def export(self) -> dict:
        return self._pipeline.get('export', {})

    # ─── Logging ──────────────────────────────────────────────
    @property
    def logging(self) -> dict:
        return self._pipeline.get('logging', {})

    @property
    def log_level(self) -> str:
        return self._pipeline.get('logging', {}).get('level', 'INFO')

    # ─── Helpers ──────────────────────────────────────────────
    def as_dict(self) -> dict:
        """للـ modules اللي بتاخد config: dict — بيدمج الاتنين"""
        return {**self._pipeline, **{'feature_definitions': self._features}}