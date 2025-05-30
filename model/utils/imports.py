"""Import calculation module for the China Growth Model.

This module implements the import equation:
M_t = M_0 * (e_t/e_0)^ε_m * (Y_t/Y_0)^μ_m

Where:
- M_t: Imports in period t
- M_0: Initial imports
- e_t: Exchange rate in period t
- e_0: Initial exchange rate
- Y_t: Domestic income in period t
- Y_0: Initial domestic income
- ε_m: Exchange rate elasticity of imports (default: -1.2)
- μ_m: Domestic income elasticity of imports (default: 1.1)
"""

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# --- Data Classes for Configuration ---


@dataclass
class ImportEquationParams:
    """Parameters for the import equation."""

    m_0: float
    e_0: float
    y_0: float
    epsilon_m: float = -1.2
    mu_m: float = 1.1


@dataclass
class ImportColumnConfig:
    """Column names for import DataFrame calculations."""

    exchange_rate_col: str = "exchange_rate"
    domestic_income_col: str = "GDP_USD_bn"
    output_col: str = "M_USD_bn"


# --- Helper Functions (Internal) ---


def _validate_initial_parameters(params: ImportEquationParams) -> None:
    """Validate initial parameter values from ImportEquationParams."""
    if params.m_0 <= 0:
        m_0_msg = f"Initial imports m_0 must be positive, got {params.m_0}"
        raise ValueError(m_0_msg)
    if params.e_0 <= 0:
        e_0_msg = f"Initial exchange rate e_0 must be positive, got {params.e_0}"
        raise ValueError(e_0_msg)
    if params.y_0 <= 0:
        y_0_msg = f"Initial domestic income y_0 must be positive, got {params.y_0}"
        raise ValueError(y_0_msg)


def _process_series_inputs(
    exchange_rate: float | pd.Series[float], domestic_income: float | pd.Series[float]
) -> tuple[pd.Series[float], pd.Series[float]]:
    """Process and validate series inputs.

    Args:
        exchange_rate: Exchange rate values
        domestic_income: Domestic income values

    Returns:
        Tuple of processed exchange rate and domestic income series
    """
    # Convert to pandas Series for consistent handling
    max_len = max(
        len(exchange_rate) if isinstance(exchange_rate, pd.Series) else 1,
        len(domestic_income) if isinstance(domestic_income, pd.Series) else 1,
    )

    if not isinstance(exchange_rate, pd.Series):
        exchange_rate = pd.Series([exchange_rate] * max_len, dtype=float)
    if not isinstance(domestic_income, pd.Series):
        domestic_income = pd.Series([domestic_income] * max_len, dtype=float)

    # Validate and clip negative values
    if (exchange_rate <= 0).any():
        logger.warning("Some exchange rate values are non-positive")
        exchange_rate = exchange_rate.clip(lower=1e-6)

    if (domestic_income <= 0).any():
        logger.warning("Some domestic income values are non-positive")
        domestic_income = domestic_income.clip(lower=1e-6)

    return exchange_rate, domestic_income


def _process_scalar_inputs(exchange_rate: float, domestic_income: float) -> tuple[float, float]:
    """Process and validate scalar inputs.

    Args:
        exchange_rate: Exchange rate value
        domestic_income: Domestic income value

    Returns:
        Tuple of processed exchange rate and domestic income values
    """
    if exchange_rate <= 0:
        logger.warning("Exchange rate %s is non-positive, clipping to 1e-6", exchange_rate)
        exchange_rate = max(exchange_rate, 1e-6)

    if domestic_income <= 0:
        logger.warning("Domestic income %s is non-positive, clipping to 1e-6", domestic_income)
        domestic_income = max(domestic_income, 1e-6)

    return exchange_rate, domestic_income


def _compute_imports(
    exchange_rate: float | pd.Series[float],
    domestic_income: float | pd.Series[float],
    params: ImportEquationParams,
) -> float | pd.Series[float]:
    """Compute imports using the import equation.

    Args:
        exchange_rate: Processed exchange rate values
        domestic_income: Processed domestic income values
        params: ImportEquationParams object

    Returns:
        Calculated imports
    """
    try:
        exchange_rate_ratio = exchange_rate / params.e_0
        domestic_income_ratio = domestic_income / params.y_0

        imports = (
            params.m_0
            * (exchange_rate_ratio**params.epsilon_m)
            * (domestic_income_ratio**params.mu_m)
        )

        logger.debug(
            "Calculated imports with exchange_rate_ratio=%s, domestic_income_ratio=%s",
            exchange_rate_ratio,
            domestic_income_ratio,
        )
    except (ValueError, OverflowError, ZeroDivisionError):
        logger.exception("Error calculating imports")
        if isinstance(exchange_rate, pd.Series):
            return pd.Series([np.nan] * len(exchange_rate), dtype=float)
        return np.nan
    else:
        return imports


# --- Main Calculation Functions ---


def calculate_imports(
    exchange_rate: float | pd.Series[float],
    domestic_income: float | pd.Series[float],
    params: ImportEquationParams,
) -> float | pd.Series[float]:
    """Calculate imports using the China growth model import equation.

    Args:
        exchange_rate: Exchange rate in period t
        domestic_income: Domestic income in period t
        params: ImportEquationParams object

    Returns:
        Calculated imports (billions USD)

    Raises:
        ValueError: If any parameters are invalid

    Example:
        >>> params = ImportEquationParams(m_0=21.84, e_0=1.5, y_0=300.0)
        >>> imports = calculate_imports(exchange_rate=8.0, domestic_income=500.0, params=params)
    """
    # Validate initial parameters
    _validate_initial_parameters(params)

    # Process inputs based on type
    if isinstance(exchange_rate, pd.Series) or isinstance(domestic_income, pd.Series):
        exchange_rate, domestic_income = _process_series_inputs(exchange_rate, domestic_income)
    else:
        exchange_rate, domestic_income = _process_scalar_inputs(exchange_rate, domestic_income)

    # Compute and return imports
    return _compute_imports(exchange_rate, domestic_income, params)


def calculate_imports_dataframe(
    df: pd.DataFrame,
    params: ImportEquationParams,
    column_config: ImportColumnConfig | None = None,
) -> pd.DataFrame:
    """Calculate imports for a DataFrame with time series data.

    Args:
        df: DataFrame containing exchange rate and domestic income data
        params: ImportEquationParams object
        column_config: Configuration for column names. If None, a default config is used.

    Returns:
        DataFrame with imports column added

    Raises:
        ValueError: If required columns are missing
    """
    if column_config is None:
        column_config = ImportColumnConfig()

    # Validate required columns
    required_cols = [column_config.exchange_rate_col, column_config.domestic_income_col]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        missing_cols_str = ", ".join(missing_cols)
        msg = f"Missing required columns: {missing_cols_str}"
        raise ValueError(msg)

    result_df = df.copy()

    # Calculate imports
    result_df[column_config.output_col] = calculate_imports(
        exchange_rate=df[column_config.exchange_rate_col],
        domestic_income=df[column_config.domestic_income_col],
        params=params,
    )

    logger.info("Calculated imports for %d periods", len(result_df))

    return result_df
