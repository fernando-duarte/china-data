"""
Economic indicators calculation module.

This module provides functions for calculating various economic indicators
including tax revenue, openness ratios, and saving measures.
"""

import logging
from typing import Optional

import numpy as np
import pandas as pd

from config import Config

from .tfp_calculator import calculate_tfp

logger = logging.getLogger(__name__)


def calculate_economic_indicators(
    merged: pd.DataFrame, alpha: float = Config.DEFAULT_ALPHA, logger: Optional[logging.Logger] = None
) -> pd.DataFrame:
    """
    Calculate comprehensive economic indicators from merged economic data.

    This function calculates multiple economic indicators including:
    - Total Factor Productivity (TFP)
    - Tax revenue in USD billions
    - Trade openness ratio
    - Net exports
    - Various saving measures (total, private, public)
    - Saving rates

    Args:
        merged: DataFrame containing merged economic data with columns such as
                GDP_USD_bn, K_USD_bn, LF_mn, hc, TAX_pct_GDP, X_USD_bn, M_USD_bn, etc.
        alpha: Capital share parameter for TFP calculation (0 < α < 1).
               Default value from Config.DEFAULT_ALPHA
        logger: Optional logger instance for detailed logging. If None, uses module logger.

    Returns:
        DataFrame with all original columns plus calculated economic indicators:
        - TFP: Total Factor Productivity
        - T_USD_bn: Tax revenue in USD billions
        - Openness_Ratio: Trade openness (exports + imports) / GDP
        - NX_USD_bn: Net exports (exports - imports)
        - S_USD_bn: Total saving (investment)
        - S_priv_USD_bn: Private saving
        - S_pub_USD_bn: Public saving (tax revenue - government spending)
        - Saving_Rate: Total saving rate (saving / GDP)

    Note:
        Missing data in input columns will result in NaN values for dependent indicators.
        The function handles missing data gracefully and logs warnings for missing columns.
    """
    if logger is None:
        logger = globals()["logger"]

    df = merged.copy()

    # Validate alpha parameter
    if not (0 < alpha < 1):
        logger.warning(f"Invalid alpha value: {alpha}. Using default: {Config.DEFAULT_ALPHA}")
        alpha = Config.DEFAULT_ALPHA

    # Calculate Total Factor Productivity (TFP)
    logger.info("Calculating Total Factor Productivity (TFP)")
    try:
        df = calculate_tfp(df, alpha=alpha)
        if "TFP" in df.columns:
            non_na_count = df["TFP"].notna().sum()
            logger.info(f"TFP calculated for {non_na_count} years")
        else:
            logger.warning("TFP calculation failed - TFP column not found")
    except Exception as e:
        logger.error(f"Error calculating TFP: {e}")
        # Ensure TFP column exists even if calculation fails
        if "TFP" not in df.columns:
            df["TFP"] = np.nan

    # Tax revenue in USD billions
    if all(c in df.columns for c in ["TAX_pct_GDP", "GDP_USD_bn"]):
        logger.info("Calculating tax revenue in USD billions (T_USD_bn)")
        df["T_USD_bn"] = (df["TAX_pct_GDP"] / 100) * df["GDP_USD_bn"]
        df["T_USD_bn"] = df["T_USD_bn"].round(Config.DECIMAL_PLACES_CURRENCY)
        non_na_count = df["T_USD_bn"].notna().sum()
        logger.info(f"Calculated T_USD_bn for {non_na_count} years")
    else:
        missing = [c for c in ["TAX_pct_GDP", "GDP_USD_bn"] if c not in df.columns]
        logger.warning(f"Cannot calculate T_USD_bn - missing columns: {missing}")
        df["T_USD_bn"] = np.nan

    # Trade openness ratio (trade as % of GDP)
    if all(c in df.columns for c in ["X_USD_bn", "M_USD_bn", "GDP_USD_bn"]):
        logger.info("Calculating trade openness ratio")
        # This is the ratio of total trade (exports + imports) to GDP
        df["Openness_Ratio"] = (df["X_USD_bn"] + df["M_USD_bn"]) / df["GDP_USD_bn"]
        df["Openness_Ratio"] = df["Openness_Ratio"].round(Config.DECIMAL_PLACES_RATIOS)
        non_na_count = df["Openness_Ratio"].notna().sum()
        logger.info(f"Calculated Openness_Ratio for {non_na_count} years")
    else:
        missing = [c for c in ["X_USD_bn", "M_USD_bn", "GDP_USD_bn"] if c not in df.columns]
        logger.warning(f"Cannot calculate Openness_Ratio - missing columns: {missing}")
        df["Openness_Ratio"] = np.nan

    # Net exports
    if all(c in df.columns for c in ["X_USD_bn", "M_USD_bn"]):
        logger.info("Calculating net exports (NX_USD_bn)")
        df["NX_USD_bn"] = df["X_USD_bn"] - df["M_USD_bn"]
        df["NX_USD_bn"] = df["NX_USD_bn"].round(Config.DECIMAL_PLACES_CURRENCY)
        non_na_count = df["NX_USD_bn"].notna().sum()
        logger.info(f"Calculated NX_USD_bn for {non_na_count} years")
    else:
        missing = [c for c in ["X_USD_bn", "M_USD_bn"] if c not in df.columns]
        logger.warning(f"Cannot calculate NX_USD_bn - missing columns: {missing}")
        df["NX_USD_bn"] = np.nan

    # Saving calculations
    # Total saving (National Saving = Y - C - G)
    if all(c in df.columns for c in ["GDP_USD_bn", "C_USD_bn", "G_USD_bn"]):
        logger.info("Calculating total national saving (S_USD_bn = Y - C - G)")
        df["S_USD_bn"] = df["GDP_USD_bn"] - df["C_USD_bn"] - df["G_USD_bn"]
        df["S_USD_bn"] = df["S_USD_bn"].round(Config.DECIMAL_PLACES_CURRENCY)
        non_na_count = df["S_USD_bn"].notna().sum()
        logger.info(f"Calculated S_USD_bn for {non_na_count} years")
    else:
        missing = [c for c in ["GDP_USD_bn", "C_USD_bn", "G_USD_bn"] if c not in df.columns]
        logger.warning(f"Cannot calculate S_USD_bn - missing columns: {missing}")
        df["S_USD_bn"] = np.nan

    # Public saving (government saving = tax revenue - government spending)
    if all(c in df.columns for c in ["T_USD_bn", "G_USD_bn"]):
        logger.info("Calculating public saving (S_pub_USD_bn)")
        df["S_pub_USD_bn"] = df["T_USD_bn"] - df["G_USD_bn"]
        df["S_pub_USD_bn"] = df["S_pub_USD_bn"].round(Config.DECIMAL_PLACES_CURRENCY)
        non_na_count = df["S_pub_USD_bn"].notna().sum()
        logger.info(f"Calculated S_pub_USD_bn for {non_na_count} years")
    else:
        missing = [c for c in ["T_USD_bn", "G_USD_bn"] if c not in df.columns]
        logger.warning(f"Cannot calculate S_pub_USD_bn - missing columns: {missing}")
        df["S_pub_USD_bn"] = np.nan

    # Private saving (total saving - public saving)
    if all(c in df.columns for c in ["S_USD_bn", "S_pub_USD_bn"]):
        logger.info("Calculating private saving (S_priv_USD_bn)")
        df["S_priv_USD_bn"] = df["S_USD_bn"] - df["S_pub_USD_bn"]
        df["S_priv_USD_bn"] = df["S_priv_USD_bn"].round(Config.DECIMAL_PLACES_CURRENCY)
        non_na_count = df["S_priv_USD_bn"].notna().sum()
        logger.info(f"Calculated S_priv_USD_bn for {non_na_count} years")
    else:
        missing = [c for c in ["S_USD_bn", "S_pub_USD_bn"] if c not in df.columns]
        logger.warning(f"Cannot calculate S_priv_USD_bn - missing columns: {missing}")
        df["S_priv_USD_bn"] = np.nan

    # Saving rate (total saving as % of GDP)
    if all(c in df.columns for c in ["S_USD_bn", "GDP_USD_bn"]):
        logger.info("Calculating saving rate")
        df["Saving_Rate"] = df["S_USD_bn"] / df["GDP_USD_bn"]
        df["Saving_Rate"] = df["Saving_Rate"].round(Config.DECIMAL_PLACES_RATIOS)
        non_na_count = df["Saving_Rate"].notna().sum()
        logger.info(f"Calculated Saving_Rate for {non_na_count} years")
    else:
        missing = [c for c in ["S_USD_bn", "GDP_USD_bn"] if c not in df.columns]
        logger.warning(f"Cannot calculate Saving_Rate - missing columns: {missing}")
        df["Saving_Rate"] = np.nan

    logger.info("Economic indicators calculation completed")
    return df
