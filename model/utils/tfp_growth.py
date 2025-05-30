"""TFP growth calculation module for the China Growth Model.

This module implements the TFP growth equation with spillover effects:
A_{t+1} = A_t * (1 + g + θ * openness_t + φ * fdi_ratio_t)

Where:
- A_t: Total Factor Productivity in period t
- A_{t+1}: Total Factor Productivity in period t+1
- g: Baseline TFP growth rate
- θ: Openness contribution to TFP growth
- openness_t: Trade openness ratio in period t
- φ: FDI contribution to TFP growth
- fdi_ratio_t: FDI inflows as ratio of GDP in period t
"""

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# --- Data Classes for Configuration ---


@dataclass
class TFPGrowthEquationParams:
    """Parameters for the TFP growth equation."""

    g: float = 0.02  # Baseline TFP growth rate
    theta: float = 0.10  # Openness contribution to TFP growth
    phi: float = 0.08  # FDI contribution to TFP growth


@dataclass
class TFPGrowthColumnConfig:
    """Column names for TFP growth DataFrame calculations."""

    tfp_col: str = "TFP"
    openness_col: str = "Openness_Ratio"
    fdi_col: str = "fdi_ratio"
    output_col: str = "TFP_next"


# --- Helper Functions (Internal) ---


def _validate_and_clip_tfp(current_tfp: float | pd.Series[float]) -> float | pd.Series[float]:
    """Validate and clip TFP values."""
    if isinstance(current_tfp, pd.Series):
        if (current_tfp <= 0).any():
            logger.warning("Some current TFP values are non-positive")
            current_tfp = current_tfp.clip(lower=1e-6)
    elif current_tfp <= 0:
        logger.warning("Current TFP %s is non-positive, clipping to 1e-6", current_tfp)
        current_tfp = max(current_tfp, 1e-6)
    return current_tfp


def _validate_and_clip_scalar_ratios(
    openness_ratio: float, fdi_ratio: float
) -> tuple[float, float]:
    """Validate and clip scalar ratio inputs."""
    if openness_ratio < 0:
        logger.warning("Openness ratio %s is negative, clipping to 0", openness_ratio)
        openness_ratio = max(openness_ratio, 0)

    if fdi_ratio < 0:
        logger.warning("FDI ratio %s is negative, clipping to 0", fdi_ratio)
        fdi_ratio = max(fdi_ratio, 0)

    return openness_ratio, fdi_ratio


def _validate_and_clip_series_ratios(
    openness_ratio: pd.Series[float], fdi_ratio: pd.Series[float]
) -> tuple[pd.Series[float], pd.Series[float]]:
    """Validate and clip series ratio inputs."""
    if (openness_ratio < 0).any():
        logger.warning("Some openness ratio values are negative")
        openness_ratio = openness_ratio.clip(lower=0)

    if (fdi_ratio < 0).any():
        logger.warning("Some FDI ratio values are negative")
        fdi_ratio = fdi_ratio.clip(lower=0)

    return openness_ratio, fdi_ratio


def _convert_to_series_for_tfp(
    current_tfp: float | pd.Series[float],
    openness_ratio: float | pd.Series[float],
    fdi_ratio: float | pd.Series[float],
) -> tuple[pd.Series[float], pd.Series[float], pd.Series[float]]:
    """Convert inputs to pandas Series for consistent handling."""
    if not isinstance(openness_ratio, pd.Series):
        openness_len = len(fdi_ratio) if isinstance(fdi_ratio, pd.Series) else 1
        openness_ratio = pd.Series([openness_ratio] * openness_len, dtype=float)
    if not isinstance(fdi_ratio, pd.Series):
        fdi_len = len(openness_ratio) if isinstance(openness_ratio, pd.Series) else 1
        fdi_ratio = pd.Series([fdi_ratio] * fdi_len, dtype=float)
    if not isinstance(current_tfp, pd.Series):
        tfp_len = len(openness_ratio) if isinstance(openness_ratio, pd.Series) else 1
        current_tfp = pd.Series([current_tfp] * tfp_len, dtype=float)

    return current_tfp, openness_ratio, fdi_ratio


