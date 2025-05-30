"""ARIMA (Auto-Regressive Integrated Moving Average) extrapolation method.

This module provides a function to extrapolate time series data using the ARIMA model.
"""

import logging

import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

from config import Config

from .extrapolation_helpers import ExtrapolationPrepResult, prepare_extrapolation_data

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
        min_data_points (int): Minimum number of data points required for ARIMA
            (default: from Config)
        order (tuple): ARIMA order parameters as (p, d, q) (default: from Config)

    Returns:
        tuple: (updated_df, success, method_info)
            - updated_df: DataFrame with extrapolated values
            - success: Boolean indicating if ARIMA was successful
            - method_info: String describing the method used
    """
    prep_result: ExtrapolationPrepResult = prepare_extrapolation_data(
        df, col, years_to_project, min_data_points, "ARIMA"
    )
    if not prep_result.success:
        return prep_result.df_result, False, prep_result.message

    # Ensure historical_data and yrs_filtered are not None before use
    if prep_result.historical_data is None or prep_result.years_to_project_filtered is None:
        # This case should ideally be caught by prep_result.success being False
        return prep_result.df_result, False, "Preparation failed unexpectedly"

    df_result = prep_result.df_result
    historical = prep_result.historical_data
    yrs_filtered = prep_result.years_to_project_filtered

    try:
        # Fit ARIMA model and generate forecasts
        model = ARIMA(historical[col], order=order)
        forecast_series = model.fit().forecast(steps=len(yrs_filtered))

        # Update the dataframe with projected values
        if hasattr(forecast_series, "tolist"):
            processed_forecast = forecast_series.tolist()
        else:
            processed_forecast = list(forecast_series)
        for i, year in enumerate(yrs_filtered):
            df_result.loc[df_result.year == year, col] = round(
                max(0, processed_forecast[i]), Config.DECIMAL_PLACES_PROJECTIONS
            )

        logger.info(
            "Successfully applied ARIMA(%d,%d,%d) to %s for years %d-%d",
            order[0],
            order[1],
            order[2],
            col,
            min(yrs_filtered),
            max(yrs_filtered),
        )
        return df_result, True, f"ARIMA({order[0]},{order[1]},{order[2]})"

    except (ValueError, TypeError) as e:
        logger.warning("ARIMA failed for %s, error: %s", col, str(e))
        return df_result, False, f"ARIMA failed: {e!s}"
