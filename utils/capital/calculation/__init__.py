"""Capital stock calculation utilities."""

import logging

import numpy as np
import pandas as pd

from config import Config

from .baseline import _find_baseline_year, _get_baseline_value
from .helpers import _calculate_capital_for_year, _log_calculation_summary
from .validation import _check_required_columns, _validate_input_data

logger = logging.getLogger(__name__)


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
    logger.debug("Available columns for capital stock calculation: %s", capital_data.columns.tolist())

    # Check for required columns
    missing_columns = _check_required_columns(capital_data)
    if missing_columns:
        logger.info("Adding empty K_USD_bn column due to missing data")
        capital_data["K_USD_bn"] = np.nan
        return capital_data

    try:
        baseline_year = _find_baseline_year(capital_data)
        logger.info("Using %d as baseline year for capital stock calculation", baseline_year)

        gdp_baseline = _get_baseline_value(capital_data, baseline_year, "cgdpo_bn")
        rkna_baseline = _get_baseline_value(capital_data, baseline_year, "rkna")
        pl_gdpo_baseline = _get_baseline_value(capital_data, baseline_year, "pl_gdpo")

        k_baseline_usd = gdp_baseline * capital_output_ratio
        logger.info("Baseline year (%d) GDP: %.2f billion USD", baseline_year, gdp_baseline)
        logger.info("Baseline year (%d) calculated capital: %.2f billion USD", baseline_year, k_baseline_usd)

        capital_data["K_USD_bn"] = np.nan

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

        if "K_USD_bn" in capital_data.columns:
            capital_data["K_USD_bn"] = capital_data["K_USD_bn"].round(Config.DECIMAL_PLACES_CURRENCY)

        _log_calculation_summary(capital_data)

    except ValueError:
        logger.exception("Error in capital stock calculation")
        capital_data["K_USD_bn"] = np.nan
    else:
        return capital_data

    return capital_data


__all__ = ["calculate_capital_stock"]
