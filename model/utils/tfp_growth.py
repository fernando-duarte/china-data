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

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def _validate_and_clip_tfp(current_tfp: float | pd.Series) -> float | pd.Series:
    """Validate and clip TFP values."""
    if isinstance(current_tfp, pd.Series):
        if (current_tfp <= 0).any():
            logger.warning("Some current TFP values are non-positive")
            current_tfp = current_tfp.clip(lower=1e-6)
    elif current_tfp <= 0:
        logger.warning("Current TFP %s is non-positive, clipping to 1e-6", current_tfp)
        current_tfp = max(current_tfp, 1e-6)
    return current_tfp


def _validate_and_clip_scalar_ratios(openness_ratio: float, fdi_ratio: float) -> tuple[float, float]:
    """Validate and clip scalar ratio inputs."""
    if openness_ratio < 0:
        logger.warning("Openness ratio %s is negative, clipping to 0", openness_ratio)
        openness_ratio = max(openness_ratio, 0)

    if fdi_ratio < 0:
        logger.warning("FDI ratio %s is negative, clipping to 0", fdi_ratio)
        fdi_ratio = max(fdi_ratio, 0)

    return openness_ratio, fdi_ratio


def _validate_and_clip_series_ratios(openness_ratio: pd.Series, fdi_ratio: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Validate and clip series ratio inputs."""
    if (openness_ratio < 0).any():
        logger.warning("Some openness ratio values are negative")
        openness_ratio = openness_ratio.clip(lower=0)

    if (fdi_ratio < 0).any():
        logger.warning("Some FDI ratio values are negative")
        fdi_ratio = fdi_ratio.clip(lower=0)

    return openness_ratio, fdi_ratio


def _convert_to_series_for_tfp(
    current_tfp: float | pd.Series,
    openness_ratio: float | pd.Series,
    fdi_ratio: float | pd.Series,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Convert inputs to pandas Series for consistent handling."""
    if not isinstance(openness_ratio, pd.Series):
        openness_ratio = pd.Series([openness_ratio] * len(fdi_ratio))
    if not isinstance(fdi_ratio, pd.Series):
        fdi_ratio = pd.Series([fdi_ratio] * len(openness_ratio))
    if not isinstance(current_tfp, pd.Series):
        current_tfp = pd.Series([current_tfp] * len(openness_ratio))

    return current_tfp, openness_ratio, fdi_ratio


def calculate_tfp_growth(
    current_tfp: float | pd.Series,
    openness_ratio: float | pd.Series,
    fdi_ratio: float | pd.Series,
    *,
    g: float = 0.02,
    theta: float = 0.10,
    phi: float = 0.08,
) -> float | pd.Series:
    """Calculate next period TFP using the growth equation with spillovers.

    Args:
        current_tfp: Current period TFP (A_t)
        openness_ratio: Trade openness ratio ((X+M)/Y)
        fdi_ratio: FDI inflows as ratio of GDP
        g: Baseline TFP growth rate (default: 0.02)
        theta: Openness contribution to TFP growth (default: 0.10)
        phi: FDI contribution to TFP growth (default: 0.08)

    Returns:
        Next period TFP (A_{t+1})

    Raises:
        ValueError: If any parameters are invalid

    Example:
        >>> next_tfp = calculate_tfp_growth(
        ...     current_tfp=1.0, openness_ratio=0.3, fdi_ratio=0.05, g=0.02, theta=0.10, phi=0.08
        ... )
    """
    # Validate TFP inputs
    current_tfp = _validate_and_clip_tfp(current_tfp)

    # Handle both scalar and series inputs
    if isinstance(openness_ratio, pd.Series) or isinstance(fdi_ratio, pd.Series):
        current_tfp, openness_ratio, fdi_ratio = _convert_to_series_for_tfp(current_tfp, openness_ratio, fdi_ratio)
        openness_ratio, fdi_ratio = _validate_and_clip_series_ratios(openness_ratio, fdi_ratio)
    else:
        openness_ratio, fdi_ratio = _validate_and_clip_scalar_ratios(openness_ratio, fdi_ratio)

    try:
        # Calculate TFP growth using the formula:
        # A_{t+1} = A_t * (1 + g + θ * openness_t + φ * fdi_ratio_t)
        growth_rate = g + theta * openness_ratio + phi * fdi_ratio
        next_tfp = current_tfp * (1 + growth_rate)

        logger.debug("Calculated TFP growth with growth_rate=%s", growth_rate)
    except (ValueError, OverflowError):
        logger.exception("Error calculating TFP growth")
        if isinstance(current_tfp, pd.Series):
            return pd.Series([np.nan] * len(current_tfp))
        return np.nan
    else:
        return next_tfp


def calculate_tfp_growth_dataframe(
    df: pd.DataFrame,
    *,
    tfp_col: str = "TFP",
    openness_col: str = "Openness_Ratio",
    fdi_col: str = "fdi_ratio",
    g: float = 0.02,
    theta: float = 0.10,
    phi: float = 0.08,
    output_col: str = "TFP_next",
) -> pd.DataFrame:
    """Calculate next period TFP for a DataFrame with time series data.

    Args:
        df: DataFrame containing TFP, openness, and FDI data
        tfp_col: Column name for current TFP data
        openness_col: Column name for openness ratio data
        fdi_col: Column name for FDI ratio data
        g: Baseline TFP growth rate (default: 0.02)
        theta: Openness contribution to TFP growth (default: 0.10)
        phi: FDI contribution to TFP growth (default: 0.08)
        output_col: Column name for calculated next period TFP

    Returns:
        DataFrame with next period TFP column added

    Raises:
        ValueError: If required columns are missing
    """
    # Validate required columns
    required_cols = [tfp_col, openness_col, fdi_col]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        msg = f"Missing required columns: {missing_cols}"
        raise ValueError(msg)

    result_df = df.copy()

    # Calculate next period TFP
    result_df[output_col] = calculate_tfp_growth(
        current_tfp=df[tfp_col],
        openness_ratio=df[openness_col],
        fdi_ratio=df[fdi_col],
        g=g,
        theta=theta,
        phi=phi,
    )

    logger.info("Calculated TFP growth for %d periods", len(result_df))

    return result_df


def calculate_tfp_sequence(
    initial_tfp: float,
    openness_sequence: pd.Series,
    fdi_sequence: pd.Series,
    *,
    g: float = 0.02,
    theta: float = 0.10,
    phi: float = 0.08,
) -> pd.Series:
    """Calculate a sequence of TFP values over multiple periods.

    Args:
        initial_tfp: Initial TFP value (A_0)
        openness_sequence: Series of openness ratios over time
        fdi_sequence: Series of FDI ratios over time
        g: Baseline TFP growth rate (default: 0.02)
        theta: Openness contribution to TFP growth (default: 0.10)
        phi: FDI contribution to TFP growth (default: 0.08)

    Returns:
        Series of TFP values over time

    Raises:
        ValueError: If sequences have different lengths
    """
    length_error_msg = "Openness and FDI sequences must have the same length"
    if len(openness_sequence) != len(fdi_sequence):
        raise ValueError(length_error_msg)

    tfp_sequence = pd.Series(index=openness_sequence.index, dtype=float)
    current_tfp = initial_tfp

    for i, (openness, fdi) in enumerate(zip(openness_sequence, fdi_sequence, strict=False)):
        tfp_sequence.iloc[i] = current_tfp

        # Calculate next period TFP
        current_tfp = calculate_tfp_growth(
            current_tfp=current_tfp,
            openness_ratio=openness,
            fdi_ratio=fdi,
            g=g,
            theta=theta,
            phi=phi,
        )

    logger.info("Calculated TFP sequence for %d periods", len(tfp_sequence))

    return tfp_sequence