def calculate_tfp_growth(
    current_tfp: float | pd.Series[float],
    openness_ratio: float | pd.Series[float],
    fdi_ratio: float | pd.Series[float],
    params: TFPGrowthEquationParams | None = None,
) -> float | pd.Series[float]:
    """Calculate next period TFP using the growth equation with spillovers.

    Args:
        current_tfp: Current period TFP (A_t)
        openness_ratio: Trade openness ratio ((X+M)/Y)
        fdi_ratio: FDI inflows as ratio of GDP
        params: TFPGrowthEquationParams object with g, theta, phi.
            If None, a default config is used.

    Returns:
        Next period TFP (A_{t+1})

    Raises:
        ValueError: If any parameters are invalid

    Example:
        >>> params_obj = TFPGrowthEquationParams(g=0.02, theta=0.10, phi=0.08)
        >>> next_tfp = calculate_tfp_growth(
        ...     current_tfp=1.0, openness_ratio=0.3, fdi_ratio=0.05, params=params_obj
        ... )
    """
    if params is None:
        params = TFPGrowthEquationParams()
    # Validate TFP inputs
    current_tfp = _validate_and_clip_tfp(current_tfp)

    # Handle both scalar and series inputs
    if isinstance(openness_ratio, pd.Series) or isinstance(fdi_ratio, pd.Series):
        current_tfp, openness_ratio, fdi_ratio = _convert_to_series_for_tfp(
            current_tfp, openness_ratio, fdi_ratio
        )
        openness_ratio, fdi_ratio = _validate_and_clip_series_ratios(openness_ratio, fdi_ratio)
    else:
        openness_ratio, fdi_ratio = _validate_and_clip_scalar_ratios(openness_ratio, fdi_ratio)

    try:
        # Calculate TFP growth using the formula:
        # A_{t+1} = A_t * (1 + g + θ * openness_t + φ * fdi_ratio_t)
        growth_rate = params.g + params.theta * openness_ratio + params.phi * fdi_ratio
        next_tfp = current_tfp * (1 + growth_rate)

        logger.debug("Calculated TFP growth with growth_rate=%s", growth_rate)
    except (ValueError, OverflowError):
        logger.exception("Error calculating TFP growth")
        if isinstance(current_tfp, pd.Series):
            return pd.Series([np.nan] * len(current_tfp), dtype=float)
        return np.nan
    else:
        return next_tfp


def calculate_tfp_growth_dataframe(
    df: pd.DataFrame,
    params: TFPGrowthEquationParams | None = None,
    column_config: TFPGrowthColumnConfig | None = None,
) -> pd.DataFrame:
    """Calculate next period TFP for a DataFrame with time series data.

    Args:
        df: DataFrame containing TFP, openness, and FDI data
        params: TFPGrowthEquationParams object. If None, a default config is used.
        column_config: TFPGrowthColumnConfig object for column names.
            If None, a default config is used.

    Returns:
        DataFrame with next period TFP column added

    Raises:
        ValueError: If required columns are missing
    """
    if params is None:
        params = TFPGrowthEquationParams()
    if column_config is None:
        column_config = TFPGrowthColumnConfig()

    # Validate required columns
    required_cols = [column_config.tfp_col, column_config.openness_col, column_config.fdi_col]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        msg = f"Missing required columns: {missing_cols}"
        raise ValueError(msg)

    result_df = df.copy()

    # Calculate next period TFP
    result_df[column_config.output_col] = calculate_tfp_growth(
        current_tfp=df[column_config.tfp_col],
        openness_ratio=df[column_config.openness_col],
        fdi_ratio=df[column_config.fdi_col],
        params=params,
    )

    logger.info("Calculated TFP growth for %d periods", len(result_df))

    return result_df


def calculate_tfp_sequence(
    initial_tfp: float,
    openness_sequence: pd.Series[float],
    fdi_sequence: pd.Series[float],
    params: TFPGrowthEquationParams | None = None,
) -> pd.Series[float]:
    """Calculate a sequence of TFP values over multiple periods.

    Args:
        initial_tfp: Initial TFP value (A_0)
        openness_sequence: Series of openness ratios over time
        fdi_sequence: Series of FDI ratios over time
        params: TFPGrowthEquationParams object. If None, a default config is used.

    Returns:
        Series of TFP values over time

    Raises:
        ValueError: If sequences have different lengths
    """
    if params is None:
        params = TFPGrowthEquationParams()

    length_error_msg = "Openness and FDI sequences must have the same length"
    if len(openness_sequence) != len(fdi_sequence):
        raise ValueError(length_error_msg)

    tfp_sequence = pd.Series(index=openness_sequence.index, dtype=float)
    current_tfp: float = initial_tfp

    for i, (openness, fdi) in enumerate(zip(openness_sequence, fdi_sequence, strict=False)):
        tfp_sequence.iloc[i] = current_tfp

        # Calculate next period TFP
        tfp_result = calculate_tfp_growth(
            current_tfp=current_tfp,
            openness_ratio=openness,
            fdi_ratio=fdi,
            params=params,
        )
        # Since we're passing floats, we know the result is a float
        current_tfp = tfp_result.iloc[0] if isinstance(tfp_result, pd.Series) else tfp_result

    logger.info("Calculated TFP sequence for %d periods", len(tfp_sequence))

    return tfp_sequence
