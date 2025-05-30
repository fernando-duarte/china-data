"""Methods for applying extrapolation techniques."""

from typing import Any

import pandas as pd

from utils.extrapolation_methods import (
    AvgGrowthRateConfig,
    extrapolate_with_arima,
    extrapolate_with_average_growth_rate,
    extrapolate_with_linear_regression,
)

from .processor_extrapolation_constants import MIN_HISTORICAL_DATA_POINTS


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
    default_growth = 0.03
    lookback = 4

    config = AvgGrowthRateConfig(
        lookback_years=lookback,
        default_growth=default_growth,
        min_data_points=MIN_HISTORICAL_DATA_POINTS,
    )

    updated_df, success, method = extrapolate_with_average_growth_rate(
        data_df, col, years_to_project, config=config
    )
    if success:
        info[col] = {"method": method, "years": years_to_project}
        return updated_df, info, True
    return data_df, info, False


def _apply_methods(
    data_df: pd.DataFrame, years_to_add: list[int], cols: list[str], info: dict[str, Any]
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Apply appropriate extrapolation methods to each column based on column type."""
    gdp_columns = [
        "GDP_USD_bn",
        "C_USD_bn",
        "G_USD_bn",
        "I_USD_bn",
        "X_USD_bn",
        "M_USD_bn",
        "NX_USD_bn",
    ]
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

        success = False

        if col in gdp_columns:
            data_df, info, success = _apply_gdp_extrapolation(data_df, col, years_to_project, info)
            if success:
                continue

        if col in {*demographic_columns, *human_capital_columns} and not success:
            data_df, info, success = _apply_demographic_extrapolation(
                data_df, col, years_to_project, info
            )
            if success:
                continue

        if not success:
            data_df, info, success = _apply_fallback_extrapolation(
                data_df, col, years_to_project, info
            )

    return data_df, info
