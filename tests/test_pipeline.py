"""
Integration test — runs the full pipeline end to end
"""

import pytest
import pandas as pd
from core.pipeline import CustomerPipeline


@pytest.fixture
def sample_csv(tmp_path):
    df = pd.DataFrame({
        'customer_id': [1001, 1002, 1003],
        'age': [25, 30, 35],
        'total_purchases': [5, 10, 15],
        'total_spent': [500.0, 1500.0, 3500.0]
    })
    path = tmp_path / "customers.csv"
    df.to_csv(path, index=False)
    return str(path)


def test_pipeline_runs_without_error(sample_csv):
    pipeline = CustomerPipeline()
    result = pipeline.run_from_csv(sample_csv)
    assert result is not None


def test_pipeline_returns_dataframe(sample_csv):
    pipeline = CustomerPipeline()
    result = pipeline.run_from_csv(sample_csv)
    assert isinstance(result, pd.DataFrame)


def test_pipeline_adds_features(sample_csv):
    pipeline = CustomerPipeline()
    result = pipeline.run_from_csv(sample_csv)
    # الـ transformer لازم يضيف columns جديدة
    assert len(result.columns) > 4


def test_pipeline_fails_gracefully_on_bad_path():
    pipeline = CustomerPipeline()
    result = pipeline.run_from_csv("bad/path.csv")
    assert result is None