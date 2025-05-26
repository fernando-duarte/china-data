"""Unit conversion utilities for data processing."""

import pandas as pd


def convert_units(df: pd.DataFrame) -> pd.DataFrame:
    """Convert units to billions for monetary values and millions for population."""
    result = df.copy()

    # Convert monetary values from USD to billions USD
    monetary_columns = [
        "GDP_USD",
        "C_USD",
        "G_USD",
        "I_USD",
        "X_USD",
        "M_USD",
        "K_USD",
        "T_USD",
        "S_USD",
        "S_pub_USD",
        "S_priv_USD",
    ]

    for col in monetary_columns:
        if col in result.columns:
            result[f"{col}_bn"] = result[col] / 1e9
            result.drop(col, axis=1, inplace=True)

    # Convert population values from persons to millions
    population_columns = ["POP", "LF"]
    for col in population_columns:
        if col in result.columns:
            result[f"{col}_mn"] = result[col] / 1e6
            result.drop(col, axis=1, inplace=True)

    return result
