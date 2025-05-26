"""Capital stock calculation module.

This module provides functions for calculating capital stock based on Penn World Table data
and a specified capital-output ratio.
"""

import logging

import numpy as np
import pandas as pd

from config import Config

logger = logging.getLogger(__name__)


def _validate_input_data(raw_data: pd.DataFrame) -> tuple[bool, str]:
    """Validate input data for capital stock calculation.

    Args:
        raw_data: DataFrame to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(raw_data, pd.DataFrame):
        return False, "Invalid input type: raw_data must be a pandas DataFrame"

    if "year" not in raw_data.columns:
        return False, "Critical: 'year' column missing from input data"

    return True, ""


def _check_required_columns(capital_data: pd.DataFrame) -> list[str]:
    """Check for required columns and log alternatives if missing.

    Args:
        capital_data: DataFrame to check

    Returns:
        List of missing required columns
    """
    required_columns = ["rkna", "pl_gdpo", "cgdpo_bn"]
    missing_columns = [col for col in required_columns if col not in capital_data.columns]

    if missing_columns:
        logger.warning("Missing required columns for capital stock calculation: %s", missing_columns)

        # Look for alternative columns that might contain the required data
        pwt_cols = [col for col in capital_data.columns if col.startswith("PWT") or col.lower().startswith("pwt")]
        if pwt_cols:
            logger.info("Found PWT columns that might contain needed data: %s", pwt_cols)
            # Try to map PWT columns to required columns
            for col in pwt_cols:
                for req_col in missing_columns:
                    if req_col.lower() in col.lower():
                        logger.info("Potential match: '%s' might contain '%s' data", col, req_col)

    return missing_columns


def _find_baseline_year(capital_data: pd.DataFrame) -> int:
    """Find the best baseline year for capital stock calculation.

    Args:
        capital_data: DataFrame with year data

    Returns:
        Baseline year to use

    Raises:
        ValueError: If no suitable baseline year is found
    """
    baseline_year = Config.BASELINE_YEAR
    if baseline_year in capital_data["year"].to_numpy():
        return baseline_year

    logger.warning("Missing %d data for capital stock calculation", baseline_year)

    years_available = sorted(capital_data["year"].unique())
    logger.info("Available years: %d to %d", min(years_available), max(years_available))

    # Try to find an alternative baseline year (closest to 2017)
    alt_years = [y for y in years_available if Config.BASELINE_YEAR_RANGE_MIN <= y <= Config.BASELINE_YEAR_RANGE_MAX]
    if alt_years:
        # Choose closest year to 2017
        baseline_year = min(alt_years, key=lambda y: abs(y - Config.BASELINE_YEAR))
        logger.info("Using alternative baseline year: %d", baseline_year)
        return baseline_year

    msg = "No suitable baseline year found in range 2010-2020"
    raise ValueError(msg)


def _get_baseline_value(capital_data: pd.DataFrame, year: int, column: str) -> float:
    """Get baseline value for a specific column and year.

    Args:
        capital_data: DataFrame with data
        year: Year to get data for
        column: Column name to extract

    Returns:
        Baseline value

    Raises:
        ValueError: If no data is found for the specified year and column
    """
    baseline_rows = capital_data.loc[capital_data.year == year, column]
    if len(baseline_rows) == 0 or pd.isna(baseline_rows.iloc[0]):
        error_msg = f"No {column} data for {year}"
        raise ValueError(error_msg)
    return float(baseline_rows.iloc[0])


def _calculate_capital_for_year(
    year: int,
    rkna_value: float,
    pl_gdpo_value: float,
    *,
    rkna_baseline: float,
    pl_gdpo_baseline: float,
    k_baseline_usd: float,
) -> float:
    """Calculate capital stock for a specific year.

    Args:
        year: Year being calculated
        rkna_value: Real capital stock value for the year
        pl_gdpo_value: Price level value for the year
        rkna_baseline: Baseline real capital stock
        pl_gdpo_baseline: Baseline price level
        k_baseline_usd: Baseline capital in USD

    Returns:
        Capital stock in USD billions
    """
    if pd.isna(rkna_value) or pd.isna(pl_gdpo_value):
        logger.debug("Missing required data for year %d", year)
        return np.nan

    # Calculate capital in USD
    return (rkna_value / rkna_baseline) * (pl_gdpo_value / pl_gdpo_baseline) * k_baseline_usd


def _log_calculation_summary(capital_data: pd.DataFrame) -> None:
    """Log summary statistics for capital stock calculation.

    Args:
        capital_data: DataFrame with calculated capital stock
    """
    k_data = capital_data.dropna(subset=["K_USD_bn"])
    logger.info("Calculated capital stock for %d years", k_data.shape[0])

    if len(k_data) > 0:
        min_k = k_data["K_USD_bn"].min()
        max_k = k_data["K_USD_bn"].max()
        logger.info("Capital stock range: %.2f to %.2f billion USD", min_k, max_k)


def calculate_capital_stock(
    raw_data: pd.DataFrame, capital_output_ratio: float = Config.DEFAULT_CAPITAL_OUTPUT_RATIO
) -> pd.DataFrame:
    """Calculate capital stock using PWT data and capital-output ratio.

    This function calculates physical capital stock based on Penn World Table data
    using relative real capital stock and price level indices, normalized to a
    baseline year (2017), and calibrated with a capital-output ratio.

    Args:
        raw_data: DataFrame with PWT data including rkna, pl_gdpo, and cgdpo columns
        capital_output_ratio: Capital-output ratio to use (default from Config)

    Returns:
        DataFrame with K_USD_bn column added (capital stock in billions of USD)
    """
    logger.info("Calculating capital stock using K/Y ratio = %f", capital_output_ratio)

    # Validate input
    is_valid, error_msg = _validate_input_data(raw_data)
    if not is_valid:
        logger.error(error_msg)
        return pd.DataFrame({"year": [], "K_USD_bn": []})

    # Create a copy to avoid modifying the original
    capital_data = raw_data.copy()

    # Log available columns for debugging
    logger.debug("Available columns for capital stock calculation: %s", capital_data.columns.tolist())

    # Check for required columns
    missing_columns = _check_required_columns(capital_data)
    if missing_columns:
        # Create empty K_USD_bn column
        logger.info("Adding empty K_USD_bn column due to missing data")
        capital_data["K_USD_bn"] = np.nan
        return capital_data

    try:
        # Find baseline year
        baseline_year = _find_baseline_year(capital_data)
        logger.info("Using %d as baseline year for capital stock calculation", baseline_year)

        # Get baseline values
        gdp_baseline = _get_baseline_value(capital_data, baseline_year, "cgdpo_bn")
        rkna_baseline = _get_baseline_value(capital_data, baseline_year, "rkna")
        pl_gdpo_baseline = _get_baseline_value(capital_data, baseline_year, "pl_gdpo")

        # Calculate capital in baseline constant USD (billions)
        k_baseline_usd = gdp_baseline * capital_output_ratio
        logger.info("Baseline year (%d) GDP: %.2f billion USD", baseline_year, gdp_baseline)
        logger.info("Baseline year (%d) calculated capital: %.2f billion USD", baseline_year, k_baseline_usd)

        # Calculate capital stock for all years
        capital_data["K_USD_bn"] = np.nan  # Initialize with NaN

        # Calculate capital stock for each year with data
        for _, row in capital_data.iterrows():
            year = row["year"]
            rkna_value = row["rkna"]
            pl_gdpo_value = row["pl_gdpo"]

            try:
                k_usd = _calculate_capital_for_year(
                    year,
                    rkna_value,
                    pl_gdpo_value,
                    rkna_baseline=rkna_baseline,
                    pl_gdpo_baseline=pl_gdpo_baseline,
                    k_baseline_usd=k_baseline_usd,
                )

                if not pd.isna(k_usd):
                    capital_data.loc[capital_data.year == year, "K_USD_bn"] = k_usd

            except (ValueError, TypeError) as e:
                logger.warning("Error calculating capital for year %s: %s", row.get("year", "?"), str(e))

        # Round to 2 decimal places
        if "K_USD_bn" in capital_data.columns:
            capital_data["K_USD_bn"] = capital_data["K_USD_bn"].round(Config.DECIMAL_PLACES_CURRENCY)

        # Log summary statistics
        _log_calculation_summary(capital_data)

    except ValueError:
        logger.exception("Error in capital stock calculation")
        capital_data["K_USD_bn"] = np.nan
    else:
        return capital_data

    return capital_data
