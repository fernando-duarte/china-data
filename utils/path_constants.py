"""
Path constants for the China Economic Data Analysis project.
This module centralizes all path-related constants to improve maintainability.
"""

import os
from typing import Dict, List

# Directory structure constants
INPUT_DIR_NAME = "input"
OUTPUT_DIR_NAME = "output"

# Path utility functions

def get_absolute_input_path() -> str:
    """
    Get the absolute path to the input directory (project_root/input).
    """
    from utils import get_project_root
    return os.path.join(get_project_root(), INPUT_DIR_NAME)

def get_absolute_output_path() -> str:
    """
    Get the absolute path to the output directory (project_root/output).
    """
    from utils import get_project_root
    return os.path.join(get_project_root(), OUTPUT_DIR_NAME)

# Common file paths relative to project root for searching
def get_search_locations_relative_to_root() -> Dict[str, List[str]]:
    """
    Get default search locations for different file types,
    all paths are relative to the project root.
    The find_file function will prepend get_project_root() to these.
    """
    return {
        "input_files": [
            INPUT_DIR_NAME,
        ],
        "output_files": [
            OUTPUT_DIR_NAME,
        ],
        "general": [
            INPUT_DIR_NAME,
            OUTPUT_DIR_NAME,
            "",  # project root itself
        ]
    }