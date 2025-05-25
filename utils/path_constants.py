"""
Path constants and utilities for the China data processing project.

This module provides centralized path management using pathlib for consistent
cross-platform path handling.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

# Directory names
INPUT_DIR_NAME = "input"
OUTPUT_DIR_NAME = "output"


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path object pointing to the project root directory
    """
    return Path(__file__).parent.parent


def get_absolute_input_path() -> Path:
    """
    Get the absolute path to the input directory.
    
    Returns:
        Path object pointing to the input directory
    """
    return get_project_root() / INPUT_DIR_NAME


def get_absolute_output_path() -> Path:
    """
    Get the absolute path to the output directory.
    
    Returns:
        Path object pointing to the output directory
    """
    return get_project_root() / OUTPUT_DIR_NAME


def get_search_locations_relative_to_root() -> dict:
    """
    Get search locations for various file types relative to project root.
    
    Returns:
        Dictionary mapping file types to lists of relative path strings
    """
    return {
        "input_files": [
            INPUT_DIR_NAME,
            f"{INPUT_DIR_NAME}/imf",
            f"{INPUT_DIR_NAME}/data",
            ".",  # Project root
        ],
        "output_files": [
            OUTPUT_DIR_NAME,
            ".",  # Project root
        ],
        "config_files": [
            ".",  # Project root
            "config",
            "parameters_info",
        ]
    }
