"""Investment from saving calculation module for the China Growth Model.

This module implements the investment equation from the saving identity:
I_t = s_t * Y_t - NX_t

Where:
- I_t: Investment in period t
- s_t: Saving rate in period t (player controlled)
- Y_t: GDP in period t
- NX_t: Net exports in period t (X_t - M_t)
"""

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def calculate_investment_from_saving(
    gdp: float | pd.Series,
    saving_rate: float | pd.Series,
    net_exports: float | pd.Series,
) -> float | pd.Series:
    """Calculate investment using the saving identity equation.
    
    Args:
        gdp: GDP in period t (billions USD)
        saving_rate: Saving rate in period t (fraction, 0-1)
        net_exports: Net exports in period t (billions USD)
        
    Returns:
        Calculated investment (billions USD)
        
    Raises:
        ValueError: If any parameters are invalid
        
    Example:
        >>> investment = calculate_investment_from_saving(
        ...     gdp=1000.0,
        ...     saving_rate=0.3,
        ...     net_exports=50.0
        ... )
        >>> # Result: 0.3 * 1000 - 50 = 250
    """
    # Handle both scalar and series inputs
    if isinstance(gdp, pd.Series) or isinstance(saving_rate, pd.Series) or isinstance(net_exports, pd.Series):
        # Convert to pandas Series for consistent handling
        max_len = max(
            len(gdp) if isinstance(gdp, pd.Series) else 1,
            len(saving_rate) if isinstance(saving_rate, pd.Series) else 1,
            len(net_exports) if isinstance(net_exports, pd.Series) else 1,
        )

        if not isinstance(gdp, pd.Series):
            gdp = pd.Series([gdp] * max_len)
        if not isinstance(saving_rate, pd.Series):
            saving_rate = pd.Series([saving_rate] * max_len)
        if not isinstance(net_exports, pd.Series):
            net_exports = pd.Series([net_exports] * max_len)

        # Validate inputs
        if (gdp < 0).any():
            logger.warning("Some GDP values are negative")
            gdp = gdp.clip(lower=0)

        if (saving_rate < 0).any() or (saving_rate > 1).any():
            logger.warning("Some saving rate values are outside [0,1] range")
            saving_rate = saving_rate.clip(lower=0, upper=1)
    else:
        # Scalar inputs
        if gdp < 0:
            logger.warning(f"GDP {gdp} is negative, clipping to 0")
            gdp = max(gdp, 0)

        if saving_rate < 0 or saving_rate > 1:
            logger.warning(f"Saving rate {saving_rate} is outside [0,1] range, clipping")
            saving_rate = max(0, min(saving_rate, 1))

    try:
        # Calculate investment using the formula:
        # I_t = s_t * Y_t - NX_t
        investment = saving_rate * gdp - net_exports

        # Check for negative investment
        if isinstance(investment, pd.Series):
            if (investment < 0).any():
                logger.warning("Some calculated investment values are negative")
                # Note: We don't automatically clip negative investment as it can be economically meaningful
        elif investment < 0:
            logger.warning(f"Calculated investment {investment} is negative")

        logger.debug(f"Calculated investment with saving_rate={saving_rate}, gdp={gdp}, net_exports={net_exports}")

        return investment

    except (ValueError, OverflowError) as e:
        logger.error(f"Error calculating investment: {e}")
        if isinstance(gdp, pd.Series):
            return pd.Series([np.nan] * len(gdp))
        return np.nan


def calculate_investment_from_saving_dataframe(
    df: pd.DataFrame,
    *,
    gdp_col: str = "GDP_USD_bn",
    saving_rate_col: str = "saving_rate",
    net_exports_col: str = "NX_USD_bn",
    output_col: str = "I_USD_bn",
) -> pd.DataFrame:
    """Calculate investment for a DataFrame with time series data.
    
    Args:
        df: DataFrame containing GDP, saving rate, and net exports data
        gdp_col: Column name for GDP data
        saving_rate_col: Column name for saving rate data
        net_exports_col: Column name for net exports data
        output_col: Column name for calculated investment (default: "I_USD_bn")
        
    Returns:
        DataFrame with investment column added
        
    Raises:
        ValueError: If required columns are missing
    """
    # Validate required columns
    required_cols = [gdp_col, saving_rate_col, net_exports_col]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    result_df = df.copy()

    # Calculate investment
    result_df[output_col] = calculate_investment_from_saving(
        gdp=df[gdp_col],
        saving_rate=df[saving_rate_col],
        net_exports=df[net_exports_col],
    )

    logger.info(f"Calculated investment for {len(result_df)} periods")

    return result_df


def calculate_required_saving_rate(
    gdp: float | pd.Series,
    target_investment: float | pd.Series,
    net_exports: float | pd.Series,
) -> float | pd.Series:
    """Calculate the saving rate required to achieve a target investment level.
    
    Rearranges the investment equation to solve for saving rate:
    s_t = (I_t + NX_t) / Y_t
    
    Args:
        gdp: GDP in period t (billions USD)
        target_investment: Target investment level (billions USD)
        net_exports: Net exports in period t (billions USD)
        
    Returns:
        Required saving rate (fraction, 0-1)
        
    Raises:
        ValueError: If GDP is zero or negative
    """
    # Validate inputs
    if isinstance(gdp, pd.Series):
        if (gdp <= 0).any():
            raise ValueError("GDP must be positive for saving rate calculation")
    elif gdp <= 0:
        raise ValueError("GDP must be positive for saving rate calculation")

    try:
        # Calculate required saving rate: s_t = (I_t + NX_t) / Y_t
        required_saving_rate = (target_investment + net_exports) / gdp

        # Clip to valid range [0, 1]
        if isinstance(required_saving_rate, pd.Series):
            required_saving_rate = required_saving_rate.clip(lower=0, upper=1)
            if (required_saving_rate == 1).any():
                logger.warning("Some required saving rates are at maximum (100%)")
        else:
            required_saving_rate = max(0, min(required_saving_rate, 1))
            if required_saving_rate == 1:
                logger.warning("Required saving rate is at maximum (100%)")

        return required_saving_rate

    except (ValueError, OverflowError, ZeroDivisionError) as e:
        logger.error(f"Error calculating required saving rate: {e}")
        if isinstance(gdp, pd.Series):
            return pd.Series([np.nan] * len(gdp))
        return np.nan


def validate_investment_feasibility(
    gdp: float | pd.Series,
    saving_rate: float | pd.Series,
    net_exports: float | pd.Series,
    min_investment: float | pd.Series = 0,
) -> bool | pd.Series:
    """Validate that investment calculation will yield feasible results.
    
    Args:
        gdp: GDP in period t (billions USD)
        saving_rate: Saving rate in period t (fraction, 0-1)
        net_exports: Net exports in period t (billions USD)
        min_investment: Minimum acceptable investment level (default: 0)
        
    Returns:
        Boolean or Series indicating whether investment would be feasible
    """
    investment = saving_rate * gdp - net_exports

    if isinstance(investment, pd.Series):
        return investment >= min_investment
    return investment >= min_investment
