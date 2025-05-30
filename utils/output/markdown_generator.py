"""Markdown output generation utilities.

This module provides functions to generate markdown tables and documentation
from processed economic data with detailed methodology notes.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from jinja2 import Template

from config import Config

from .markdown_template import MARKDOWN_TEMPLATE


def _get_display_name(var: str, column_mapping: dict[str, str]) -> str:
    """Get display name for a variable using column mapping."""
    for disp, internal in column_mapping.items():
        if internal == var:
            return disp
    return var


def _format_years_string(years: list[int]) -> str:
    """Format years list into a readable string."""
    if len(years) == 1:
        return str(years[0])
    return f"{years[0]}-{years[-1]}"


def _categorize_extrapolation_method(method: str) -> str:
    """Categorize extrapolation method into standard groups."""
    if "ARIMA" in method:
        return "ARIMA(1,1,1)"
    if "growth rate" in method:
        return "Average growth rate"
    if "regression" in method:
        return "Linear regression"
    if "Investment" in method or "investment" in method:
        return "Investment-based projection"
    if "IMF" in method:
        return "IMF projections"
    return "Extrapolated"


def _process_extrapolation_info(
    extrapolation_info: dict[str, Any]
) -> tuple[list[str], dict[str, list[str]]]:
    """Process extrapolation info to create notes and method groupings."""
    column_mapping = Config.get_inverse_column_map()
    notes = []
    extrapolation_methods: dict[str, list[str]] = {
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

        display_name = _get_display_name(var, column_mapping)
        years_str = _format_years_string(info["years"])

        # Add to notes
        notes.append(f"- {display_name}: {info['method']} ({years_str})")

        # Categorize method
        method_category = _categorize_extrapolation_method(info["method"])
        extrapolation_methods[method_category].append(f"{display_name} ({years_str})")

    return notes, extrapolation_methods


def create_markdown_table(
    data: pd.DataFrame,
    output_path: str,
    extrapolation_info: dict[str, Any],
    *,
    alpha: float = 1 / 3,
    capital_output_ratio: float = 3.0,
    input_file: str = "china_data_raw.md",
    end_year: int = 2025,
) -> None:
    """Create comprehensive markdown output with data table and methodology documentation.

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
    headers = list(data.columns)
    rows = data.to_numpy().tolist()

    # Process extrapolation information
    notes, extrapolation_methods = _process_extrapolation_info(extrapolation_info)

    # Generate timestamp
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Render template
    tmpl = Template(MARKDOWN_TEMPLATE)
    with Path(output_path).open("w", encoding="utf-8") as f:
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
