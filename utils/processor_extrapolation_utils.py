"""Helper functions for series extrapolation."""

import pandas as pd

from config import Config

from .processor_extrapolation_constants import (
    DEFAULT_LOOKBACK_YEARS,
    MIN_HISTORICAL_DATA_POINTS,
)


def _get_default_growth_rate(col: str) -> float:
    """Get default growth rate for a specific column."""
    if col in ["GDP_USD_bn", "C_USD_bn", "G_USD_bn", "I_USD_bn", "X_USD_bn", "M_USD_bn"]:
        return Config.DEFAULT_GROWTH_RATE
    if col == "POP_mn":
        return 0.005
    if col in {"LF_mn", "hc"}:
        return 0.01
    if col == "K_USD_bn":
        return 0.04
    return 0.03


def _calculate_historical_growth(historical_data: pd.DataFrame, col: str) -> float:
    """Calculate average historical growth rate for a column."""
    if len(historical_data) >= MIN_HISTORICAL_DATA_POINTS:
        n_years = min(DEFAULT_LOOKBACK_YEARS, len(historical_data))
        last_years = historical_data.iloc[-n_years:][col].to_numpy()
        if len(last_years) > 1:
            growth_rates = [(last_years[i] / last_years[i - 1]) - 1 for i in range(1, len(last_years))]
            return float(sum(growth_rates) / len(growth_rates))
    return _get_default_growth_rate(col)


def _fill_missing_key_variables(data_df: pd.DataFrame, years_to_add: list[int]) -> pd.DataFrame:
    """Fill missing values for key variables using growth-based extrapolation."""
    key_vars = [
        "GDP_USD_bn",
        "C_USD_bn",
        "G_USD_bn",
        "I_USD_bn",
        "X_USD_bn",
        "M_USD_bn",
        "POP_mn",
        "LF_mn",
        "FDI_pct_GDP",
        "TAX_pct_GDP",
        "hc",
        "K_USD_bn",
    ]

    for year in years_to_add:
        for col in key_vars:
            if col in data_df.columns and pd.isna(data_df.loc[data_df.year == year, col].to_numpy()[0]):
                last_valid = data_df[data_df.year < year][[col]].dropna()
                if len(last_valid) > 0:
                    last_value = float(last_valid.iloc[-1][col].to_numpy()[0])
                    last_year = int(data_df.loc[last_valid.index[-1], "year"])

                    historical_data = data_df[data_df.year <= data_df.year.max()][[col]].dropna()
                    avg_growth = _calculate_historical_growth(historical_data, col)

                    projected_value = last_value * (1 + avg_growth) ** (year - last_year)
                    data_df.loc[data_df.year == year, col] = round(projected_value, 4)

    return data_df
