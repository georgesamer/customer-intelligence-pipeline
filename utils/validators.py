"""
File: utils/validators.py
Purpose: Data validation functions
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple, Optional

def validate_required_columns(df: pd.DataFrame, required_columns: List[str]) -> Tuple[bool, List[str]]:
    """
    Check if DataFrame has all required columns
    
    Args:
        df: Input DataFrame
        required_columns: List of required column names
    
    Returns:
        (is_valid, missing_columns)
    """
    missing = [col for col in required_columns if col not in df.columns]
    return len(missing) == 0, missing

def validate_data_types(df: pd.DataFrame, expected_types: Dict[str, str]) -> Tuple[bool, Dict[str, str]]:
    """
    Validate column data types
    
    Args:
        df: Input DataFrame
        expected_types: Dict mapping column names to expected types
    
    Returns:
        (is_valid, type_errors)
    """
    type_errors = {}
    for col, expected_type in expected_types.items():
        if col in df.columns:
            actual_type = str(df[col].dtype)
            if expected_type not in actual_type:
                type_errors[col] = f"Expected {expected_type}, got {actual_type}"
    
    return len(type_errors) == 0, type_errors

def validate_no_missing_values(df: pd.DataFrame, columns: Optional[List[str]] = None) -> Tuple[bool, Dict[str, int]]:
    """
    Check for missing values in specified columns
    
    Args:
        df: Input DataFrame
        columns: Columns to check (None = all columns)
    
    Returns:
        (is_valid, missing_counts)
    """
    if columns is None:
        columns = df.columns.tolist()
    
    missing_counts = {}
    for col in columns:
        if col in df.columns:
            missing = df[col].isnull().sum()
            if missing > 0:
                missing_counts[col] = missing
    
    return len(missing_counts) == 0, missing_counts

def validate_value_ranges(df: pd.DataFrame, ranges: Dict[str, Tuple[float, float]]) -> Tuple[bool, Dict[str, str]]:
    """
    Validate that numeric columns are within expected ranges
    
    Args:
        df: Input DataFrame
        ranges: Dict mapping column names to (min, max) tuples
    
    Returns:
        (is_valid, out_of_range)
    """
    out_of_range = {}
    for col, (min_val, max_val) in ranges.items():
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            out_of_min = (df[col] < min_val).sum()
            out_of_max = (df[col] > max_val).sum()
            if out_of_min > 0 or out_of_max > 0:
                out_of_range[col] = f"{out_of_min} below min, {out_of_max} above max"
    
    return len(out_of_range) == 0, out_of_range

def validate_unique_constraint(df: pd.DataFrame, column: str) -> Tuple[bool, int]:
    """
    Check if column has unique values
    
    Args:
        df: Input DataFrame
        column: Column to check
    
    Returns:
        (is_unique, duplicate_count)
    """
    if column not in df.columns:
        return False, 0
    
    duplicates = df.duplicated(subset=[column]).sum()
    return duplicates == 0, duplicates

def validate_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Comprehensive data quality report
    
    Args:
        df: Input DataFrame
    
    Returns:
        dict: Quality report
    """
    report = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_rows": df.duplicated().sum(),
        "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "memory_usage_mb": df.memory_usage(deep=True).sum() / (1024 * 1024)
    }
    
    # Add basic stats for numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        report["numeric_stats"] = df[numeric_cols].describe().to_dict()
    
    return report