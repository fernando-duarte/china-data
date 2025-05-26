"""Capital stock projection module.

This module provides functions for projecting capital stock into the future
using a perpetual inventory method.
"""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def _validate_inputs(processed_data: pd.DataFrame) -> tuple[bool, str]:
    """Validate input data for capital stock projection.

    Args:
        processed_data: DataFrame to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(processed_data, pd.DataFrame):
        return False, "Invalid input type: processed_data must be a pandas DataFrame"

    required_columns = ["year", "K_USD_bn", "I_USD_bn"]
    for column in required_columns:
        if column not in processed_data.columns:
            return False, f"Required '{column}' column not found in data"

    k_data_not_na = processed_data.dropna(subset=["K_USD_bn"])
    if len(k_data_not_na) == 0:
        return False, "No non-NA capital stock data available for projection"

    return True, ""


def _get_last_capital_value(capital_data: pd.DataFrame) -> tuple[float, int]:
    """Get the last valid capital stock value and year.

    Args:
        capital_data: DataFrame with capital stock data

    Returns:
        Tuple of (last_capital_value, last_year)

    Raises:
        ValueError: If no valid capital stock data is found
    """
    k_data_not_na = capital_data.dropna(subset=["K_USD_bn"])
    last_year_with_data = k_data_not_na["year"].max()
    last_k = k_data_not_na.loc[k_data_not_na.year == last_year_with_data, "K_USD_bn"].iloc[0]

    if pd.isna(last_k) or last_k <= 0:
        error_msg = f"Invalid capital stock value for year {last_year_with_data}: {last_k}"
        raise ValueError(error_msg)

    return float(last_k), int(last_year_with_data)


def _estimate_investment(capital_data: pd.DataFrame, year: int) -> float:
    """Estimate investment value for a given year.

    Args:
        capital_data: DataFrame with investment data
        year: Year to estimate investment for

    Returns:
        Estimated investment value
    """
    # Try to get investment for previous year
    prev_year = year - 1
    prev_inv_row = capital_data.loc[capital_data["year"] == prev_year, "I_USD_bn"]

    if len(prev_inv_row) == 0 or pd.isna(prev_inv_row.iloc[0]):
        logger.warning("No investment data for previous year %d, using last known value", prev_year)
        # Use the last known investment value
        last_inv = capital_data.dropna(subset=["I_USD_bn"])["I_USD_bn"].iloc[-1]
        return float(last_inv)

    # Use previous year's investment with a small growth rate (5%)
    return float(prev_inv_row.iloc[0] * 1.05)


def _project_years(
    capital_data: pd.DataFrame, years_to_project: list[int], last_k: float, last_year: int, delta: float
) -> dict[int, float]:
    """Project capital stock for specified years.

    Args:
        capital_data: DataFrame with investment data
        years_to_project: List of years to project
        last_k: Last known capital stock value
        last_year: Last year with known capital stock
        delta: Depreciation rate

    Returns:
        Dictionary mapping years to projected capital stock values
    """
    proj = {last_year: last_k}

    for y in years_to_project:
        # Get investment value for this year
        inv_row = capital_data.loc[capital_data["year"] == y, "I_USD_bn"]

        if len(inv_row) == 0 or pd.isna(inv_row.iloc[0]):
            logger.warning("No investment data for year %d, using estimated value", y)
            inv_value = _estimate_investment(capital_data, y)
        else:
            inv_value = inv_row.iloc[0]

        previous_k = proj[y - 1]

        # Apply the perpetual inventory method
        projected_k = (1 - delta) * previous_k + inv_value

        # Store the projected value
        proj[y] = round(projected_k, 2)

    return proj


def _merge_projections(capital_data: pd.DataFrame, proj_df: pd.DataFrame, end_year: int) -> pd.DataFrame:
    """Merge projected values with original data.

    Args:
        capital_data: Original DataFrame
        proj_df: DataFrame with projections
        end_year: Final year to include

    Returns:
        Merged DataFrame with projections
    """
    result = capital_data

    # Make sure all years up to end_year exist in the result
    for year in range(int(capital_data["year"].min()), end_year + 1):
        if year not in result["year"].to_numpy():
            result = pd.concat([result, pd.DataFrame({"year": [year]})], ignore_index=True)

    # For each projection year, update the capital stock
    for _, row in proj_df.iterrows():
        year_mask = result["year"] == row["year"]
        if year_mask.any():
            result.loc[year_mask, "K_USD_bn"] = row["K_USD_bn"]
        else:
            # Add missing years
            new_row = pd.DataFrame({"year": [row["year"]], "K_USD_bn": [row["K_USD_bn"]]})
            result = pd.concat([result, new_row], ignore_index=True)

    # Sort by year for consistency
    return result.sort_values("year").reset_index(drop=True)


def project_capital_stock(processed_data: pd.DataFrame, end_year: int, delta: float = 0.05) -> pd.DataFrame:
    """Project capital stock into the future using a perpetual inventory method.

    This method projects capital stock using the perpetual inventory equation:
    K_t = (1-δ) * K_{t-1} + I_t

    Args:
        processed_data: DataFrame containing 'year', 'K_USD_bn', and 'I_USD_bn' columns
                       (Investment should already be extrapolated to end_year)
        end_year: Final year to project capital stock to
        delta: Depreciation rate (default: 0.05)

    Returns:
        DataFrame with projected capital stock values
    """
    logger.info("Projecting capital stock to year %d with delta=%f", end_year, delta)

    # Validate inputs
    is_valid, error_msg = _validate_inputs(processed_data)
    if not is_valid:
        logger.error(error_msg)
        return pd.DataFrame({"year": [], "K_USD_bn": []})

    # Create a copy to avoid modifying the original
    capital_data = processed_data.copy()

    # Check if we have data to project from
    k_data_not_na = capital_data.dropna(subset=["K_USD_bn"])

    # Sort by year to ensure correct order
    capital_data = capital_data.sort_values("year").reset_index(drop=True)
    logger.info("Capital stock data available: %d rows", k_data_not_na.shape[0])

    # Check if we need to project at all (if end_year is already covered)
    max_year = capital_data["year"].max()
    if max_year >= end_year:
        logger.info("Data already extends to year %d, no projection needed", max_year)
        return capital_data

    # Get the last valid capital stock value for projection
    try:
        last_k, last_year_with_data = _get_last_capital_value(capital_data)
        logger.info("Last capital stock value: %.2f billion USD (year %d)", last_k, last_year_with_data)
    except ValueError:
        logger.exception("Error retrieving last capital stock value")
        return capital_data

    # Define years to project
    years_to_project = list(range(int(last_year_with_data) + 1, end_year + 1))
    if not years_to_project:
        logger.info("No years to project - returning original data")
        return capital_data

    logger.info("Years to project: %d to %d", min(years_to_project), max(years_to_project))

    # Project capital stock using perpetual inventory method
    try:
        proj = _project_years(capital_data, years_to_project, last_k, last_year_with_data, delta)
        logger.info("Successfully projected capital stock for %d years", len(proj) - 1)

        # Create DataFrame with projections
        proj_df = pd.DataFrame(list(proj.items()), columns=["year", "K_USD_bn"])

        # Merge with original data
        result = _merge_projections(capital_data, proj_df, end_year)

        logger.info("Final result has capital stock data for %d years", result.dropna(subset=["K_USD_bn"]).shape[0])
    except Exception:
        logger.exception("Error projecting capital stock")
        return capital_data

    return result
