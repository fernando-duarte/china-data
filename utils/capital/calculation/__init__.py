"""Capital stock calculation utilities."""

import logging
from typing import Any

import numpy as np
import pandas as pd

from config import Config

from .baseline import _find_baseline_year, _get_baseline_value
from .helpers import CapitalBaselineParams, _calculate_capital_for_year, _log_calculation_summary
from .validation import _check_required_columns, _validate_input_data

logger = logging.getLogger(__name__)


def _process_capital_row(row: pd.Series[Any], baseline_info: dict[str, Any]) -> float | None:
    """Process a single row to calculate capital."""
    year = row["year"]
    rkna_value = row["rkna"]
    pl_gdpo_value = row["pl_gdpo"]

    try:
        baseline_params = CapitalBaselineParams(
            rkna_baseline=baseline_info["rkna"],
            pl_gdpo_baseline=baseline_info["pl_gdpo"],
            k_baseline_usd=baseline_info["k_usd"],
        )
        k_usd = _calculate_capital_for_year(
            year,
            rkna_value,
            pl_gdpo_value,
            params=baseline_params,
        )
        return k_usd if not pd.isna(k_usd) else None
    except (ValueError, TypeError) as e:
        logger.warning("Error calculating capital for year %s: %s", row.get("year", "?"), str(e))
        return None


def calculate_capital_stock(
    raw_data: pd.DataFrame, capital_output_ratio: float = Config.DEFAULT_CAPITAL_OUTPUT_RATIO
) -> pd.DataFrame:
    """Calculate capital stock using PWT data and capital-output ratio."""
    logger.info("Calculating capital stock using K/Y ratio = %f", capital_output_ratio)

    # Validate input
    is_valid, error_msg = _validate_input_data(raw_data)
    if not is_valid:
        logger.error(error_msg)
        return pd.DataFrame({"year": [], "K_USD_bn": []})

    # Create a copy to avoid modifying the original
    capital_data = raw_data.copy()

    # Log available columns for debugging
    logger.debug(
        "Available columns for capital stock calculation: %s", capital_data.columns.tolist()
    )

    # Check for required columns
    missing_columns = _check_required_columns(capital_data)
    if missing_columns:
        logger.info("Adding empty K_USD_bn column due to missing data")
        capital_data["K_USD_bn"] = np.nan
        return capital_data

    try:
        baseline_info: dict[str, Any] = {}
        baseline_info["year"] = _find_baseline_year(capital_data)
        logger.info(
            "Using %d as baseline year for capital stock calculation", baseline_info["year"]
        )

        baseline_info["gdp"] = _get_baseline_value(capital_data, baseline_info["year"], "cgdpo_bn")
        baseline_info["rkna"] = _get_baseline_value(capital_data, baseline_info["year"], "rkna")
        baseline_info["pl_gdpo"] = _get_baseline_value(
            capital_data, baseline_info["year"], "pl_gdpo"
        )

        baseline_info["k_usd"] = baseline_info["gdp"] * capital_output_ratio
        logger.info(
            "Baseline year (%d) GDP: %.2f billion USD",
            baseline_info["year"],
            baseline_info["gdp"],
        )
        logger.info(
            "Baseline year (%d) calculated capital: %.2f billion USD",
            baseline_info["year"],
            baseline_info["k_usd"],
        )

        capital_data["K_USD_bn"] = np.nan

        for _, row in capital_data.iterrows():
            k_usd = _process_capital_row(row, baseline_info)
            if k_usd is not None:
                capital_data.loc[capital_data.year == row["year"], "K_USD_bn"] = k_usd

        if "K_USD_bn" in capital_data.columns:
            capital_data["K_USD_bn"] = capital_data["K_USD_bn"].round(
                Config.DECIMAL_PLACES_CURRENCY
            )

        _log_calculation_summary(capital_data)

    except ValueError:
        logger.exception("Error in capital stock calculation")
        capital_data["K_USD_bn"] = np.nan
    else:
        return capital_data

    return capital_data


__all__ = ["calculate_capital_stock"]
