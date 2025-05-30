"""Total Factor Productivity (TFP) calculation module.

This module provides functions for calculating Total Factor Productivity
using the Cobb-Douglas production function.
"""

import logging

import numpy as np
import pandas as pd

try:
    from utils.logging_config import get_logger

    logger = get_logger(__name__)
except ImportError:
    # Fallback to standard logging if structured logging is not available
    logger = logging.getLogger(__name__)


def calculate_tfp(df: pd.DataFrame, alpha: float) -> pd.DataFrame:
    """Calculate Total Factor Productivity using the Cobb-Douglas production function.

    Args:
        df: DataFrame containing GDP_USD_bn, K_USD_bn, LF_mn, and hc columns
        alpha: Capital share parameter (0 < alpha < 1)

    Returns:
        DataFrame with TFP column added

    Formula:
        TFP = Y / (K^alpha * (L*H)^(1-alpha))
        Where:
        - Y = GDP (output)
        - K = Capital stock
        - L = Labor force
        - H = Human capital index
        - alpha = Capital share parameter
    """
    result = df.copy()

    try:
        # Validate required columns
        required_cols = ["GDP_USD_bn", "K_USD_bn", "LF_mn", "hc"]
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            logger.warning("Missing required columns for TFP calculation: %s", missing_cols)
            result["TFP"] = np.nan
            return result

        # Extract variables
        gdp = df["GDP_USD_bn"]
        capital = df["K_USD_bn"]
        labor = df["LF_mn"]
        human_capital = df["hc"]

        # Check for valid data (all inputs must be non-negative and not missing)
        has_valid_inputs = (
            gdp.notna()
            & capital.notna()
            & labor.notna()
            & human_capital.notna()
            & (gdp >= 0)
            & (capital > 0)
            & (labor > 0)
            & (human_capital > 0)
        )

        # Special case: when GDP is 0 but other inputs are valid, TFP is 0
        gdp_is_zero = (gdp == 0) & has_valid_inputs

        # Valid data for normal TFP calculation (GDP > 0)
        valid_for_calculation = has_valid_inputs & (gdp > 0)

        if not (valid_for_calculation.any() or gdp_is_zero.any()):
            logger.warning("No valid data points for TFP calculation")
            result["TFP"] = np.nan
            return result

        # Initialize TFP column with NaN
        result["TFP"] = np.nan

        # Calculate TFP for valid data points where GDP > 0
        if valid_for_calculation.any():
            result.loc[valid_for_calculation, "TFP"] = gdp[valid_for_calculation] / (
                np.power(capital[valid_for_calculation], alpha)
                * np.power(
                    labor[valid_for_calculation] * human_capital[valid_for_calculation], 1 - alpha
                )
            )

        # Set TFP to 0 where GDP is 0 but other inputs are valid
        if gdp_is_zero.any():
            result.loc[gdp_is_zero, "TFP"] = 0

        logger.info("TFP calculation completed successfully")

    except (ValueError, TypeError, ZeroDivisionError):
        logger.exception("Error calculating TFP")
        result["TFP"] = np.nan

    return result
