"""Helper functions for capital stock calculations."""

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def _calculate_capital_for_year(
    year: int,
    rkna_value: float,
    pl_gdpo_value: float,
    *,
    rkna_baseline: float,
    pl_gdpo_baseline: float,
    k_baseline_usd: float,
) -> float:
    """Calculate capital stock for a specific year."""
    if pd.isna(rkna_value) or pd.isna(pl_gdpo_value):
        logger.debug("Missing required data for year %d", year)
        return np.nan

    return (rkna_value / rkna_baseline) * (pl_gdpo_value / pl_gdpo_baseline) * k_baseline_usd


def _log_calculation_summary(capital_data: pd.DataFrame) -> None:
    """Log summary statistics for capital stock calculation."""
    k_data = capital_data.dropna(subset=["K_USD_bn"])
    logger.info("Calculated capital stock for %d years", k_data.shape[0])

    if len(k_data) > 0:
        min_k = k_data["K_USD_bn"].min()
        max_k = k_data["K_USD_bn"].max()
        logger.info("Capital stock range: %.2f to %.2f billion USD", min_k, max_k)
