"""Fallback data loader for China economic data.

This module provides functionality to load data from existing china_data_raw.md files
as fallback when primary data sources are unavailable.
"""

import logging
from pathlib import Path

import pandas as pd

from utils.error_handling import DataValidationError, FileOperationError, log_error_with_context

from .fallback_utils import (
    _convert_to_numeric,
    _read_and_parse_markdown_table,
    _split_into_indicators,
)

logger = logging.getLogger(__name__)


def _raise_no_indicators_error(fallback_data: pd.DataFrame) -> None:
    """Raise error when no valid indicators are found.

    Args:
        fallback_data: DataFrame that was processed

    Raises:
        DataValidationError: Always raised with details about available columns
    """
    raise DataValidationError(
        column="fallback_data",
        message="No valid indicators found in fallback data",
        data_info=f"Available columns: {list(fallback_data.columns)}",
    )


def load_fallback_data(output_dir: str) -> dict[str, pd.DataFrame] | None:
    """Load data from existing china_data_raw.md file as fallback.

    Args:
        output_dir: Directory where china_data_raw.md is located

    Returns:
        Dictionary of dataframes by indicator name, or None if file not found

    Raises:
        FileOperationError: If file operations fail
        DataValidationError: If data validation fails
    """
    fallback_file = Path(output_dir) / "china_data_raw.md"
    if not fallback_file.exists():
        logger.warning("Fallback file %s not found", fallback_file)
        return None

    logger.info("Loading fallback data from %s", fallback_file)

    try:
        # Parse markdown table
        fallback_data = _read_and_parse_markdown_table(fallback_file)

        # Convert to numeric types
        fallback_data = _convert_to_numeric(fallback_data)

        # Split into indicators
        result = _split_into_indicators(fallback_data)

        if not result:
            _raise_no_indicators_error(fallback_data)

        logger.info("Successfully loaded fallback data with %d indicators", len(result))
    except (FileOperationError, DataValidationError):
        raise
    except Exception as e:
        log_error_with_context(
            logger,
            "Unexpected error loading fallback data",
            e,
            context={"fallback_file": fallback_file},
        )
        raise FileOperationError(
            operation="parse",
            filepath=str(fallback_file),
            message="Unexpected error during fallback data parsing",
            original_error=e,
        ) from e

    return result
