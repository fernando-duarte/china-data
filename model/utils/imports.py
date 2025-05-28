"""Import calculation module for the China Growth Model.

This module implements the import equation:
M_t = M_0 * (e_t/e_0)^ε_m * (Y_t/Y_0)^μ_m

Where:
- M_t: Imports in period t
- M_0: Initial imports (base period)
- e_t: Exchange rate in period t (CNY per USD)
- e_0: Initial exchange rate (base period)
- ε_m: Import exchange rate elasticity (typically negative)
- Y_t: Domestic income (GDP) in period t
- Y_0: Initial domestic income (base period)
- μ_m: Import income elasticity
"""

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def calculate_imports(
    exchange_rate: float | pd.Series,
    domestic_income: float | pd.Series,
    *,
    m_0: float,
    e_0: float,
    y_0: float,
    epsilon_m: float = -1.2,
    mu_m: float = 1.1,
) -> float | pd.Series:
    """Calculate imports using the China growth model import equation.

    Args:
        exchange_rate: Current exchange rate(s) (CNY per USD)
        domestic_income: Current domestic income (GDP) (billions USD)
        m_0: Initial imports in base period (billions USD)
        e_0: Initial exchange rate in base period (CNY per USD)
        y_0: Initial domestic income in base period (billions USD)
        epsilon_m: Import exchange rate elasticity (default: -1.2, typically negative)
        mu_m: Import income elasticity (default: 1.1)

    Returns:
        Calculated imports (billions USD)

    Raises:
        ValueError: If any parameters are invalid

    Example:
        >>> imports = calculate_imports(
        ...     exchange_rate=8.0, domestic_income=500.0, m_0=21.84, e_0=1.5, y_0=300.0, epsilon_m=-1.2, mu_m=1.1
        ... )
    """
    # Validate inputs
    if m_0 <= 0:
        raise ValueError(f"Initial imports m_0 must be positive, got {m_0}")
    if e_0 <= 0:
        raise ValueError(f"Initial exchange rate e_0 must be positive, got {e_0}")
    if y_0 <= 0:
        raise ValueError(f"Initial domestic income y_0 must be positive, got {y_0}")

    # Handle both scalar and series inputs
    if isinstance(exchange_rate, pd.Series) or isinstance(domestic_income, pd.Series):
        # Convert to pandas Series for consistent handling
        if not isinstance(exchange_rate, pd.Series):
            exchange_rate = pd.Series([exchange_rate] * len(domestic_income))
        if not isinstance(domestic_income, pd.Series):
            domestic_income = pd.Series([domestic_income] * len(exchange_rate))

        # Check for invalid values
        if (exchange_rate <= 0).any():
            logger.warning("Some exchange rate values are non-positive")
            exchange_rate = exchange_rate.clip(lower=1e-6)

        if (domestic_income <= 0).any():
            logger.warning("Some domestic income values are non-positive")
            domestic_income = domestic_income.clip(lower=1e-6)
    else:
        # Scalar inputs
        if exchange_rate <= 0:
            logger.warning(f"Exchange rate {exchange_rate} is non-positive, clipping to 1e-6")
            exchange_rate = max(exchange_rate, 1e-6)

        if domestic_income <= 0:
            logger.warning(f"Domestic income {domestic_income} is non-positive, clipping to 1e-6")
            domestic_income = max(domestic_income, 1e-6)

    try:
        # Calculate imports using the formula:
        # M_t = M_0 * (e_t/e_0)^ε_m * (Y_t/Y_0)^μ_m
        exchange_rate_ratio = exchange_rate / e_0
        domestic_income_ratio = domestic_income / y_0

        imports = m_0 * np.power(exchange_rate_ratio, epsilon_m) * np.power(domestic_income_ratio, mu_m)

        logger.debug(
            f"Calculated imports with exchange_rate_ratio={exchange_rate_ratio}, "
            f"domestic_income_ratio={domestic_income_ratio}"
        )

        return imports

    except (ValueError, OverflowError, ZeroDivisionError) as e:
        logger.error(f"Error calculating imports: {e}")
        if isinstance(exchange_rate, pd.Series):
            return pd.Series([np.nan] * len(exchange_rate))
        return np.nan


def calculate_imports_dataframe(
    df: pd.DataFrame,
    *,
    exchange_rate_col: str = "exchange_rate",
    domestic_income_col: str = "GDP_USD_bn",
    m_0: float,
    e_0: float,
    y_0: float,
    epsilon_m: float = -1.2,
    mu_m: float = 1.1,
    output_col: str = "M_USD_bn",
) -> pd.DataFrame:
    """Calculate imports for a DataFrame with time series data.

    Args:
        df: DataFrame containing exchange rate and domestic income data
        exchange_rate_col: Column name for exchange rate data
        domestic_income_col: Column name for domestic income (GDP) data
        m_0: Initial imports in base period (billions USD)
        e_0: Initial exchange rate in base period (CNY per USD)
        y_0: Initial domestic income in base period (billions USD)
        epsilon_m: Import exchange rate elasticity (default: -1.2)
        mu_m: Import income elasticity (default: 1.1)
        output_col: Column name for calculated imports (default: "M_USD_bn")

    Returns:
        DataFrame with imports column added

    Raises:
        ValueError: If required columns are missing
    """
    # Validate required columns
    required_cols = [exchange_rate_col, domestic_income_col]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    result_df = df.copy()

    # Calculate imports
    result_df[output_col] = calculate_imports(
        exchange_rate=df[exchange_rate_col],
        domestic_income=df[domestic_income_col],
        m_0=m_0,
        e_0=e_0,
        y_0=y_0,
        epsilon_m=epsilon_m,
        mu_m=mu_m,
    )

    logger.info(f"Calculated imports for {len(result_df)} periods")

    return result_df
