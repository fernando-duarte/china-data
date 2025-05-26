import logging
from typing import Any

import numpy as np
import pandas as pd

from config import Config
from utils.extrapolation_methods import (
    extrapolate_with_arima,
    extrapolate_with_average_growth_rate,
    extrapolate_with_linear_regression,
)

logger = logging.getLogger(__name__)

# Constants for magic numbers
MIN_HISTORICAL_DATA_POINTS = 2
DEFAULT_LOOKBACK_YEARS = 5


def _prepare(data_df: pd.DataFrame, end_year: int) -> tuple[pd.DataFrame, dict[str, Any], list[int], list[str]]:
    """Prepare data for extrapolation by adding missing years and identifying columns to extrapolate."""
    max_year = data_df.year.max()
    if max_year >= end_year:
        missing = False
        key = ["GDP_USD_bn", "C_USD_bn", "G_USD_bn", "I_USD_bn", "X_USD_bn", "M_USD_bn", "POP_mn", "LF_mn"]
        for year in [end_year - 1, end_year]:
            for var in key:
                if var in data_df.columns and pd.isna(data_df.loc[data_df.year == year, var].to_numpy()[0]):
                    missing = True
                    break
            if missing:
                break
        if not missing:
            return data_df, {}, [], []
        years_to_add = [end_year - 1, end_year]
    else:
        years_to_add = list(range(max_year + 1, end_year + 1))
    new_years_df = pd.DataFrame({"year": years_to_add})
    updated_df = pd.concat([data_df, new_years_df], ignore_index=True)
    numeric_cols = updated_df.select_dtypes(include=[np.number]).columns.tolist()
    cols_to_extrapolate = [c for c in numeric_cols if c != "year"]
    return updated_df, {}, years_to_add, cols_to_extrapolate


def _apply_gdp_extrapolation(
    data_df: pd.DataFrame, col: str, years_to_project: list[int], info: dict[str, Any]
) -> tuple[pd.DataFrame, dict[str, Any], bool]:
    """Apply ARIMA extrapolation for GDP-related columns."""
    updated_df, success, method = extrapolate_with_arima(
        data_df, col, years_to_project, min_data_points=5, order=(1, 1, 1)
    )
    if success:
        info[col] = {"method": method, "years": years_to_project}
        return updated_df, info, True
    return data_df, info, False


def _apply_demographic_extrapolation(
    data_df: pd.DataFrame, col: str, years_to_project: list[int], info: dict[str, Any]
) -> tuple[pd.DataFrame, dict[str, Any], bool]:
    """Apply linear regression extrapolation for demographic and human capital columns."""
    updated_df, success, method = extrapolate_with_linear_regression(
        data_df, col, years_to_project, min_data_points=MIN_HISTORICAL_DATA_POINTS
    )
    if success:
        info[col] = {"method": method, "years": years_to_project}
        return updated_df, info, True
    return data_df, info, False


def _apply_fallback_extrapolation(
    data_df: pd.DataFrame, col: str, years_to_project: list[int], info: dict[str, Any]
) -> tuple[pd.DataFrame, dict[str, Any], bool]:
    """Apply average growth rate extrapolation as fallback method."""
    default_growth = 0.03  # Default for most series
    lookback = 4  # Default lookback period

    updated_df, success, method = extrapolate_with_average_growth_rate(
        data_df, col, years_to_project, lookback_years=lookback, default_growth=default_growth
    )
    if success:
        info[col] = {"method": method, "years": years_to_project}
        return updated_df, info, True
    return data_df, info, False


