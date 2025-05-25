"""
Markdown output generation utilities.

This module provides functions to generate markdown tables and documentation
from processed economic data with detailed methodology notes.
"""

from .markdown_template import MARKDOWN_TEMPLATE
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
from jinja2 import Template


def create_markdown_table(
    data: pd.DataFrame,
    output_path: str,
    extrapolation_info: Dict[str, Any],
    alpha: float = 1 / 3,
    capital_output_ratio: float = 3.0,
    input_file: str = "china_data_raw.md",
    end_year: int = 2025,
) -> None:
    """
    Create comprehensive markdown output with data table and methodology documentation.

    Args:
        data: Processed economic data DataFrame
        output_path: Path to write the markdown file
        extrapolation_info: Dictionary containing extrapolation method information
        alpha: Capital share parameter used in TFP calculation
        capital_output_ratio: Capital-output ratio used in capital stock calculation
        input_file: Name of the input raw data file
        end_year: Final year of data projection

    Note:
        The function generates a comprehensive markdown document including:
        - Data table with all economic indicators
        - Detailed methodology notes
        - Source attribution
        - Mathematical formulas for derived variables
        - Extrapolation method documentation
    """
    column_mapping = {
        "Year": "year",
        "GDP": "GDP_USD_bn",
        "Consumption": "C_USD_bn",
        "Government": "G_USD_bn",
        "Investment": "I_USD_bn",
        "Exports": "X_USD_bn",
        "Imports": "M_USD_bn",
        "Net Exports": "NX_USD_bn",
        "Population": "POP_mn",
        "Labor Force": "LF_mn",
        "Physical Capital": "K_USD_bn",
        "TFP": "TFP",
        "FDI (% of GDP)": "FDI_pct_GDP",
        "Human Capital": "hc",
        "Tax Revenue (bn USD)": "T_USD_bn",
        "Openness Ratio": "Openness_Ratio",
        "Saving (bn USD)": "S_USD_bn",
        "Private Saving (bn USD)": "S_priv_USD_bn",
        "Public Saving (bn USD)": "S_pub_USD_bn",
        "Saving Rate": "Saving_Rate",
    }

    headers = list(data.columns)
    rows = data.values.tolist()
    notes = []

    for var, info in extrapolation_info.items():
        if not info["years"]:
            continue
        display_name = var
        for disp, internal in column_mapping.items():
            if internal == var:
                display_name = disp
                break
        years = info["years"]
        if len(years) == 1:
            years_str = f"{years[0]}"
        else:
            years_str = f"{years[0]}-{years[-1]}"
        notes.append(f"- {display_name}: {info['method']} ({years_str})")

    # Group extrapolation methods for detailed notes
    extrapolation_methods: Dict[str, List[str]] = {
        "ARIMA(1,1,1)": [],
        "Average growth rate": [],
        "Linear regression": [],
        "Investment-based projection": [],
        "IMF projections": [],
        "Extrapolated": [],
    }

    for var, info in extrapolation_info.items():
        if not info["years"]:
            continue
        display_name = var
        for disp, internal in column_mapping.items():
            if internal == var:
                display_name = disp
                break

        method = info["method"]
        years_str = f"{info['years'][0]}-{info['years'][-1]}" if len(info["years"]) > 1 else f"{info['years'][0]}"

        if "ARIMA" in method:
            extrapolation_methods["ARIMA(1,1,1)"].append(f"{display_name} ({years_str})")
        elif "growth rate" in method:
            extrapolation_methods["Average growth rate"].append(f"{display_name} ({years_str})")
        elif "regression" in method:
            extrapolation_methods["Linear regression"].append(f"{display_name} ({years_str})")
        elif "Investment" in method or "investment" in method:
            extrapolation_methods["Investment-based projection"].append(f"{display_name} ({years_str})")
        elif "IMF" in method:
            extrapolation_methods["IMF projections"].append(f"{display_name} ({years_str})")
        else:
            extrapolation_methods["Extrapolated"].append(f"{display_name} ({years_str})")

    today = datetime.today().strftime("%Y-%m-%d")
    tmpl = Template(MARKDOWN_TEMPLATE)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(
            tmpl.render(
                headers=headers,
                rows=rows,
                notes=notes,
                extrapolation_methods=extrapolation_methods,
                alpha=alpha,
                capital_output_ratio=capital_output_ratio,
                input_file=input_file,
                end_year=end_year,
                today=today,
            )
        )
