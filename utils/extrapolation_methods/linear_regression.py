"""Linear regression-based extrapolation method for time series data.

This module provides functionality to extrapolate time series using linear regression.
It fits a linear trend to historical data and projects it forward.
"""

import logging

import pandas as pd
from sklearn.linear_model import LinearRegression

from config import Config

from .extrapolation_helpers import ExtrapolationPrepResult, prepare_extrapolation_data

logger = logging.getLogger(__name__)


def extrapolate_with_linear_regression(
    df: pd.DataFrame,
    col: str,
    years_to_project: list[int],
    min_data_points: int = Config.MIN_DATA_POINTS_FOR_REGRESSION,
) -> tuple[pd.DataFrame, bool, str]:
    """Extrapolate a time series using linear regression.

    Args:
        df (pd.DataFrame): DataFrame containing the time series data
        col (str): Column name of the series to extrapolate
        years_to_project (list): List of years to project values for
        min_data_points (int): Minimum number of data points required (default: from Config)

    Returns:
        tuple: (updated_df, success, method_info)
            - updated_df: DataFrame with extrapolated values
            - success: Boolean indicating if the projection was successful
            - method_info: String describing the method used
    """
    prep_result: ExtrapolationPrepResult = prepare_extrapolation_data(
        df, col, years_to_project, min_data_points, "Linear regression"
    )
    if not prep_result.success:
        return prep_result.df_result, False, prep_result.message

    if prep_result.historical_data is None or prep_result.years_to_project_filtered is None:
        return prep_result.df_result, False, "Preparation failed unexpectedly"

    df_result = prep_result.df_result
    historical = prep_result.historical_data
    yrs_filtered = prep_result.years_to_project_filtered

    try:
        # Prepare data for linear regression
        x_values = historical["year"].to_numpy().reshape(-1, 1)
        y_values = historical[col].to_numpy()

        # Fit linear regression model
        model = LinearRegression()
        model.fit(x_values, y_values)

        # Generate predictions for future years
        for year in yrs_filtered:
            pred = model.predict([[year]])[0]
            # Ensure predictions are non-negative and rounded appropriately
            df_result.loc[df_result.year == year, col] = round(
                max(0, pred), Config.DECIMAL_PLACES_PROJECTIONS
            )

        logger.info(
            "Applied linear regression to %s for years %d-%d",
            col,
            min(yrs_filtered),
            max(yrs_filtered),
        )
    except (ValueError, TypeError) as e:
        logger.warning("Linear regression failed for %s, error: %s", col, str(e))
        return df_result, False, f"Linear regression failed: {e!s}"

    return df_result, True, "Linear regression"
