"""
Tests for data_layer/ingestion/loaders.py
"""

import pytest
import pandas as pd
import os
from data_layer.ingestion.loaders import CSVLoader, JSONLoader


@pytest.fixture
def sample_csv(tmp_path):
    """Create a temp CSV file for testing"""
    df = pd.DataFrame({
        'customer_id': [1, 2, 3],
        'age': [25, 30, 35],
        'total_purchases': [5, 10, 15],
        'total_spent': [100.0, 200.0, 300.0]
    })
    path = tmp_path / "test_customers.csv"
    df.to_csv(path, index=False)
    return str(path)


@pytest.fixture
def sample_json(tmp_path):
    """Create a temp JSON file for testing"""
    df = pd.DataFrame({
        'customer_id': [1, 2, 3],
        'total_spent': [100.0, 200.0, 300.0]
    })
    path = tmp_path / "test_customers.json"
    df.to_json(path, orient='records')
    return str(path)


def test_csv_loader_loads_correctly(sample_csv):
    loader = CSVLoader(sample_csv)
    df = loader.load()
    assert df is not None
    assert len(df) == 3
    assert 'customer_id' in df.columns


def test_csv_loader_returns_none_on_missing_file():
    loader = CSVLoader("nonexistent/path.csv")
    df = loader.load()
    assert df is None


def test_json_loader_loads_correctly(sample_json):
    loader = JSONLoader(sample_json)
    df = loader.load()
    assert df is not None
    assert len(df) == 3


def test_json_loader_returns_none_on_missing_file():
    loader = JSONLoader("nonexistent/path.json")
    df = loader.load()
    assert df is None