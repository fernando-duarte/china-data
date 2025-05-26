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

        # Check for valid data
        valid_mask = (
            gdp.notna()
            & capital.notna()
            & labor.notna()
            & human_capital.notna()
            & (gdp > 0)
            & (capital > 0)
            & (labor > 0)
            & (human_capital > 0)
        )

        if not valid_mask.any():
            logger.warning("No valid data points for TFP calculation")
            result["TFP"] = np.nan
            return result

        # Calculate TFP using Cobb-Douglas production function
        result["TFP"] = gdp / (np.power(capital, alpha) * np.power(labor * human_capital, 1 - alpha))

        # Set invalid calculations to NaN
        result.loc[~valid_mask, "TFP"] = np.nan

        logger.info("TFP calculation completed successfully")

    except (ValueError, TypeError, ZeroDivisionError):
        logger.exception("Error calculating TFP")
        result["TFP"] = np.nan

    return result
