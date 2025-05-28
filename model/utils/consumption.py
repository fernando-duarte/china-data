"""Consumption calculation module for the China Growth Model.

This module implements the consumption equation:
C_t = (1 - s_t) * Y_t - G_t

Where:
- C_t: Consumption in period t
- s_t: Saving rate in period t (player controlled)
- Y_t: GDP in period t
- G_t: Government spending in period t
"""

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def _validate_and_clip_series_inputs(
    gdp: pd.Series, saving_rate: pd.Series, government_spending: pd.Series
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Validate and clip series inputs for consumption calculation."""
    if (gdp < 0).any():
        logger.warning("Some GDP values are negative")
        gdp = gdp.clip(lower=0)

    if (saving_rate < 0).any() or (saving_rate > 1).any():
        logger.warning("Some saving rate values are outside [0,1] range")
        saving_rate = saving_rate.clip(lower=0, upper=1)

    if (government_spending < 0).any():
        logger.warning("Some government spending values are negative")
        government_spending = government_spending.clip(lower=0)

    return gdp, saving_rate, government_spending


def _validate_and_clip_scalar_inputs(
    gdp: float, saving_rate: float, government_spending: float
) -> tuple[float, float, float]:
    """Validate and clip scalar inputs for consumption calculation."""
    if gdp < 0:
        logger.warning("GDP %s is negative, clipping to 0", gdp)
        gdp = max(gdp, 0)

    if saving_rate < 0 or saving_rate > 1:
        logger.warning("Saving rate %s is outside [0,1] range, clipping", saving_rate)
        saving_rate = max(0, min(saving_rate, 1))

    if government_spending < 0:
        logger.warning("Government spending %s is negative, clipping to 0", government_spending)
        government_spending = max(government_spending, 0)

    return gdp, saving_rate, government_spending


def _convert_to_series(
    gdp: float | pd.Series,
    saving_rate: float | pd.Series,
    government_spending: float | pd.Series,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Convert inputs to pandas Series for consistent handling."""
    max_len = max(
        len(gdp) if isinstance(gdp, pd.Series) else 1,
        len(saving_rate) if isinstance(saving_rate, pd.Series) else 1,
        len(government_spending) if isinstance(government_spending, pd.Series) else 1,
    )

    if not isinstance(gdp, pd.Series):
        gdp = pd.Series([gdp] * max_len)
    if not isinstance(saving_rate, pd.Series):
        saving_rate = pd.Series([saving_rate] * max_len)
    if not isinstance(government_spending, pd.Series):
        government_spending = pd.Series([government_spending] * max_len)

    return gdp, saving_rate, government_spending


def calculate_consumption(
    gdp: float | pd.Series,
    saving_rate: float | pd.Series,
    government_spending: float | pd.Series,
) -> float | pd.Series:
    """Calculate consumption using the China growth model consumption equation.

    Args:
        gdp: GDP in period t (billions USD)
        saving_rate: Saving rate in period t (fraction, 0-1)
        government_spending: Government spending in period t (billions USD)

    Returns:
        Calculated consumption (billions USD)

    Raises:
        ValueError: If any parameters are invalid

    Example:
        >>> consumption = calculate_consumption(gdp=1000.0, saving_rate=0.3, government_spending=200.0)
        >>> # Result: (1 - 0.3) * 1000 - 200 = 500
    """
    # Handle both scalar and series inputs
    is_series_input = (
        isinstance(gdp, pd.Series) or isinstance(saving_rate, pd.Series) or isinstance(government_spending, pd.Series)
    )

    if is_series_input:
        gdp, saving_rate, government_spending = _convert_to_series(gdp, saving_rate, government_spending)
        gdp, saving_rate, government_spending = _validate_and_clip_series_inputs(gdp, saving_rate, government_spending)
    else:
        gdp, saving_rate, government_spending = _validate_and_clip_scalar_inputs(gdp, saving_rate, government_spending)

    try:
        consumption = (1 - saving_rate) * gdp - government_spending

        # Check for negative consumption
        if isinstance(consumption, pd.Series):
            if (consumption < 0).any():
                logger.warning("Some calculated consumption values are negative")
                consumption = consumption.clip(lower=0)
        elif consumption < 0:
            logger.warning("Calculated consumption %s is negative, clipping to 0", consumption)
            consumption = max(consumption, 0)

        logger.debug(
            "Calculated consumption with saving_rate=%s, gdp=%s, gov_spending=%s", saving_rate, gdp, government_spending
        )
    except (ValueError, OverflowError):
        logger.exception("Error calculating consumption")
        if isinstance(gdp, pd.Series):
            return pd.Series([np.nan] * len(gdp))
        return np.nan
    else:
        return consumption


def calculate_consumption_dataframe(
    df: pd.DataFrame,
    *,
    gdp_col: str = "GDP_USD_bn",
    saving_rate_col: str = "saving_rate",
    government_spending_col: str = "G_USD_bn",
    output_col: str = "C_USD_bn",
) -> pd.DataFrame:
    """Calculate consumption for a DataFrame with time series data.

    Args:
        df: DataFrame containing GDP, saving rate, and government spending data
        gdp_col: Column name for GDP data
        saving_rate_col: Column name for saving rate data
        government_spending_col: Column name for government spending data
        output_col: Column name for calculated consumption (default: "C_USD_bn")

    Returns:
        DataFrame with consumption column added

    Raises:
        ValueError: If required columns are missing
    """
    # Validate required columns
    required_cols = [gdp_col, saving_rate_col, government_spending_col]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        missing_cols_str = ", ".join(missing_cols)
        msg = f"Missing required columns: {missing_cols_str}"
        raise ValueError(msg)

    result_df = df.copy()

    # Calculate consumption
    result_df[output_col] = calculate_consumption(
        gdp=df[gdp_col],
        saving_rate=df[saving_rate_col],
        government_spending=df[government_spending_col],
    )

    logger.info("Calculated consumption for %d periods", len(result_df))

    return result_df


def validate_consumption_feasibility(
    gdp: float | pd.Series,
    saving_rate: float | pd.Series,
    government_spending: float | pd.Series,
) -> bool | pd.Series:
    """Validate that consumption calculation will yield non-negative results.

    Args:
        gdp: GDP in period t (billions USD)
        saving_rate: Saving rate in period t (fraction, 0-1)
        government_spending: Government spending in period t (billions USD)

    Returns:
        Boolean or Series indicating whether consumption would be non-negative
    """
    consumption = (1 - saving_rate) * gdp - government_spending

    if isinstance(consumption, pd.Series):
        return consumption >= 0
    return consumption >= 0
