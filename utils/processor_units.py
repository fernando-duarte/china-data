"""Unit conversion utilities for data processing."""

import pandas as pd

from config import Config


def convert_units(df: pd.DataFrame) -> pd.DataFrame:
    """Convert units in the DataFrame to standardized units.

    Converts:
    - Currency values from USD to billions USD
    - Population from total to millions
    - Labor force from total to millions

    Args:
        df: DataFrame with raw data

    Returns:
        DataFrame with converted units
    """
    result = df.copy()

    # Convert currency columns from USD to billions USD
    currency_cols = [
        col for col in result.columns
        if col.endswith("_USD") and not col.endswith("_bn")
    ]
    for col in currency_cols:
        new_col = col.replace("_USD", "_USD_bn")
        result[new_col] = result[col] / Config.BILLION_DIVISOR
        result.drop(col, axis=1, inplace=True)

    # Convert population from total to millions
    if "POP" in result.columns:
        result["POP_mn"] = result["POP"] / Config.BILLION_DIVISOR
        result.drop("POP", axis=1, inplace=True)

    # Convert labor force from total to millions
    if "LF" in result.columns:
        result["LF_mn"] = result["LF"] / Config.BILLION_DIVISOR
        result.drop("LF", axis=1, inplace=True)

    return result
