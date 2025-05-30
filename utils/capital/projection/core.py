"""Core logic for projecting capital stock."""

import logging

import pandas as pd

from .validation import _get_last_capital_value, _validate_inputs

logger = logging.getLogger(__name__)


def _estimate_investment(capital_data: pd.DataFrame, year: int) -> float:
    """Estimate investment value for a given year."""
    prev_year = year - 1
    prev_inv_row = capital_data.loc[capital_data["year"] == prev_year, "I_USD_bn"]
    if len(prev_inv_row) == 0 or pd.isna(prev_inv_row.iloc[0]):
        logger.warning(
            "No investment data for previous year %d, using last known value",
            prev_year,
        )
        last_inv = capital_data.dropna(subset=["I_USD_bn"])["I_USD_bn"].iloc[-1]
        return float(last_inv)
    return float(prev_inv_row.iloc[0] * 1.05)


def _project_years(
    capital_data: pd.DataFrame,
    years_to_project: list[int],
    last_k: float,
    last_year: int,
    delta: float,
) -> dict[int, float]:
    """Project capital stock for specified years."""
    proj = {last_year: last_k}
    for y in years_to_project:
        inv_row = capital_data.loc[capital_data["year"] == y, "I_USD_bn"]
        if len(inv_row) == 0 or pd.isna(inv_row.iloc[0]):
            logger.warning("No investment data for year %d, using estimated value", y)
            inv_value = _estimate_investment(capital_data, y)
        else:
            inv_value = inv_row.iloc[0]
        previous_k = proj[y - 1]
        projected_k = (1 - delta) * previous_k + inv_value
        proj[y] = round(projected_k, 2)
    return proj


def _merge_projections(
    capital_data: pd.DataFrame, proj_df: pd.DataFrame, end_year: int
) -> pd.DataFrame:
    """Merge projected values with original data."""
    result = capital_data
    for year in range(int(capital_data["year"].min()), end_year + 1):
        if year not in result["year"].to_numpy():
            result = pd.concat([result, pd.DataFrame({"year": [year]})], ignore_index=True)
    for _, row in proj_df.iterrows():
        year_mask = result["year"] == row["year"]
        if year_mask.any():
            result.loc[year_mask, "K_USD_bn"] = row["K_USD_bn"]
        else:
            new_row = pd.DataFrame({"year": [row["year"]], "K_USD_bn": [row["K_USD_bn"]]})
            result = pd.concat([result, new_row], ignore_index=True)
    return result.sort_values("year").reset_index(drop=True)


def project_capital_stock(
    processed_data: pd.DataFrame, end_year: int, delta: float = 0.05
) -> pd.DataFrame:
    """Project capital stock into the future using a perpetual inventory method."""
    logger.info("Projecting capital stock to year %d with delta=%f", end_year, delta)
    is_valid, error_msg = _validate_inputs(processed_data)
    if not is_valid:
        logger.error(error_msg)
        return pd.DataFrame({"year": [], "K_USD_bn": []})
    capital_data = processed_data.copy()
    k_data_not_na = capital_data.dropna(subset=["K_USD_bn"])
    capital_data = capital_data.sort_values("year").reset_index(drop=True)
    logger.info("Capital stock data available: %d rows", k_data_not_na.shape[0])
    max_year = capital_data["year"].max()
    if max_year >= end_year:
        logger.info("Data already extends to year %d, no projection needed", max_year)
        return capital_data
    try:
        last_k, last_year_with_data = _get_last_capital_value(capital_data)
        logger.info(
            "Last capital stock value: %.2f billion USD (year %d)",
            last_k,
            last_year_with_data,
        )
    except ValueError:
        logger.exception("Error retrieving last capital stock value")
        return capital_data
    years_to_project = list(range(int(last_year_with_data) + 1, end_year + 1))
    if not years_to_project:
        logger.info("No years to project - returning original data")
        return capital_data
    logger.info("Years to project: %d to %d", min(years_to_project), max(years_to_project))
    try:
        proj = _project_years(capital_data, years_to_project, last_k, last_year_with_data, delta)
        logger.info("Successfully projected capital stock for %d years", len(proj) - 1)
        proj_df = pd.DataFrame(list(proj.items()), columns=["year", "K_USD_bn"])
        result = _merge_projections(capital_data, proj_df, end_year)
        logger.info(
            "Final result has capital stock data for %d years",
            result.dropna(subset=["K_USD_bn"]).shape[0],
        )
    except Exception:  # pylint: disable=broad-exception-caught
        logger.exception("Error projecting capital stock")
        return capital_data
    return result
