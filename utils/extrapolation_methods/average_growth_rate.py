"""Average growth rate extrapolation method for time series data.

This module provides functionality to extrapolate time series using average growth rates.
It calculates the average growth rate from historical data and applies it to project future values.
"""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def extrapolate_with_average_growth_rate(
    df: pd.DataFrame,
    col: str,
    years_to_project: list[int],
    *,
    lookback_years: int = 4,
    default_growth: float = 0.03,
    min_data_points: int = 2,
) -> tuple[pd.DataFrame, bool, str]:
    """Extrapolate a time series using average historical growth rate.

    Args:
        df (pd.DataFrame): DataFrame containing the time series data
        col (str): Column name of the series to extrapolate
        years_to_project (list): List of years to project values for
        lookback_years (int): Maximum number of years to look back for calculating growth rate (default: 4)
        default_growth (float): Default growth rate to use if historical data is insufficient (default: 0.03)
        min_data_points (int): Minimum number of data points required (default: 2)

    Returns:
        tuple: (updated_df, success, method_info)
            - updated_df: DataFrame with extrapolated values
            - success: Boolean indicating if the projection was successful
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
        logger.info(
            "Insufficient data for average growth rate on %s (need %d, have %d)", col, min_data_points, len(historical)
        )
        # If we have at least 1 data point, we can still use the default growth rate
        if len(historical) == 1:
            last_year = int(historical["year"].max())
            last_value = historical[historical["year"] == last_year][col].to_numpy()[0]

            # Filter years to actually project
            yrs = [y for y in years_to_project if y > last_year]
            if not yrs:
                return df_result, False, "No years to project"

            # Apply default growth rate from the last known value
            for _i, year in enumerate(yrs):
                projected_value = last_value * (1 + default_growth) ** (year - last_year)
                df_result.loc[df_result.year == year, col] = round(projected_value, 4)

            logger.info("Applied default growth rate of %.2f%% to %s", default_growth * 100, col)
            return df_result, True, f"Default growth rate ({default_growth:.2%})"

        return df_result, False, f"Insufficient data (need {min_data_points})"

    # Get the last observed year and value
    last_year = int(historical["year"].max())
    last_value = historical[historical["year"] == last_year][col].to_numpy()[0]

    # Filter years to actually project (might be fewer than requested if some already exist)
    yrs = [y for y in years_to_project if y > last_year]
    if not yrs:
        return df_result, False, "No years to project"

    try:
        # Determine how many years of data to use for calculating average growth rate
        n_years = min(lookback_years, len(historical))

        # Sort by year and get the last n_years of data
        historical_sorted = historical.sort_values("year")
        last_years = historical_sorted[col].iloc[-n_years:].to_numpy()

        # Calculate year-over-year growth rates
        growth_rates = [(last_years[i] / last_years[i - 1]) - 1 for i in range(1, len(last_years))]

        # Calculate average growth rate, using default if no growth rates are available
        avg_growth = sum(growth_rates) / len(growth_rates) if growth_rates else default_growth

        # Generate projections using compound growth formula
        for _i, year in enumerate(yrs):
            projected_value = last_value * (1 + avg_growth) ** (year - last_year)
            df_result.loc[df_result.year == year, col] = round(projected_value, 4)

        # Report the average growth rate used
        growth_percent = avg_growth * 100
        logger.info(
            "Applied average growth rate of %.2f%% to %s using %d historical periods",
            growth_percent,
            col,
            len(growth_rates),
        )

    except (ValueError, TypeError, ZeroDivisionError) as e:
        logger.warning("Average growth rate calculation failed for %s, error: %s", col, str(e))
        return df_result, False, f"Average growth rate failed: {e!s}"

    return df_result, True, f"Average growth rate ({growth_percent:.2f}%)"
