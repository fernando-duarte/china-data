"""Validation utilities for capital stock projection."""

import logging
import pandas as pd

logger = logging.getLogger(__name__)


def _validate_inputs(processed_data: pd.DataFrame) -> tuple[bool, str]:
    """Validate input data for capital stock projection."""
    if not isinstance(processed_data, pd.DataFrame):
        return False, "Invalid input type: processed_data must be a pandas DataFrame"

    required_columns = ["year", "K_USD_bn", "I_USD_bn"]
    for column in required_columns:
        if column not in processed_data.columns:
            return False, f"Required '{column}' column not found in data"

    k_data_not_na = processed_data.dropna(subset=["K_USD_bn"])
    if len(k_data_not_na) == 0:
        return False, "No non-NA capital stock data available for projection"

    return True, ""


def _get_last_capital_value(capital_data: pd.DataFrame) -> tuple[float, int]:
    """Get the last valid capital stock value and year."""
    k_data_not_na = capital_data.dropna(subset=["K_USD_bn"])
    last_year_with_data = k_data_not_na["year"].max()
    last_k = (
        k_data_not_na.loc[k_data_not_na.year == last_year_with_data, "K_USD_bn"]
        .iloc[0]
    )

    if pd.isna(last_k) or last_k <= 0:
        error_msg = (
            f"Invalid capital stock value for year {last_year_with_data}: {last_k}"
        )
        raise ValueError(error_msg)

    return float(last_k), int(last_year_with_data)
