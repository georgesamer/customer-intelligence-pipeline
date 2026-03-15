"""
Tests for data_layer/processing/cleaner.py
"""

import pytest
import pandas as pd
import numpy as np
from data_layer.processing.cleaner import DataCleaner


@pytest.fixture
def dirty_df():
    """DataFrame with missing values and duplicates"""
    return pd.DataFrame({
        'customer_id': [1, 2, 3, 3],       # duplicate
        'age': [25, None, 35, 35],          # missing
        'total_spent': [100.0, 200.0, None, 300.0]  # missing
    })


@pytest.fixture
def clean_df():
    return pd.DataFrame({
        'customer_id': [1, 2, 3],
        'age': [25, 30, 35],
        'total_spent': [100.0, 200.0, 300.0]
    })


def test_cleaner_removes_duplicates(dirty_df):
    cleaner = DataCleaner(dirty_df)
    result = cleaner.clean()
    assert len(result) == 3


def test_cleaner_fills_missing_numeric(dirty_df):
    cleaner = DataCleaner(dirty_df)
    result = cleaner.clean()
    assert result.isnull().sum().sum() == 0


def test_cleaner_returns_dataframe(clean_df):
    cleaner = DataCleaner(clean_df)
    result = cleaner.clean()
    assert isinstance(result, pd.DataFrame)


def test_cleaner_doesnt_modify_original(dirty_df):
    original_nulls = dirty_df.isnull().sum().sum()
    cleaner = DataCleaner(dirty_df)
    cleaner.clean()
    # الـ original مش اتغير لأن بنعمل .copy() في __init__
    assert dirty_df.isnull().sum().sum() == original_nulls