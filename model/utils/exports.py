"""Export calculation module for the China Growth Model.

This module implements the export equation:
X_t = X_0 * (e_t/e_0)^ε_x * (Y*_t/Y*_0)^μ_x

Where:
- X_t: Exports in period t
- X_0: Initial exports
- e_t: Exchange rate in period t
- e_0: Initial exchange rate
- Y*_t: Foreign income in period t
- Y*_0: Initial foreign income
- ε_x: Exchange rate elasticity of exports (default: 1.5)
- μ_x: Foreign income elasticity of exports (default: 1.5)
"""

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def _validate_initial_parameters(x_0: float, e_0: float, y_star_0: float) -> None:
    """Validate initial parameter values.

    Args:
        x_0: Initial exports
        e_0: Initial exchange rate
        y_star_0: Initial foreign income

    Raises:
        ValueError: If any parameters are invalid
    """
    if x_0 <= 0:
        x_0_msg = f"Initial exports x_0 must be positive, got {x_0}"
        raise ValueError(x_0_msg)
    if e_0 <= 0:
        e_0_msg = f"Initial exchange rate e_0 must be positive, got {e_0}"
        raise ValueError(e_0_msg)
    if y_star_0 <= 0:
        y_star_0_msg = f"Initial foreign income y_star_0 must be positive, got {y_star_0}"
        raise ValueError(y_star_0_msg)


def _process_series_inputs(
    exchange_rate: float | pd.Series, foreign_income: float | pd.Series
) -> tuple[pd.Series, pd.Series]:
    """Process and validate series inputs.

    Args:
        exchange_rate: Exchange rate values
        foreign_income: Foreign income values

    Returns:
        Tuple of processed exchange rate and foreign income series
    """
    # Convert to pandas Series for consistent handling
    max_len = max(
        len(exchange_rate) if isinstance(exchange_rate, pd.Series) else 1,
        len(foreign_income) if isinstance(foreign_income, pd.Series) else 1,
    )

    if not isinstance(exchange_rate, pd.Series):
        exchange_rate = pd.Series([exchange_rate] * max_len)
    if not isinstance(foreign_income, pd.Series):
        foreign_income = pd.Series([foreign_income] * max_len)

    # Validate and clip negative values
    if (exchange_rate <= 0).any():
        logger.warning("Some exchange rate values are non-positive")
        exchange_rate = exchange_rate.clip(lower=1e-6)

    if (foreign_income <= 0).any():
        logger.warning("Some foreign income values are non-positive")
        foreign_income = foreign_income.clip(lower=1e-6)

    return exchange_rate, foreign_income


def _process_scalar_inputs(exchange_rate: float, foreign_income: float) -> tuple[float, float]:
    """Process and validate scalar inputs.

    Args:
        exchange_rate: Exchange rate value
        foreign_income: Foreign income value

    Returns:
        Tuple of processed exchange rate and foreign income values
    """
    if exchange_rate <= 0:
        logger.warning("Exchange rate %s is non-positive, clipping to 1e-6", exchange_rate)
        exchange_rate = max(exchange_rate, 1e-6)

    if foreign_income <= 0:
        logger.warning("Foreign income %s is non-positive, clipping to 1e-6", foreign_income)
        foreign_income = max(foreign_income, 1e-6)

    return exchange_rate, foreign_income


def _compute_exports(
    exchange_rate: float | pd.Series,
    foreign_income: float | pd.Series,
    x_0: float,
    e_0: float,
    y_star_0: float,
    epsilon_x: float,
    mu_x: float,
) -> float | pd.Series:
    """Compute exports using the export equation.

    Args:
        exchange_rate: Processed exchange rate values
        foreign_income: Processed foreign income values
        x_0: Initial exports
        e_0: Initial exchange rate
        y_star_0: Initial foreign income
        epsilon_x: Exchange rate elasticity
        mu_x: Foreign income elasticity

    Returns:
        Calculated exports
    """
    try:
        exchange_rate_ratio = exchange_rate / e_0
        foreign_income_ratio = foreign_income / y_star_0

        exports = x_0 * (exchange_rate_ratio**epsilon_x) * (foreign_income_ratio**mu_x)

        logger.debug(
            "Calculated exports with exchange_rate_ratio=%s, foreign_income_ratio=%s",
            exchange_rate_ratio,
            foreign_income_ratio,
        )
    except (ValueError, OverflowError, ZeroDivisionError):
        logger.exception("Error calculating exports")
        if isinstance(exchange_rate, pd.Series):
            return pd.Series([np.nan] * len(exchange_rate))
        return np.nan
    else:
        return exports


def calculate_exports(
    exchange_rate: float | pd.Series,
    foreign_income: float | pd.Series,
    x_0: float,
    e_0: float,
    y_star_0: float,
    epsilon_x: float = 1.5,
    mu_x: float = 1.5,
) -> float | pd.Series:
    """Calculate exports using the China growth model export equation.

    Args:
        exchange_rate: Exchange rate in period t
        foreign_income: Foreign income in period t
        x_0: Initial exports (billions USD)
        e_0: Initial exchange rate
        y_star_0: Initial foreign income
        epsilon_x: Exchange rate elasticity of exports (default: 1.5)
        mu_x: Foreign income elasticity of exports (default: 1.5)

    Returns:
        Calculated exports (billions USD)

    Raises:
        ValueError: If any parameters are invalid

    Example:
        >>> exports = calculate_exports(exchange_rate=8.0, foreign_income=1200.0, x_0=19.41, e_0=1.5, y_star_0=1000.0)
    """
    # Validate initial parameters
    _validate_initial_parameters(x_0, e_0, y_star_0)

    # Process inputs based on type
    if isinstance(exchange_rate, pd.Series) or isinstance(foreign_income, pd.Series):
        exchange_rate, foreign_income = _process_series_inputs(exchange_rate, foreign_income)
    else:
        exchange_rate, foreign_income = _process_scalar_inputs(exchange_rate, foreign_income)

    # Compute and return exports
    return _compute_exports(exchange_rate, foreign_income, x_0, e_0, y_star_0, epsilon_x, mu_x)


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
        x_0: Initial exports (billions USD)
        e_0: Initial exchange rate
        y_star_0: Initial foreign income
        epsilon_x: Exchange rate elasticity of exports (default: 1.5)
        mu_x: Foreign income elasticity of exports (default: 1.5)
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
        missing_cols_str = ", ".join(missing_cols)
        msg = f"Missing required columns: {missing_cols_str}"
        raise ValueError(msg)

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

    logger.info("Calculated exports for %d periods", len(result_df))

    return result_df
