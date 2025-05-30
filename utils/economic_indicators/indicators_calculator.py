"""Economic indicators calculation module.

This module provides functions for calculating various economic indicators
including tax revenue, openness ratios, and saving measures.
"""

import logging

import numpy as np
import pandas as pd

from config import Config

from .tfp_calculator import calculate_tfp

try:
    from utils.logging_config import get_logger

    logger = get_logger(__name__)
except ImportError:
    # Fallback to standard logging if structured logging is not available
    logger = logging.getLogger(__name__)


def _calculate_tfp_indicator(
    result_df: pd.DataFrame, alpha: float, log_instance: logging.Logger
) -> pd.DataFrame:
    """Calculate Total Factor Productivity indicator."""
    log_instance.info("Calculating Total Factor Productivity (TFP)")
    try:
        result_df = calculate_tfp(result_df, alpha)
        if "TFP" in result_df.columns:
            non_na_count = result_df["TFP"].notna().sum()
            log_instance.info("Calculated TFP for %s years", non_na_count)
        else:
            log_instance.warning("TFP calculation failed - TFP column not found")
    except Exception:  # pylint: disable=broad-exception-caught
        log_instance.exception("Error calculating TFP")
        if "TFP" not in result_df.columns:
            result_df["TFP"] = np.nan
    return result_df


def _calculate_tax_revenue(result_df: pd.DataFrame, log_instance: logging.Logger) -> pd.DataFrame:
    """Calculate tax revenue in USD billions."""
    required_cols = ["TAX_pct_GDP", "GDP_USD_bn"]
    if all(c in result_df.columns for c in required_cols):
        log_instance.info("Calculating tax revenue in USD billions (T_USD_bn)")
        result_df["T_USD_bn"] = (result_df["TAX_pct_GDP"] / 100) * result_df["GDP_USD_bn"]
        result_df["T_USD_bn"] = result_df["T_USD_bn"].round(Config.DECIMAL_PLACES_CURRENCY)
        non_na_count = result_df["T_USD_bn"].notna().sum()
        log_instance.info("Calculated T_USD_bn for %s years", non_na_count)
    else:
        missing = [c for c in required_cols if c not in result_df.columns]
        log_instance.warning("Cannot calculate T_USD_bn - missing columns: %s", missing)
        result_df["T_USD_bn"] = np.nan
    return result_df


def _calculate_trade_indicators(
    result_df: pd.DataFrame, log_instance: logging.Logger
) -> pd.DataFrame:
    """Calculate trade-related indicators (openness ratio and net exports)."""
    # Trade openness ratio
    openness_cols = ["X_USD_bn", "M_USD_bn", "GDP_USD_bn"]
    if all(c in result_df.columns for c in openness_cols):
        log_instance.info("Calculating trade openness ratio")
        result_df["Openness_Ratio"] = (result_df["X_USD_bn"] + result_df["M_USD_bn"]) / result_df[
            "GDP_USD_bn"
        ]
        result_df["Openness_Ratio"] = result_df["Openness_Ratio"].round(
            Config.DECIMAL_PLACES_RATIOS
        )
        non_na_count = result_df["Openness_Ratio"].notna().sum()
        log_instance.info("Calculated Openness_Ratio for %s years", non_na_count)
    else:
        missing = [c for c in openness_cols if c not in result_df.columns]
        log_instance.warning("Cannot calculate Openness_Ratio - missing columns: %s", missing)
        result_df["Openness_Ratio"] = np.nan

    # Net exports
    nx_cols = ["X_USD_bn", "M_USD_bn"]
    if all(c in result_df.columns for c in nx_cols):
        log_instance.info("Calculating net exports (NX_USD_bn)")
        result_df["NX_USD_bn"] = result_df["X_USD_bn"] - result_df["M_USD_bn"]
        result_df["NX_USD_bn"] = result_df["NX_USD_bn"].round(Config.DECIMAL_PLACES_CURRENCY)
        non_na_count = result_df["NX_USD_bn"].notna().sum()
        log_instance.info("Calculated NX_USD_bn for %s years", non_na_count)
    else:
        missing = [c for c in nx_cols if c not in result_df.columns]
        log_instance.warning("Cannot calculate NX_USD_bn - missing columns: %s", missing)
        result_df["NX_USD_bn"] = np.nan

    return result_df


