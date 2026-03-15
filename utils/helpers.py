"""
File: utils/helpers.py
Purpose: General helper functions used across the pipeline
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Any, Dict, List, Optional

def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """
    Safe division to avoid division by zero
    
    Args:
        a: Numerator
        b: Denominator
        default: Default value if denominator is 0
    
    Returns:
        float: Result of division or default
    """
    try:
        return a / b if b != 0 and b is not None else default
    except:
        return default

def parse_date_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Safely parse a column as datetime
    
    Args:
        df: Input DataFrame
        column: Column name to parse
    
    Returns:
        DataFrame with parsed column
    """
    try:
        df[column] = pd.to_datetime(df[column])
    except:
        df[column] = pd.NaT
    return df

def get_timestamp() -> str:
    """Get current timestamp as string (YYYYMMDD_HHMMSS)"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def format_currency(value: float) -> str:
    """Format number as currency"""
    return f"${value:,.2f}"

def chunk_dataframe(df: pd.DataFrame, chunk_size: int = 1000):
    """
    Split DataFrame into chunks for processing large data
    
    Args:
        df: Input DataFrame
        chunk_size: Number of rows per chunk
    
    Yields:
        DataFrame chunks
    """
    for i in range(0, len(df), chunk_size):
        yield df.iloc[i:i + chunk_size]

def memory_usage(df: pd.DataFrame) -> str:
    """
    Get memory usage of DataFrame in human-readable format
    
    Args:
        df: Input DataFrame
    
    Returns:
        str: Memory usage (e.g., "15.2 MB")
    """
    memory_bytes = df.memory_usage(deep=True).sum()
    memory_mb = memory_bytes / (1024 * 1024)
    return f"{memory_mb:.2f} MB"

def is_numeric_column(df: pd.DataFrame, column: str) -> bool:
    """Check if column is numeric"""
    return column in df.columns and pd.api.types.is_numeric_dtype(df[column])

def safe_get(df: pd.DataFrame, column: str, default: Any = None) -> Any:
    """Safely get column from DataFrame"""
    return df[column] if column in df.columns else default

def clean_string(text: str) -> str:
    """Clean string by stripping and lowercasing"""
    if pd.isna(text):
        return ""
    return str(text).strip().lower()