"""Consumption calculation module for the China Growth Model.

This module calculates consumption as a residual of GDP accounting:
C_t = Y_t - I_t - G_t - NX_t

Where:
- C_t: Consumption in period t
- Y_t: GDP in period t
- I_t: Investment in period t
- G_t: Government spending in period t
- NX_t: Net exports in period t
"""

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def _validate_and_clip_scalar_inputs(gdp: float, investment: float, gov_spending: float) -> tuple[float, float, float]:
    """Validate and clip scalar inputs."""
    if gdp < 0:
        logger.warning("GDP %s is negative, clipping to 0", gdp)
        gdp = max(gdp, 0)

    if investment < 0:
        logger.warning("Investment %s is negative, clipping to 0", investment)
        investment = max(investment, 0)

    if gov_spending < 0:
        logger.warning("Government spending %s is negative, clipping to 0", gov_spending)
        gov_spending = max(gov_spending, 0)

    return gdp, investment, gov_spending


def _validate_and_clip_series_inputs(
    gdp: pd.Series[float], investment: pd.Series[float], gov_spending: pd.Series[float]
) -> tuple[pd.Series[float], pd.Series[float], pd.Series[float]]:
    """Validate and clip series inputs."""
    if (gdp < 0).any():
        logger.warning("Some GDP values are negative")
        gdp = gdp.clip(lower=0)

    if (investment < 0).any():
        logger.warning("Some investment values are negative")
        investment = investment.clip(lower=0)

    if (gov_spending < 0).any():
        logger.warning("Some government spending values are negative")
        gov_spending = gov_spending.clip(lower=0)

    return gdp, investment, gov_spending


def _convert_to_series(
    gdp: float | pd.Series[float],
    investment: float | pd.Series[float],
    gov_spending: float | pd.Series[float],
    net_exports: float | pd.Series[float],
) -> tuple[pd.Series[float], pd.Series[float], pd.Series[float], pd.Series[float]]:
    """Convert inputs to pandas Series for consistent handling."""
    max_len = max(
        len(gdp) if isinstance(gdp, pd.Series) else 1,
        len(investment) if isinstance(investment, pd.Series) else 1,
        len(gov_spending) if isinstance(gov_spending, pd.Series) else 1,
        len(net_exports) if isinstance(net_exports, pd.Series) else 1,
    )

    if not isinstance(gdp, pd.Series):
        gdp = pd.Series([gdp] * max_len, dtype=float)
    if not isinstance(investment, pd.Series):
        investment = pd.Series([investment] * max_len, dtype=float)
    if not isinstance(gov_spending, pd.Series):
        gov_spending = pd.Series([gov_spending] * max_len, dtype=float)
    if not isinstance(net_exports, pd.Series):
        net_exports = pd.Series([net_exports] * max_len, dtype=float)

    return gdp, investment, gov_spending, net_exports


def calculate_consumption(
    gdp: float | pd.Series[float],
    investment: float | pd.Series[float],
    gov_spending: float | pd.Series[float],
    net_exports: float | pd.Series[float],
) -> float | pd.Series[float]:
    """Calculate consumption using the GDP accounting identity.

    Args:
        gdp: GDP in period t (billions USD)
        investment: Investment in period t (billions USD)
        gov_spending: Government spending in period t (billions USD)
        net_exports: Net exports in period t (billions USD)

    Returns:
        Calculated consumption (billions USD)

    Raises:
        ValueError: If any parameters are invalid

    Example:
        >>> consumption = calculate_consumption(gdp=1000.0, investment=300.0, gov_spending=200.0, net_exports=50.0)
        >>> # Result: 1000 - 300 - 200 - 50 = 450
    """
    # Handle both scalar and series inputs
    is_series = (
        isinstance(gdp, pd.Series)
        or isinstance(investment, pd.Series)
        or isinstance(gov_spending, pd.Series)
        or isinstance(net_exports, pd.Series)
    )

    if is_series:
        gdp, investment, gov_spending, net_exports = _convert_to_series(gdp, investment, gov_spending, net_exports)
        gdp, investment, gov_spending = _validate_and_clip_series_inputs(gdp, investment, gov_spending)
    else:
        # Type assertions for MyPy
        assert isinstance(gdp, float)
        assert isinstance(investment, float)
        assert isinstance(gov_spending, float)
        gdp, investment, gov_spending = _validate_and_clip_scalar_inputs(gdp, investment, gov_spending)

    try:
        # Calculate consumption using the formula: C_t = Y_t - I_t - G_t - NX_t
        consumption = gdp - investment - gov_spending - net_exports

        # Check for negative consumption
        if isinstance(consumption, pd.Series):
            if (consumption < 0).any():
                logger.warning("Some calculated consumption values are negative")
        elif consumption < 0:
            logger.warning("Calculated consumption %s is negative", consumption)

        logger.debug(
            "Calculated consumption with gdp=%s, investment=%s, gov_spending=%s, net_exports=%s",
            gdp,
            investment,
            gov_spending,
            net_exports,
        )
    except (ValueError, OverflowError):
        logger.exception("Error calculating consumption")
        if isinstance(gdp, pd.Series):
            return pd.Series([np.nan] * len(gdp), dtype=float)
        return np.nan
    else:
        return consumption


def calculate_consumption_dataframe(
    df: pd.DataFrame,
    *,
    gdp_col: str = "GDP_USD_bn",
    investment_col: str = "I_USD_bn",
    gov_spending_col: str = "G_USD_bn",
    net_exports_col: str = "NX_USD_bn",
    output_col: str = "C_USD_bn",
) -> pd.DataFrame:
    """Calculate consumption for a DataFrame with time series data.

    Args:
        df: DataFrame containing GDP, investment, government spending, and net exports data
        gdp_col: Column name for GDP data
        investment_col: Column name for investment data
        gov_spending_col: Column name for government spending data
        net_exports_col: Column name for net exports data
        output_col: Column name for calculated consumption (default: "C_USD_bn")

    Returns:
        DataFrame with consumption column added

    Raises:
        ValueError: If required columns are missing
    """
    # Validate required columns
    required_cols = [gdp_col, investment_col, gov_spending_col, net_exports_col]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        msg = f"Missing required columns: {missing_cols}"
        raise ValueError(msg)

    result_df = df.copy()

    # Calculate consumption
    result_df[output_col] = calculate_consumption(
        gdp=df[gdp_col],
        investment=df[investment_col],
        gov_spending=df[gov_spending_col],
        net_exports=df[net_exports_col],
    )

    logger.info("Calculated consumption for %d periods", len(result_df))

    return result_df


def calculate_consumption_share(
    consumption: float | pd.Series[float],
    gdp: float | pd.Series[float],
) -> float | pd.Series[float]:
    """Calculate consumption as a share of GDP.

    Args:
        consumption: Consumption value(s)
        gdp: GDP value(s)

    Returns:
        Consumption share (C/Y)

    Raises:
        ValueError: If GDP is zero or negative
    """
    # Validate GDP
    gdp_positive_msg = "GDP must be positive for share calculation"
    if isinstance(gdp, pd.Series):
        if (gdp <= 0).any():
            raise ValueError(gdp_positive_msg)
    elif gdp <= 0:
        raise ValueError(gdp_positive_msg)

    return consumption / gdp
