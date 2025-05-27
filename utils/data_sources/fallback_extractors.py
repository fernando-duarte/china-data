"""Utility functions for extracting indicator data from fallback sources."""

import logging

import pandas as pd

from config import Config

logger = logging.getLogger(__name__)


def _extract_wdi_indicators(fallback_data: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Extract WDI indicators from fallback data."""
    result = {}
    raw_data_mapping = Config.get_raw_data_column_map()
    wdi_mapping = {
        display: internal
        for internal, display in raw_data_mapping.items()
        if not display.startswith("PWT") and display != "Year"
    }

    for col, name in wdi_mapping.items():
        if col in fallback_data.columns:
            indicator_df = fallback_data[["Year", col]].rename(columns={"Year": "year", col: name}).dropna()
            if len(indicator_df) > 0:
                result[name] = indicator_df
                logger.debug("Loaded %d rows for %s from fallback", len(indicator_df), name)

    return result


def _extract_tax_data(fallback_data: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Extract tax data from fallback data."""
    result = {}

    if "Tax Revenue (% of GDP)" in fallback_data.columns:
        tax_df = (
            fallback_data[["Year", "Tax Revenue (% of GDP)"]]
            .rename(columns={"Year": "year", "Tax Revenue (% of GDP)": "TAX_pct_GDP"})
            .dropna()
        )
        if len(tax_df) > 0:
            result["TAX_pct_GDP"] = tax_df
            logger.debug("Loaded %d rows for TAX_pct_GDP from fallback", len(tax_df))

    return result


def _extract_pwt_data(fallback_data: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Extract PWT data from fallback data."""
    result = {}

    raw_data_mapping = Config.get_raw_data_column_map()
    pwt_rename_map = {display: internal for internal, display in raw_data_mapping.items() if display.startswith("PWT")}
    pwt_cols = list(pwt_rename_map.keys())

    pwt_available = [col for col in pwt_cols if col in fallback_data.columns]
    if pwt_available:
        cols_to_select = ["Year", *pwt_available]
        rename_dict = {k: v for k, v in pwt_rename_map.items() if k in cols_to_select}
        pwt_df = (
            fallback_data[cols_to_select]
            .rename(columns=rename_dict)
            .dropna(subset=[rename_dict[c] for c in pwt_available], how="all")
        )
        if len(pwt_df) > 0:
            result["PWT"] = pwt_df
            logger.debug("Loaded %d rows for PWT from fallback", len(pwt_df))

    return result


def _split_into_indicators(fallback_data: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Split DataFrame into separate dataframes by indicator type."""
    result: dict[str, pd.DataFrame] = {}
    result.update(_extract_wdi_indicators(fallback_data))
    result.update(_extract_tax_data(fallback_data))
    result.update(_extract_pwt_data(fallback_data))

    return result
