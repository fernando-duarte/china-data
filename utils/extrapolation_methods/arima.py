"""ARIMA (Auto-Regressive Integrated Moving Average) extrapolation method.

This module provides a function to extrapolate time series data using the ARIMA model.
"""

import logging

import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

from config import Config

logger = logging.getLogger(__name__)


def extrapolate_with_arima(
    df: pd.DataFrame,
    col: str,
    years_to_project: list[int],
    min_data_points: int = Config.MIN_DATA_POINTS_FOR_ARIMA,
    order: tuple[int, int, int] = Config.DEFAULT_ARIMA_ORDER,
) -> tuple[pd.DataFrame, bool, str]:
    """Extrapolate a time series using ARIMA model.

    Args:
        df (pd.DataFrame): DataFrame containing the time series data
        col (str): Column name of the series to extrapolate
        years_to_project (list): List of years to project values for
        min_data_points (int): Minimum number of data points required for ARIMA (default: from Config)
        order (tuple): ARIMA order parameters as (p, d, q) (default: from Config)

    Returns:
        tuple: (updated_df, success, method_info)
            - updated_df: DataFrame with extrapolated values
            - success: Boolean indicating if ARIMA was successful
            - method_info: String describing the method used
    """
    # Create a copy of the dataframe to avoid modifying the original
    df_result = df.copy()

    # Check if the column exists and has sufficient data
    if col not in df_result.columns or df_result[col].isna().all():
        return df_result, False, "No data"

    # Get historical data (non-NA values)
    historical = df_result[["year", col]].dropna()

    if len(historical) < min_data_points:
        logger.info("Insufficient data for ARIMA on %s (need %d, have %d)", col, min_data_points, len(historical))
        return df_result, False, f"Insufficient data (need {min_data_points})"

    # Get the last observed year
    last_year = int(historical["year"].max())

    # Filter years to actually project (might be fewer than requested if some already exist)
    yrs = [y for y in years_to_project if y > last_year]
    if not yrs:
        return df_result, False, "No years to project"

    try:
        # Fit ARIMA model
        model = ARIMA(historical[col], order=order)
        model_fit = model.fit()

        # Generate forecasts
        fc = model_fit.forecast(steps=len(yrs))
        vals = fc.tolist() if hasattr(fc, "tolist") else list(fc)

        # Update the dataframe with projected values
        for i, year in enumerate(yrs):
            df_result.loc[df_result.year == year, col] = round(max(0, vals[i]), Config.DECIMAL_PLACES_PROJECTIONS)

        logger.info(
            "Successfully applied ARIMA(%d,%d,%d) to %s for years %d-%d",
            order[0],
            order[1],
            order[2],
            col,
            min(yrs),
            max(yrs),
        )
        return df_result, True, f"ARIMA({order[0]},{order[1]},{order[2]})"

    except (ValueError, TypeError) as e:
        logger.warning("ARIMA failed for %s, error: %s", col, str(e))
        return df_result, False, f"ARIMA failed: {e!s}"
