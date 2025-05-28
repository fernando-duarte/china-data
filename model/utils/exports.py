"""Export calculation module for the China Growth Model.

This module implements the export equation:
X_t = X_0 * (e_t/e_0)^ε_x * (Y*_t/Y*_0)^μ_x

Where:
- X_t: Exports in period t
- X_0: Initial exports (base period)
- e_t: Exchange rate in period t (CNY per USD)
- e_0: Initial exchange rate (base period)
- ε_x: Export exchange rate elasticity
- Y*_t: Foreign income in period t
- Y*_0: Initial foreign income (base period)
- μ_x: Export income elasticity
"""

import logging
from typing import Union

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def calculate_exports(
    exchange_rate: Union[float, pd.Series],
    foreign_income: Union[float, pd.Series],
    *,
    x_0: float,
    e_0: float,
    y_star_0: float,
    epsilon_x: float = 1.5,
    mu_x: float = 1.5,
) -> Union[float, pd.Series]:
    """Calculate exports using the China growth model export equation.
    
    Args:
        exchange_rate: Current exchange rate(s) (CNY per USD)
        foreign_income: Current foreign income index(es)
        x_0: Initial exports in base period (billions USD)
        e_0: Initial exchange rate in base period (CNY per USD)
        y_star_0: Initial foreign income in base period (index)
        epsilon_x: Export exchange rate elasticity (default: 1.5)
        mu_x: Export income elasticity (default: 1.5)
        
    Returns:
        Calculated exports (billions USD)
        
    Raises:
        ValueError: If any parameters are invalid
        
    Example:
        >>> exports = calculate_exports(
        ...     exchange_rate=8.0,
        ...     foreign_income=1200.0,
        ...     x_0=19.41,
        ...     e_0=1.5,
        ...     y_star_0=1000.0,
        ...     epsilon_x=1.5,
        ...     mu_x=1.5
        ... )
    """
    # Validate inputs
    if x_0 <= 0:
        raise ValueError(f"Initial exports x_0 must be positive, got {x_0}")
    if e_0 <= 0:
        raise ValueError(f"Initial exchange rate e_0 must be positive, got {e_0}")
    if y_star_0 <= 0:
        raise ValueError(f"Initial foreign income y_star_0 must be positive, got {y_star_0}")
    
    # Handle both scalar and series inputs
    if isinstance(exchange_rate, pd.Series) or isinstance(foreign_income, pd.Series):
        # Convert to pandas Series for consistent handling
        if not isinstance(exchange_rate, pd.Series):
            exchange_rate = pd.Series([exchange_rate] * len(foreign_income))
        if not isinstance(foreign_income, pd.Series):
            foreign_income = pd.Series([foreign_income] * len(exchange_rate))
            
        # Check for invalid values
        if (exchange_rate <= 0).any():
            logger.warning("Some exchange rate values are non-positive")
            exchange_rate = exchange_rate.clip(lower=1e-6)
            
        if (foreign_income <= 0).any():
            logger.warning("Some foreign income values are non-positive")
            foreign_income = foreign_income.clip(lower=1e-6)
    else:
        # Scalar inputs
        if exchange_rate <= 0:
            logger.warning(f"Exchange rate {exchange_rate} is non-positive, clipping to 1e-6")
            exchange_rate = max(exchange_rate, 1e-6)
            
        if foreign_income <= 0:
            logger.warning(f"Foreign income {foreign_income} is non-positive, clipping to 1e-6")
            foreign_income = max(foreign_income, 1e-6)
    
    try:
        # Calculate exports using the formula:
        # X_t = X_0 * (e_t/e_0)^ε_x * (Y*_t/Y*_0)^μ_x
        exchange_rate_ratio = exchange_rate / e_0
        foreign_income_ratio = foreign_income / y_star_0
        
        exports = x_0 * np.power(exchange_rate_ratio, epsilon_x) * np.power(foreign_income_ratio, mu_x)
        
        logger.debug(f"Calculated exports with exchange_rate_ratio={exchange_rate_ratio}, "
                    f"foreign_income_ratio={foreign_income_ratio}")
        
        return exports
        
    except (ValueError, OverflowError, ZeroDivisionError) as e:
        logger.error(f"Error calculating exports: {e}")
        if isinstance(exchange_rate, pd.Series):
            return pd.Series([np.nan] * len(exchange_rate))
        else:
            return np.nan


def calculate_exports_dataframe(
    df: pd.DataFrame,
    *,
    exchange_rate_col: str = "exchange_rate",
    foreign_income_col: str = "Y_star",
    x_0: float,
    e_0: float,
    y_star_0: float,
    epsilon_x: float = 1.5,
    mu_x: float = 1.5,
    output_col: str = "X_USD_bn",
) -> pd.DataFrame:
    """Calculate exports for a DataFrame with time series data.
    
    Args:
        df: DataFrame containing exchange rate and foreign income data
        exchange_rate_col: Column name for exchange rate data
        foreign_income_col: Column name for foreign income data
        x_0: Initial exports in base period (billions USD)
        e_0: Initial exchange rate in base period (CNY per USD)
        y_star_0: Initial foreign income in base period (index)
        epsilon_x: Export exchange rate elasticity (default: 1.5)
        mu_x: Export income elasticity (default: 1.5)
        output_col: Column name for calculated exports (default: "X_USD_bn")
        
    Returns:
        DataFrame with exports column added
        
    Raises:
        ValueError: If required columns are missing
    """
    # Validate required columns
    required_cols = [exchange_rate_col, foreign_income_col]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    result_df = df.copy()
    
    # Calculate exports
    result_df[output_col] = calculate_exports(
        exchange_rate=df[exchange_rate_col],
        foreign_income=df[foreign_income_col],
        x_0=x_0,
        e_0=e_0,
        y_star_0=y_star_0,
        epsilon_x=epsilon_x,
        mu_x=mu_x,
    )
    
    logger.info(f"Calculated exports for {len(result_df)} periods")
    
    return result_df
