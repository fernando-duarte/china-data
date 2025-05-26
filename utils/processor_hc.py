"""Human capital projection module.

This module provides functions for projecting human capital values to future years
using various statistical methods.
"""

import logging

import numpy as np
import pandas as pd

from utils.extrapolation_methods import extrapolate_with_average_growth_rate, extrapolate_with_linear_regression

logger = logging.getLogger(__name__)

# Constants
MIN_DATA_POINTS_FOR_REGRESSION = 2
MAX_REASONABLE_HC_VALUE = 5
DEFAULT_HC_GROWTH_RATE = 0.01
FALLBACK_LOOKBACK_YEARS = 2


class HumanCapitalError(Exception):
    """Custom exception for human capital processing errors."""


def _validate_input_data(processed_data: pd.DataFrame) -> None:
    """Validate input data for human capital projection.

    Args:
        processed_data: Input DataFrame to validate

    Raises:
        HumanCapitalError: If validation fails
    """
    if not isinstance(processed_data, pd.DataFrame):
        msg = "Input data must be a pandas DataFrame"
        logger.error("Input data is not a pandas DataFrame")
        raise HumanCapitalError(msg)

    if "year" not in processed_data.columns:
        msg = "Input data must contain a 'year' column"
        logger.error("Year column missing from input data")
        raise HumanCapitalError(msg)


def _log_data_quality_info(hc_data: pd.DataFrame) -> None:
    """Log information about data quality and characteristics."""
    total_rows = hc_data.shape[0]
    non_na_rows = hc_data.dropna(subset=["hc"]).shape[0]
    na_percentage = (total_rows - non_na_rows) / total_rows * 100 if total_rows > 0 else 0

    logger.info(
        "Human capital data: %s total rows, %s non-NA rows (%.1f%% missing)",
        total_rows,
        non_na_rows,
        na_percentage,
    )

    if non_na_rows > 0:
        min_hc = hc_data["hc"].min()
        max_hc = hc_data["hc"].max()
        logger.info("Human capital range: %s to %s", min_hc, max_hc)

        if min_hc < 0:
            logger.warning("Found negative human capital values (min=%s)", min_hc)

        if max_hc > MAX_REASONABLE_HC_VALUE:
            logger.warning("Unusually high human capital values detected (max=%s)", max_hc)

        # Sample data for debugging
        sample = hc_data.dropna(subset=["hc"]).head(3)
        logger.debug("Sample human capital values:\n%s", sample)


def _create_placeholder_dataframe(end_year: int) -> pd.DataFrame:
    """Create a placeholder DataFrame with years and NaN values for human capital."""
    logger.info("Creating placeholder DataFrame with years from 1960 to %s", end_year)
    return pd.DataFrame({"year": range(1960, end_year + 1), "hc": np.nan})


def _check_for_alternative_columns(processed_data: pd.DataFrame) -> None:
    """Check for alternative human capital columns and log findings."""
    pwt_cols = [col for col in processed_data.columns if col.startswith("PWT") or col.lower().startswith("pwt")]
    if pwt_cols:
        logger.info("Found potential human capital columns: %s", pwt_cols)


def _ensure_years_exist(hc_data: pd.DataFrame, years_to_project: list[int]) -> pd.DataFrame:
    """Ensure all required years exist in the DataFrame."""
    for year in years_to_project:
        if year not in hc_data["year"].to_numpy():
            hc_data = pd.concat([hc_data, pd.DataFrame({"year": [year], "hc": [np.nan]})], ignore_index=True)
    return hc_data


def _try_linear_regression_projection(hc_data: pd.DataFrame, years_to_project: list[int]) -> tuple[pd.DataFrame, bool]:
    """Try to project human capital using linear regression."""
    updated_df, success, method = extrapolate_with_linear_regression(
        hc_data, "hc", years_to_project, min_data_points=MIN_DATA_POINTS_FOR_REGRESSION
    )

    if success:
        logger.info("Successfully projected human capital using %s", method)
        return updated_df, True

    logger.error("Linear regression failed: %s", method)
    return hc_data, False


def _try_growth_rate_projection(hc_data: pd.DataFrame, years_to_project: list[int]) -> tuple[pd.DataFrame, bool]:
    """Try to project human capital using average growth rate."""
    updated_df, success, method = extrapolate_with_average_growth_rate(
        hc_data, "hc", years_to_project, lookback_years=FALLBACK_LOOKBACK_YEARS, default_growth=DEFAULT_HC_GROWTH_RATE
    )

    if success:
        logger.info("Successfully projected human capital using %s", method)
        return updated_df, True

    logger.error("Growth trend extrapolation failed: %s", method)
    return hc_data, False


def _try_last_value_projection(hc_data: pd.DataFrame, years_to_project: list[int]) -> tuple[pd.DataFrame, bool]:
    """Try to project human capital using last value carry-forward."""
    updated_df, success, method = extrapolate_with_average_growth_rate(
        hc_data, "hc", years_to_project, default_growth=0.0, min_data_points=1
    )

    if success:
        logger.info("Successfully projected human capital using %s", method)
        return updated_df, True

    logger.error("Last value carry-forward failed: %s", method)
    return hc_data, False


def _project_with_fallback_methods(hc_data: pd.DataFrame, years_to_project: list[int]) -> pd.DataFrame:
    """Project human capital using fallback methods when insufficient data for regression."""
    if len(hc_data.dropna(subset=["hc"])) > 0:
        logger.info("Falling back to last value carry-forward due to insufficient data points")

        # Ensure all years exist in the dataframe
        hc_data = _ensure_years_exist(hc_data, years_to_project)

        # Use average growth rate with 0 growth (equivalent to last value carry-forward)
        updated_df, success = _try_last_value_projection(hc_data, years_to_project)
        if success:
            return updated_df

    return hc_data


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
    """Project human capital values to a specified end year using linear regression.

    Parameters:
    -----------
    processed_data : pandas DataFrame
        Data containing at least 'year' and possibly 'hc' columns
    end_year : int, default=2025
        The final year to project human capital values to

    Returns:
    --------
    pandas DataFrame
        DataFrame with years and human capital values, including projections to end_year
    """
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
