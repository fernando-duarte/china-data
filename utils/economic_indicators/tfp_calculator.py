"""
Total Factor Productivity (TFP) calculation module.

This module provides functions for calculating Total Factor Productivity
using the Cobb-Douglas production function.
"""

import logging

import numpy as np
import pandas as pd

from config import Config

logger = logging.getLogger(__name__)


def calculate_tfp(data: pd.DataFrame, alpha: float = Config.DEFAULT_ALPHA) -> pd.DataFrame:
    """
    Calculate Total Factor Productivity (TFP) using the Cobb-Douglas production function.

    TFP is calculated as: TFP = Y / (K^α * (L*h)^(1-α))
    where Y is GDP, K is capital stock, L is labor force, h is human capital, and α is capital share.

    Args:
        data: DataFrame containing GDP, capital stock, labor force, and human capital data.
              Must have columns: GDP_USD_bn, K_USD_bn, LF_mn, hc
        alpha: Capital share parameter in the production function (0 < α < 1).
               Default value from Config.DEFAULT_ALPHA

    Returns:
        DataFrame with added TFP column, rounded to Config.DECIMAL_PLACES_RATIOS decimal places.
        Returns NaN for TFP where required data is missing.

    Note:
        The function assumes a Cobb-Douglas production function and requires all input
        variables to be positive for meaningful TFP calculation.
    """
    df = data.copy()

    # Validate required columns
    required_columns = ["GDP_USD_bn", "K_USD_bn", "LF_mn", "hc"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.warning(f"Missing columns for TFP calculation: {missing_columns}")
        df["TFP"] = np.nan
        return df

    # Validate alpha parameter
    if not (0 < alpha < 1):
        logger.warning(f"Invalid alpha value: {alpha}. Must be between 0 and 1.")
        df["TFP"] = np.nan
        return df

    try:
        # Calculate TFP using Cobb-Douglas production function
        # TFP = Y / (K^α * (L*h)^(1-α))
        df["TFP"] = df["GDP_USD_bn"] / ((df["K_USD_bn"] ** alpha) * ((df["LF_mn"] * df["hc"]) ** (1 - alpha)))
        df["TFP"] = df["TFP"].round(Config.DECIMAL_PLACES_RATIOS)

        # Log statistics
        valid_tfp = df["TFP"].dropna()
        if len(valid_tfp) > 0:
            logger.debug(
                f"TFP calculated for {len(valid_tfp)} observations. "
                f"Range: {valid_tfp.min():.4f} to {valid_tfp.max():.4f}"
            )
        else:
            logger.warning("No valid TFP values calculated")

    except Exception as e:
        logger.error(f"Error calculating TFP: {e}")
        df["TFP"] = np.nan

    return df