def _apply_methods(
    data_df: pd.DataFrame, years_to_add: list[int], cols: list[str], info: dict[str, Any]
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Apply appropriate extrapolation methods to each column based on column type.

    Args:
        data_df: DataFrame containing the data
        years_to_add: List of years to add projections for
        cols: List of columns to extrapolate
        info: Dictionary to store extrapolation method information

    Returns:
        tuple: (updated DataFrame, updated info dictionary)
    """
    gdp_columns = ["GDP_USD_bn", "C_USD_bn", "G_USD_bn", "I_USD_bn", "X_USD_bn", "M_USD_bn", "NX_USD_bn"]
    demographic_columns = ["POP_mn", "LF_mn"]
    human_capital_columns = ["hc"]

    for col in cols:
        if data_df[col].isna().all():
            continue

        historical = data_df[["year", col]].dropna()
        if len(historical) == 0:
            continue

        last_year = int(historical["year"].max())
        years_to_project = list(range(last_year + 1, years_to_add[-1] + 1))
        if not years_to_project:
            continue

        # Try different methods based on column type
        success = False

        # For GDP-related columns, try ARIMA first
        if col in gdp_columns:
            data_df, info, success = _apply_gdp_extrapolation(data_df, col, years_to_project, info)
            if success:
                continue

        # For demographic and human capital columns, try linear regression
        if col in {*demographic_columns, *human_capital_columns} and not success:
            data_df, info, success = _apply_demographic_extrapolation(data_df, col, years_to_project, info)
            if success:
                continue

        # Fall back to average growth rate for all other cases
        if not success:
            data_df, info, success = _apply_fallback_extrapolation(data_df, col, years_to_project, info)

    return data_df, info


def _get_default_growth_rate(col: str) -> float:
    """Get default growth rate for a specific column."""
    if col in ["GDP_USD_bn", "C_USD_bn", "G_USD_bn", "I_USD_bn", "X_USD_bn", "M_USD_bn"]:
        return Config.DEFAULT_GROWTH_RATE
    if col == "POP_mn":
        return 0.005
    if col in {"LF_mn", "hc"}:
        return 0.01
    if col == "K_USD_bn":
        return 0.04
    return 0.03


def _calculate_historical_growth(historical_data: pd.DataFrame, col: str) -> float:
    """Calculate average historical growth rate for a column."""
    if len(historical_data) >= MIN_HISTORICAL_DATA_POINTS:
        n_years = min(DEFAULT_LOOKBACK_YEARS, len(historical_data))
        last_years = historical_data.iloc[-n_years:][col].to_numpy()
        if len(last_years) > 1:
            growth_rates = [(last_years[i] / last_years[i - 1]) - 1 for i in range(1, len(last_years))]
            return float(sum(growth_rates) / len(growth_rates))
    return _get_default_growth_rate(col)


def _fill_missing_key_variables(data_df: pd.DataFrame, years_to_add: list[int]) -> pd.DataFrame:
    """Fill missing values for key variables using growth-based extrapolation."""
    key_vars = [
        "GDP_USD_bn",
        "C_USD_bn",
        "G_USD_bn",
        "I_USD_bn",
        "X_USD_bn",
        "M_USD_bn",
        "POP_mn",
        "LF_mn",
        "FDI_pct_GDP",
        "TAX_pct_GDP",
        "hc",
        "K_USD_bn",
    ]

    for year in years_to_add:
        for col in key_vars:
            if col in data_df.columns and pd.isna(data_df.loc[data_df.year == year, col].to_numpy()[0]):
                last_valid = data_df[data_df.year < year][[col]].dropna()
                if len(last_valid) > 0:
                    last_value = last_valid.iloc[-1][col].to_numpy()[0]
                    last_year = data_df.loc[last_valid.index[-1], "year"]

                    historical_data = data_df[data_df.year <= data_df.year.max()][[col]].dropna()
                    avg_growth = _calculate_historical_growth(historical_data, col)

                    projected_value = last_value * (1 + avg_growth) ** (year - last_year)
                    data_df.loc[data_df.year == year, col] = round(projected_value, 4)

    return data_df


def _finalize(
    data_df: pd.DataFrame,
    years_to_add: list[int],
    raw_data: pd.DataFrame,
    cols: list[str],
    info: dict[str, Any],
    *,
    end_year: int,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Finalize extrapolation by filling missing key variables and updating metadata."""
    # Fill missing key variables
    data_df = _fill_missing_key_variables(data_df, years_to_add)

    # Update extrapolation info for all columns
    for col in cols:
        if col in raw_data.columns:
            raw_non_nan = raw_data[["year", col]].dropna()
            if len(raw_non_nan) == 0:
                continue
            last_actual_year = int(raw_non_nan["year"].max())
        else:
            hist = data_df[["year", col]].dropna()
            if len(hist) == 0:
                continue
            last_actual_year = int(hist["year"].max())

        if last_actual_year < end_year:
            extrap_years = list(range(last_actual_year + 1, end_year + 1))
            if extrap_years:
                method = info.get(col, {}).get("method", "Extrapolated")
                info[col] = {"method": method, "years": extrap_years}

    return data_df, info


def extrapolate_series_to_end_year(
    data: pd.DataFrame, end_year: int = 2025, raw_data: pd.DataFrame | None = None
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Extrapolate time series data to the specified end year.

    Args:
        data: DataFrame containing the data to extrapolate
        end_year: Target year for extrapolation
        raw_data: Optional raw data for reference

    Returns:
        Tuple of (extrapolated DataFrame, extrapolation info dictionary)
    """
    data_df, info, years_to_add, cols = _prepare(data.copy(), end_year)
    if not years_to_add and not info:
        return data_df, info
    data_df, info = _apply_methods(data_df, years_to_add, cols, info)
    data_df, info = _finalize(
        data_df, years_to_add, raw_data if raw_data is not None else data, cols, info, end_year=end_year
    )
    return data_df, info
