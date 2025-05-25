"""
Data formatting utilities for output generation.

This module provides functions to format DataFrames for various output formats
with appropriate number formatting and value handling.
"""

import pandas as pd


def format_data_for_output(data_df: pd.DataFrame) -> pd.DataFrame:
    """
    Format DataFrame values for output with appropriate precision and formatting.

    Args:
        data_df: Input DataFrame to format

    Returns:
        DataFrame with formatted values suitable for output

    Note:
        - NaN values are converted to "nan" strings
        - Different columns get different precision levels
        - Trailing zeros are removed for cleaner display
    """
    # Instead of copying the entire DataFrame, create a new one with formatted values
    formatted_data = {}

    for col_name in data_df.columns:
        vals = []
        for val in data_df[col_name]:
            if pd.isna(val):
                vals.append("nan")
            elif isinstance(val, float):
                if col_name in ["FDI (% of GDP)", "TFP", "Human Capital", "Openness Ratio", "Saving Rate"]:
                    vals.append(f"{val:.4f}".rstrip("0").rstrip("."))
                elif col_name in [
                    "GDP",
                    "Consumption",
                    "Government",
                    "Investment",
                    "Exports",
                    "Imports",
                    "Net Exports",
                    "Physical Capital",
                    "Tax Revenue (bn USD)",
                    "Saving (bn USD)",
                    "Private Saving (bn USD)",
                    "Public Saving (bn USD)",
                ]:
                    vals.append(f"{val:.4f}".rstrip("0").rstrip("."))
                elif col_name in ["Population", "Labor Force"]:
                    vals.append(f"{val:.2f}".rstrip("0").rstrip("."))
                else:
                    vals.append(f"{val:.2f}".rstrip("0").rstrip("."))
            elif isinstance(val, int) and col_name == "Year":
                vals.append(str(val))
            elif col_name in ["Population", "Labor Force"] and isinstance(val, (int, float)):
                vals.append(f"{val:.2f}".rstrip("0").rstrip("."))
            else:
                vals.append(str(val))
        formatted_data[col_name] = vals

    return pd.DataFrame(formatted_data)
