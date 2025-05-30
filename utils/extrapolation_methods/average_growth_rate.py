"""Average growth rate extrapolation method for time series data.

This module provides functionality to extrapolate time series using average growth rates.
It calculates the average growth rate from historical data and applies it to project future values.
"""

import logging
from dataclasses import dataclass

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class AvgGrowthRateConfig:
    """Configuration for average growth rate extrapolation."""

    lookback_years: int = 4
    default_growth: float = 0.03
    min_data_points: int = 2


def extrapolate_with_average_growth_rate(  # pylint: disable=too-many-locals
    df: pd.DataFrame,
    col: str,
    years_to_project: list[int],
    config: AvgGrowthRateConfig | None = None,
) -> tuple[pd.DataFrame, bool, str]:
    """Extrapolate a time series using average historical growth rate.

    Args:
        df (pd.DataFrame): DataFrame containing the time series data
        col (str): Column name of the series to extrapolate
        years_to_project (list): List of years to project values for
        config (AvgGrowthRateConfig | None): Configuration for the extrapolation method
            (default: None, which uses the default configuration)

    Returns:
        tuple: (updated_df, success, method_info)
            - updated_df: DataFrame with extrapolated values
            - success: Boolean indicating if the projection was successful
            - method_info: String describing the method used
    """
    df_result = df.copy()
    success = False
    method_info = "Initialization failed"
    growth_percent_for_info = 0.0  # For final method_info string

    if config is None:
        config = AvgGrowthRateConfig()

    if col not in df_result.columns or df_result[col].isna().all():
        method_info = "No data"
        return df_result, success, method_info  # Early exit 1

    historical = df_result[["year", col]].dropna()

    if len(historical) < config.min_data_points:
        method_info = f"Insufficient data (need {config.min_data_points}, have {len(historical)})"
        if len(historical) == 1:
            last_year_hist = int(historical["year"].max())
            last_value_hist = historical[historical["year"] == last_year_hist][col].to_numpy()[0]
            yrs_to_proj_default = [y for y in years_to_project if y > last_year_hist]

            if not yrs_to_proj_default:
                method_info = "No years to project with default growth"
            else:
                for _i, year_val in enumerate(yrs_to_proj_default):
                    exponent = year_val - last_year_hist
                    base = 1 + config.default_growth
                    projected_val_default = last_value_hist * (base**exponent)
                    df_result.loc[df_result.year == year_val, col] = round(projected_val_default, 4)
                logger.info(
                    "Applied default growth rate of %.2f%% to %s",
                    config.default_growth * 100,
                    col,
                )
                success = True
                method_info = f"Default growth rate ({config.default_growth:.2%})"
        return df_result, success, method_info  # Early exit 2 & 3 (consolidated)

    last_year = int(historical["year"].max())
    last_value = historical[historical["year"] == last_year][col].to_numpy()[0]
    yrs = [y for y in years_to_project if y > last_year]

    if not yrs:
        method_info = "No years to project (data already up to date or beyond requested years)"
        # Consider success=True if data is already current, but Pylint wants fewer returns.
        # For now, let's keep success=False to match original logic of this specific return path.
        return df_result, success, method_info  # Early exit 4

    try:
        n_years = min(config.lookback_years, len(historical))
        historical_sorted = historical.sort_values("year")
        last_years_data = historical_sorted[col].iloc[-n_years:].to_numpy()
        growth_rates = [
            (last_years_data[i] / last_years_data[i - 1]) - 1
            for i in range(1, len(last_years_data))
        ]
        avg_growth = (
            sum(growth_rates) / len(growth_rates) if growth_rates else config.default_growth
        )

        for _i, year_val_main in enumerate(yrs):
            exponent_main = year_val_main - last_year
            base_main = 1 + avg_growth
            projected_value_main = last_value * (base_main**exponent_main)
            df_result.loc[df_result.year == year_val_main, col] = round(projected_value_main, 4)

        growth_percent_for_info = avg_growth * 100
        logger.info(
            "Applied average growth rate of %.2f%% to %s using %d historical periods",
            growth_percent_for_info,
            col,
            len(growth_rates),
        )
        success = True
        method_info = f"Average growth rate ({growth_percent_for_info:.2f}%)"

    except (ValueError, TypeError, ZeroDivisionError) as e:
        logger.warning("Average growth rate calculation failed for %s, error: %s", col, str(e))
        method_info = f"Average growth rate failed: {e!s}"
        # success remains False

    return df_result, success, method_info  # Final common return point
