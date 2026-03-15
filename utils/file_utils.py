"""
File: utils/file_utils.py
Purpose: Helper functions for file operations
"""

import os
import json
import yaml
import pandas as pd
from typing import Dict, Any, Optional

def ensure_dir(directory: str) -> str:
    """
    Create directory if it doesn't exist
    
    Args:
        directory: Directory path
    
    Returns:
        directory: Same directory path
    """
    os.makedirs(directory, exist_ok=True)
    return directory

def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load YAML configuration file
    
    Args:
        config_path: Path to YAML config file
    
    Returns:
        dict: Configuration dictionary
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"⚠️ Config file not found: {config_path}")
        return {}
    except Exception as e:
        print(f"⚠️ Error loading config: {e}")
        return {}

def save_json(data: Dict[str, Any], filepath: str) -> None:
    """
    Save data as JSON file
    
    Args:
        data: Dictionary to save
        filepath: Output file path
    """
    ensure_dir(os.path.dirname(filepath))
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_json(filepath: str) -> Dict[str, Any]:
    """
    Load JSON file
    
    Args:
        filepath: Path to JSON file
    
    Returns:
        dict: Loaded JSON data
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️ JSON file not found: {filepath}")
        return {}
    except Exception as e:
        print(f"⚠️ Error loading JSON: {e}")
        return {}

def get_file_size_mb(filepath: str) -> float:
    """
    Get file size in megabytes
    
    Args:
        filepath: Path to file
    
    Returns:
        float: File size in MB
    """
    return os.path.getsize(filepath) / (1024 * 1024)

def list_files(directory: str, extension: Optional[str] = None) -> list:
    """
    List files in directory, optionally filter by extension
    
    Args:
        directory: Directory to scan
        extension: File extension to filter (e.g., '.csv')
    
    Returns:
        list: List of file paths
    """
    files = []
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            if extension:
                if file.endswith(extension):
                    files.append(file_path)
            else:
                files.append(file_path)
    return files

def file_exists(filepath: str) -> bool:
    """Check if file exists"""
    return os.path.exists(filepath)