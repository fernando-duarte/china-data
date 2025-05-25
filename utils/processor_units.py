"""Convert data units to standardized formats.

This module handles unit conversions for economic data:
- GDP components: Convert to billions USD
- Population/Labor Force: Convert to millions of people
- PWT data: Convert to billions
"""

import pandas as pd


def convert_units(raw_data: pd.DataFrame) -> pd.DataFrame:
    """Convert units to standardized formats.

    Args:
        raw_data: Raw data with original units

    Returns:
        DataFrame with converted units and renamed columns
    """
    df = raw_data.copy()

    # Convert USD values to billions
    for col in ["GDP_USD", "C_USD", "G_USD", "I_USD", "X_USD", "M_USD"]:
        if col in df.columns:
            df[col] = df[col] / 1e9

    # Convert PWT data to billions
    for col in ["rgdpo", "cgdpo"]:
        if col in df.columns:
            df[col] = df[col] / 1000

    # Convert population/labor force to millions
    for col in ["POP", "LF"]:
        if col in df.columns:
            df[col] = df[col] / 1e6

    # Rename columns to indicate units
    df = df.rename(
        columns={
            "GDP_USD": "GDP_USD_bn",
            "C_USD": "C_USD_bn",
            "G_USD": "G_USD_bn",
            "I_USD": "I_USD_bn",
            "X_USD": "X_USD_bn",
            "M_USD": "M_USD_bn",
            "rgdpo": "rgdpo_bn",
            "cgdpo": "cgdpo_bn",
            "POP": "POP_mn",
            "LF": "LF_mn",
        }
    )

    return df
