"""
Utilities for the China Economic Data Analysis project.
Contains common utility functions used across the codebase.
"""

import os
import logging
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)


def get_project_root() -> str:
    """
    Get the project root directory.
    
    Since the current directory structure is the project root 
    (what used to be inside the china_data folder), we can 
    simply use the directory containing this utils module.
    
    Returns:
        str: Path to the project root directory
    """
    # Simple path resolution from this file to the project root
    # utils/__init__.py -> project root is the parent directory
    return str(Path(__file__).parent.parent)


def find_file(filename: str, possible_locations_relative_to_root: Optional[List[str]] = None) -> Optional[str]:
    """
    Find a file by searching multiple possible locations relative to the project root.

    Args:
        filename: Name of the file to find (e.g., "china_data_raw.md")
        possible_locations_relative_to_root: List of directories relative to project root to search.
                                            If None, uses default "general" locations.

    Returns:
        Full path to the found file, or None if not found
    """
    project_root = get_project_root()

    if possible_locations_relative_to_root is None:
        from utils.path_constants import get_search_locations_relative_to_root
        search_locations_relative = get_search_locations_relative_to_root()["general"]
    else:
        search_locations_relative = possible_locations_relative_to_root

    checked_paths = []
    for rel_location in search_locations_relative:
        # Construct absolute path by joining project_root, the relative location, and filename
        # If rel_location is an empty string (representing project root itself),
        # os.path.join handles it correctly.
        path = os.path.join(project_root, rel_location, filename)
        checked_paths.append(path)
        if os.path.exists(path):
            logger.info(f"Found file at: {path}")
            return path

    logger.warning(f"File '{filename}' not found. Searched in: {checked_paths}")
    return None


def ensure_directory(directory: str) -> str:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        directory: Directory path to ensure exists

    Returns:
        The absolute path to the directory
    """
    os.makedirs(directory, exist_ok=True)
    return os.path.abspath(directory)


def get_output_directory() -> str:
    """
    Get the path to the output directory, ensuring it exists.
    
    Since the project root is now the current directory,
    the output directory is simply ./output from the project root.

    Returns:
        str: Path to the output directory
    """
    # Simple path to output directory from project root
    project_root = get_project_root()
    output_dir = os.path.join(project_root, "output")
    
    # Ensure the directory exists
    return ensure_directory(output_dir)