def _calculate_saving_indicators(
    result_df: pd.DataFrame, log_instance: logging.Logger
) -> pd.DataFrame:
    """Calculate saving-related indicators."""
    # Total saving (National Saving = Y - C - G)
    total_saving_cols = ["GDP_USD_bn", "C_USD_bn", "G_USD_bn"]
    if all(c in result_df.columns for c in total_saving_cols):
        log_instance.info("Calculating total national saving (S_USD_bn = Y - C - G)")
        result_df["S_USD_bn"] = (
            result_df["GDP_USD_bn"] - result_df["C_USD_bn"] - result_df["G_USD_bn"]
        )
        result_df["S_USD_bn"] = result_df["S_USD_bn"].round(Config.DECIMAL_PLACES_CURRENCY)
        non_na_count = result_df["S_USD_bn"].notna().sum()
        log_instance.info("Calculated S_USD_bn for %s years", non_na_count)
    else:
        missing = [c for c in total_saving_cols if c not in result_df.columns]
        log_instance.warning("Cannot calculate S_USD_bn - missing columns: %s", missing)
        result_df["S_USD_bn"] = np.nan

    # Public saving (government saving = tax revenue - government spending)
    public_saving_cols = ["T_USD_bn", "G_USD_bn"]
    if all(c in result_df.columns for c in public_saving_cols):
        log_instance.info("Calculating public saving (S_pub_USD_bn)")
        result_df["S_pub_USD_bn"] = result_df["T_USD_bn"] - result_df["G_USD_bn"]
        result_df["S_pub_USD_bn"] = result_df["S_pub_USD_bn"].round(Config.DECIMAL_PLACES_CURRENCY)
        non_na_count = result_df["S_pub_USD_bn"].notna().sum()
        log_instance.info("Calculated S_pub_USD_bn for %s years", non_na_count)
    else:
        missing = [c for c in public_saving_cols if c not in result_df.columns]
        log_instance.warning("Cannot calculate S_pub_USD_bn - missing columns: %s", missing)
        result_df["S_pub_USD_bn"] = np.nan

    # Private saving (total saving - public saving)
    private_saving_cols = ["S_USD_bn", "S_pub_USD_bn"]
    if all(c in result_df.columns for c in private_saving_cols):
        log_instance.info("Calculating private saving (S_priv_USD_bn)")
        result_df["S_priv_USD_bn"] = result_df["S_USD_bn"] - result_df["S_pub_USD_bn"]
        result_df["S_priv_USD_bn"] = result_df["S_priv_USD_bn"].round(
            Config.DECIMAL_PLACES_CURRENCY
        )
        non_na_count = result_df["S_priv_USD_bn"].notna().sum()
        log_instance.info("Calculated S_priv_USD_bn for %s years", non_na_count)
    else:
        missing = [c for c in private_saving_cols if c not in result_df.columns]
        log_instance.warning("Cannot calculate S_priv_USD_bn - missing columns: %s", missing)
        result_df["S_priv_USD_bn"] = np.nan

    # Saving rate (total saving as % of GDP)
    saving_rate_cols = ["S_USD_bn", "GDP_USD_bn"]
    if all(c in result_df.columns for c in saving_rate_cols):
        log_instance.info("Calculating saving rate")
        result_df["Saving_Rate"] = result_df["S_USD_bn"] / result_df["GDP_USD_bn"]
        result_df["Saving_Rate"] = result_df["Saving_Rate"].round(Config.DECIMAL_PLACES_RATIOS)
        non_na_count = result_df["Saving_Rate"].notna().sum()
        log_instance.info("Calculated Saving_Rate for %s years", non_na_count)
    else:
        missing = [c for c in saving_rate_cols if c not in result_df.columns]
        log_instance.warning("Cannot calculate Saving_Rate - missing columns: %s", missing)
        result_df["Saving_Rate"] = np.nan

    return result_df


def calculate_economic_indicators(
    merged: pd.DataFrame,
    alpha: float = Config.DEFAULT_ALPHA,
    log_instance: logging.Logger | None = None,
) -> pd.DataFrame:
    """Calculate comprehensive economic indicators from merged economic data.

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
        alpha: Capital share parameter for TFP calculation (0 < alpha < 1).
               Default value from Config.DEFAULT_ALPHA
        log_instance: Optional logger instance for detailed logging. If None, uses
               module log_instance.

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
    if log_instance is None:
        log_instance = logger

    result_df = merged.copy()

    # Validate alpha parameter
    if not 0 < alpha < 1:
        log_instance.warning(
            "Invalid alpha value: %s. Using default: %s",
            alpha,
            Config.DEFAULT_ALPHA,
        )
        alpha = Config.DEFAULT_ALPHA

    # Calculate indicators using helper functions
    result_df = _calculate_tfp_indicator(result_df, alpha, log_instance)
    result_df = _calculate_tax_revenue(result_df, log_instance)
    result_df = _calculate_trade_indicators(result_df, log_instance)
    result_df = _calculate_saving_indicators(result_df, log_instance)

    log_instance.info("Economic indicators calculation completed")
    return result_df
