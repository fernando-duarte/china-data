"""
Utilities for the China Economic Data Analysis project.

This module provides common utility functions used across the codebase:
- Project root and file path resolution
- Directory creation and management
- Output directory handling

The utilities handle the project's directory structure where the project root
contains the main scripts, utils/, tests/, input/, and output/ directories.
"""

import logging
from pathlib import Path
from typing import List, Optional

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
                                            If None, uses default "input_files" locations.

    Returns:
        Full path to the found file, or None if not found
    """
    project_root = Path(get_project_root())

    if possible_locations_relative_to_root is None:
        from utils.path_constants import get_search_locations_relative_to_root
        search_locations_relative = get_search_locations_relative_to_root()["input_files"]
    else:
        search_locations_relative = possible_locations_relative_to_root

    checked_paths = []
    for rel_location in search_locations_relative:
        # Construct absolute path using pathlib
        if rel_location == ".":
            # Project root
            path = project_root / filename
        else:
            path = project_root / rel_location / filename
            
        checked_paths.append(str(path))
        if path.exists():
            logger.info(f"Found file at: {path}")
            return str(path)

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
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return str(path.resolve())


def get_output_directory() -> str:
    """
    Get the path to the output directory, ensuring it exists.

    Since the project root is now the current directory,
    the output directory is simply ./output from the project root.

    Returns:
        str: Path to the output directory
    """
    # Simple path to output directory from project root
    project_root = Path(get_project_root())
    output_dir = project_root / "output"

    # Ensure the directory exists
    return ensure_directory(str(output_dir))
