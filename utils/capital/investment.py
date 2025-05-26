"""Investment calculation module.

This module provides functions for calculating investment data based on capital stock
and depreciation rates.
"""

import logging

import numpy as np
import pandas as pd

from config import Config

logger = logging.getLogger(__name__)

# Constants for magic numbers
MIN_DATA_POINTS = 2
MIN_OUTLIER_DETECTION_POINTS = 5
OUTLIER_Z_SCORE_THRESHOLD = 3


def _validate_investment_input(capital_data: pd.DataFrame) -> tuple[bool, str]:
    """Validate input data for investment calculation."""
    if not isinstance(capital_data, pd.DataFrame):
        return False, "Input is not a pandas DataFrame"

    if "year" not in capital_data.columns:
        return False, "'year' column missing from input data"

    if "K_USD_bn" not in capital_data.columns:
        return False, "'K_USD_bn' column missing from input data"

    return True, ""


def _prepare_capital_data(capital_data: pd.DataFrame) -> pd.DataFrame:
    """Prepare and clean capital data for investment calculation."""
    capital_df = capital_data.copy()
    df_clean = capital_df.dropna(subset=["K_USD_bn"])

    if df_clean.shape[0] < MIN_DATA_POINTS:
        msg = "Not enough non-NA capital stock data points to calculate investment"
        raise ValueError(msg)

    return df_clean.sort_values("year")


def _calculate_single_investment(curr_k: float, prev_k: float, delta: float) -> float:
    """Calculate investment for a single year using perpetual inventory method."""
    return curr_k - (1 - delta) * prev_k


def _apply_investment_sanity_checks(inv: float, curr_k: float, curr_year: int) -> float:
    """Apply sanity checks to calculated investment values."""
    if inv < 0:
        logger.warning("Calculated negative investment for year %d: %.2f", curr_year, inv)
        if inv < -Config.NEGATIVE_INVESTMENT_THRESHOLD * curr_k:
            logger.warning("Large negative investment (%.2f) in year %d, capping to zero", inv, curr_year)
            return 0
    return inv


def _log_investment_statistics(result: pd.DataFrame, valid_years: list[int]) -> None:
    """Log statistics for calculated investment values."""
    non_na = result.dropna(subset=["I_USD_bn"])
    if len(non_na) == 0:
        logger.warning("No valid investment calculations")
        return

    min_i = non_na["I_USD_bn"].min()
    max_i = non_na["I_USD_bn"].max()
    mean_i = non_na["I_USD_bn"].mean()

    logger.info("Calculated investment for %d years", len(valid_years))
    logger.info(
        "Investment range: %.2f to %.2f billion USD, average: %.2f billion USD",
        min_i,
        max_i,
        mean_i,
    )

    _check_investment_outliers(non_na, mean_i)
    _log_investment_ratios(non_na)


def _check_investment_outliers(non_na: pd.DataFrame, mean_i: float) -> None:
    """Check for outlier investment values."""
    if non_na.shape[0] <= MIN_OUTLIER_DETECTION_POINTS:
        return

    std_i = non_na["I_USD_bn"].std()
    z_scores = (non_na["I_USD_bn"] - mean_i) / std_i
    outliers = non_na[abs(z_scores) > OUTLIER_Z_SCORE_THRESHOLD]

    if len(outliers) > 0:
        outlier_years = outliers["year"].tolist()
        logger.warning("Outlier investment values detected for years: %s", outlier_years)


def _log_investment_ratios(non_na: pd.DataFrame) -> None:
    """Log investment-to-capital ratios."""
    non_na = non_na.copy()
    non_na["I_K_ratio"] = non_na["I_USD_bn"] / non_na["K_USD_bn"]
    avg_i_k_ratio = non_na["I_K_ratio"].mean()
    logger.info(
        "Average investment-to-capital ratio: %.4f (%.2f%%)",
        avg_i_k_ratio,
        avg_i_k_ratio * 100,
    )


def calculate_investment(capital_data: pd.DataFrame, delta: float = Config.DEFAULT_DEPRECIATION_RATE) -> pd.DataFrame:
    """Calculate investment data using changes in capital stock and depreciation.

    This function calculates investment using the perpetual inventory method in reverse:
    I_t = K_t - (1-delta) * K_{t-1}

    Args:
        capital_data: DataFrame with 'year' and 'K_USD_bn' columns
        delta: Depreciation rate (default from Config)

    Returns:
        DataFrame with 'year' and 'I_USD_bn' columns
    """
    logger.info("Estimating investment data using delta=%f", delta)

    # Validate input
    is_valid, error_msg = _validate_investment_input(capital_data)
    if not is_valid:
        logger.error(error_msg)
        return pd.DataFrame({"year": [], "I_USD_bn": []})

    try:
        # Prepare data
        df_clean = _prepare_capital_data(capital_data)

        logger.info(
            "Using %d years of capital stock data from %d to %d",
            df_clean.shape[0],
            df_clean["year"].min(),
            df_clean["year"].max(),
        )

        # Create result DataFrame
        result = pd.DataFrame({"year": capital_data["year"]})
        investments: dict[int, float] = {}
        valid_years = []

        # Calculate investments for consecutive years
        for i in range(1, len(df_clean)):
            curr_year = int(df_clean.iloc[i]["year"])
            prev_year = int(df_clean.iloc[i - 1]["year"])

            if curr_year == prev_year + 1:
                curr_k = float(df_clean.iloc[i]["K_USD_bn"])
                prev_k = float(df_clean.iloc[i - 1]["K_USD_bn"])

                inv = _calculate_single_investment(curr_k, prev_k, delta)
                inv = _apply_investment_sanity_checks(inv, curr_k, curr_year)

                investments[curr_year] = inv
                valid_years.append(curr_year)
            else:
                logger.debug("Skipping non-consecutive years %d to %d", prev_year, curr_year)

        # Process results
        if investments:
            inv_df = pd.DataFrame(list(investments.items()), columns=["year", "I_USD_bn"])
            result = result.merge(inv_df, on="year", how="left")
            _log_investment_statistics(result, valid_years)
        else:
            logger.warning("Could not calculate investment for any year")

        # Round results
        if "I_USD_bn" in result.columns:
            result["I_USD_bn"] = result["I_USD_bn"].round(Config.DECIMAL_PLACES_INVESTMENT)

    except Exception:
        logger.exception("Error calculating investment")
        result = pd.DataFrame({"year": capital_data["year"], "I_USD_bn": np.nan})

    return result
