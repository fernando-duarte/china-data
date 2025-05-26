"""Total Factor Productivity (TFP) calculation module.

This module provides functions for calculating Total Factor Productivity
using the Cobb-Douglas production function.
"""

import logging

import numpy as np
import pandas as pd

from config import Config

logger = logging.getLogger(__name__)


def calculate_tfp(
    df: pd.DataFrame, alpha: float = Config.DEFAULT_ALPHA, required_columns: dict[str, str] | None = None
) -> pd.DataFrame:
    """Calculate Total Factor Productivity (TFP) using a Cobb-Douglas production function.

    Args:
        df (pd.DataFrame): Input DataFrame with required columns
        alpha (float): Capital share parameter (default: from Config)
        required_columns (dict): Mapping of required columns (default: None, uses Config)

    Returns:
        pd.DataFrame: DataFrame with TFP column added
    """
    # Create a copy to avoid modifying the original
    result = df.copy()

    # Get column mapping
    cols = required_columns or {"GDP": "GDP_USD_bn", "K": "K_USD_bn", "L": "LF_mn", "H": "hc"}

    # Check if required columns exist
    missing_cols = [col for col, name in cols.items() if name not in result.columns]
    if missing_cols:
        logger.warning("Missing columns for TFP calculation: %s", [cols[col] for col in missing_cols])
        return result

    try:
        # Extract variables
        gdp = result[cols["GDP"]]
        capital = result[cols["K"]]
        labor = result[cols["L"]]
        human_capital = result[cols["H"]]

        # Calculate TFP
        # A = Y / (K^α * (L*H)^(1-α))
        result["TFP"] = gdp / (np.power(capital, alpha) * np.power(labor * human_capital, 1 - alpha))

        logger.info("TFP calculation completed successfully")

    except Exception as e:
        logger.error("Error calculating TFP: %s", str(e))
        result["TFP"] = np.nan

    # Check if any valid TFP values were calculated
    if not result["TFP"].notna().any():
        logger.warning("No valid TFP values calculated")

    return result
