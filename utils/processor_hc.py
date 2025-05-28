"""Human capital projection module.

This module provides functions for projecting human capital values to future years
using various statistical methods.
"""

import pandas as pd

from .processor_hc_helpers import (
    MIN_DATA_POINTS_FOR_REGRESSION,
    HumanCapitalError,
    _check_for_alternative_columns,
    _create_placeholder_dataframe,
    _log_data_quality_info,
    _project_with_fallback_methods,
    _try_growth_rate_projection,
    _try_last_value_projection,
    _try_linear_regression_projection,
    _validate_input_data,
    logger,
)


def _prepare_hc_data(processed_data: pd.DataFrame, end_year: int) -> pd.DataFrame | None:
    """Prepare and validate human capital data for projection."""
    try:
        _validate_input_data(processed_data)
        logger.info("Data contains %s rows and %s columns", processed_data.shape[0], processed_data.shape[1])
        logger.debug("Available columns in data: %s", processed_data.columns.tolist())
    except HumanCapitalError:
        logger.info("Returning empty DataFrame due to validation failure")
        return _create_placeholder_dataframe(end_year)
    except (KeyError, ValueError, AttributeError):
        logger.exception("Failed to validate input data")
        return _create_placeholder_dataframe(end_year)

    if "hc" not in processed_data.columns:
        logger.warning("Human capital (hc) column not found in the data")
        _check_for_alternative_columns(processed_data)
        return _create_placeholder_dataframe(end_year)

    return None  # Indicates successful preparation


def _analyze_hc_data(hc_data: pd.DataFrame, end_year: int) -> tuple[pd.DataFrame, list[int]] | None:
    """Analyze human capital data and determine projection requirements."""
    _log_data_quality_info(hc_data)

    hc_data_not_na = hc_data.dropna(subset=["hc"])
    if len(hc_data_not_na) == 0:
        logger.warning("No non-NA human capital data available for projection")
        return hc_data, []

    last_year_with_data = hc_data_not_na["year"].max()
    first_year_with_data = hc_data_not_na["year"].min()
    logger.info("Human capital data available from %s to %s", first_year_with_data, last_year_with_data)

    if last_year_with_data >= end_year:
        logger.info("No projection needed - data already available up to %s", last_year_with_data)
        return hc_data, []

    years_to_project = list(range(int(last_year_with_data) + 1, end_year + 1))
    if not years_to_project:
        logger.info("No years to project")
        return hc_data, []

    logger.info(
        "Will project human capital for %s years: %s to %s",
        len(years_to_project),
        min(years_to_project),
        max(years_to_project),
    )

    return hc_data_not_na, years_to_project


def _execute_projection_methods(hc_data: pd.DataFrame, years_to_project: list[int]) -> pd.DataFrame:
    """Execute projection methods in order of preference."""
    # Try linear regression as primary method
    updated_df, success = _try_linear_regression_projection(hc_data, years_to_project)
    if success:
        return updated_df

    # Try average growth rate with a small lookback period (trend extrapolation)
    updated_df, success = _try_growth_rate_projection(hc_data, years_to_project)
    if success:
        return updated_df

    # Last resort: just copy the last available value (using growth rate of 0)
    updated_df, success = _try_last_value_projection(hc_data, years_to_project)
    if success:
        return updated_df

    logger.warning("All projection methods failed, returning original data")
    return hc_data


def project_human_capital(processed_data: pd.DataFrame, end_year: int = 2025) -> pd.DataFrame:
    """Project human capital values to a specified end year using linear regression."""
    logger.info("Projecting human capital to year %s", end_year)

    # Prepare and validate data
    placeholder = _prepare_hc_data(processed_data, end_year)
    if placeholder is not None:
        return placeholder

    try:
        # Extract human capital data
        logger.info("Extracting human capital data")
        hc_data = processed_data[["year", "hc"]].copy()

        # Analyze data and determine projection requirements
        analysis_result = _analyze_hc_data(hc_data, end_year)
        if analysis_result is None:
            return hc_data

        hc_data_not_na, years_to_project = analysis_result
        if not years_to_project:
            return hc_data

        # Check if we have enough data for regression
        if len(hc_data_not_na) < MIN_DATA_POINTS_FOR_REGRESSION:
            logger.warning("Insufficient data for regression (only %s points)", len(hc_data_not_na))
            return _project_with_fallback_methods(hc_data, years_to_project)

        # Execute projection methods
        return _execute_projection_methods(hc_data, years_to_project)

    except (KeyError, ValueError, AttributeError):
        logger.exception("Unexpected error projecting human capital")
        return hc_data
