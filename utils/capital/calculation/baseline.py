"""Baseline selection utilities for capital stock calculations."""

import logging

import pandas as pd

from config import Config

logger = logging.getLogger(__name__)


def _find_baseline_year(capital_data: pd.DataFrame) -> int:
    """Find the best baseline year for capital stock calculation."""
    baseline_year = Config.BASELINE_YEAR
    if baseline_year in capital_data["year"].to_numpy():
        return baseline_year

    logger.warning("Missing %d data for capital stock calculation", baseline_year)

    years_available = sorted(capital_data["year"].unique())
    logger.info("Available years: %d to %d", min(years_available), max(years_available))

    # Try to find an alternative baseline year (closest to Config.BASELINE_YEAR)
    alt_years = [
        y
        for y in years_available
        if Config.BASELINE_YEAR_RANGE_MIN <= y <= Config.BASELINE_YEAR_RANGE_MAX
    ]
    if alt_years:
        baseline_year = min(alt_years, key=lambda y: abs(y - Config.BASELINE_YEAR))
        logger.info("Using alternative baseline year: %d", baseline_year)
        return baseline_year

    msg = "No suitable baseline year found in range 2010-2020"
    raise ValueError(msg)


def _get_baseline_value(capital_data: pd.DataFrame, year: int, column: str) -> float:
    """Get baseline value for a specific column and year."""
    baseline_rows = capital_data.loc[capital_data.year == year, column]
    if len(baseline_rows) == 0 or pd.isna(baseline_rows.iloc[0]):
        error_msg = f"No {column} data for {year}"
        raise ValueError(error_msg)
    return float(baseline_rows.iloc[0])
