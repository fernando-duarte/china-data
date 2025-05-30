"""Validation helpers for capital stock calculations."""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def _validate_input_data(raw_data: pd.DataFrame) -> tuple[bool, str]:
    """Validate input data for capital stock calculation.

    Args:
        raw_data: DataFrame to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(raw_data, pd.DataFrame):
        return False, "Invalid input type: raw_data must be a pandas DataFrame"

    if "year" not in raw_data.columns:
        return False, "Critical: 'year' column missing from input data"

    return True, ""


def _check_required_columns(capital_data: pd.DataFrame) -> list[str]:
    """Check for required columns and log alternatives if missing."""
    required_columns = ["rkna", "pl_gdpo", "cgdpo_bn"]
    missing_columns = [col for col in required_columns if col not in capital_data.columns]

    if missing_columns:
        logger.warning(
            "Missing required columns for capital stock calculation: %s", missing_columns
        )

        # Look for alternative columns that might contain the required data
        pwt_cols = [
            col
            for col in capital_data.columns
            if col.startswith("PWT") or col.lower().startswith("pwt")
        ]
        if pwt_cols:
            logger.info("Found PWT columns that might contain needed data: %s", pwt_cols)
            # Try to map PWT columns to required columns
            for col in pwt_cols:
                for req_col in missing_columns:
                    if req_col.lower() in col.lower():
                        logger.info("Potential match: '%s' might contain '%s' data", col, req_col)

    return missing_columns
