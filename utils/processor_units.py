"""Unit conversion utilities for the China data processor."""

import pandas as pd


def convert_units(data: pd.DataFrame) -> pd.DataFrame:
    """Convert units to standardized formats.

    Args:
        data: Input DataFrame with raw data

    Returns:
        DataFrame with converted units
    """
    result = data.copy()

    # Convert USD values to billions USD
    usd_columns = [
        "GDP_USD",
        "C_USD",
        "G_USD",
        "I_USD",
        "X_USD",
        "M_USD",
        "NX_USD",
        "K_USD",
        "FDI_USD",
    ]
    for col in usd_columns:
        if col in result.columns:
            result[f"{col}_bn"] = result[col] / 1e9
            result = result.drop(col, axis=1)

    # Convert population values from persons to millions
    pop_columns = ["POP", "LF"]
    for col in pop_columns:
        if col in result.columns:
            result[f"{col}_mn"] = result[col] / 1e6
            result = result.drop(col, axis=1)

    # Convert PWT cgdpo (millions USD) to billions USD
    if "cgdpo" in result.columns:
        result["cgdpo_bn"] = (
            result["cgdpo"] / 1e3
        )  # cgdpo is in millions, so divide by 1000 to get billions
        result = result.drop("cgdpo", axis=1)

    return result
