"""Module for loading and preprocessing economic data for the China model."""

import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from config import Config
from utils import find_file
from utils.data_sources.imf_loader import load_imf_tax_data
from utils.path_constants import get_search_locations_relative_to_root

logger = logging.getLogger(__name__)


def _find_table_header(lines: list[str]) -> int:
    """Find the index of the table header in markdown lines."""
    for i, line in enumerate(lines):
        if "| Year |" in line and "GDP" in line:
            return i
    msg = "Could not find table header in the markdown file."
    raise ValueError(msg)


def _parse_header(header_line: str) -> list[str]:
    """Parse and clean the header line from markdown table."""
    # Clean up header line by removing leading/trailing |
    header_line = header_line.removeprefix("|")
    header_line = header_line.removesuffix("|")

    # Split by | and strip whitespace
    return [h.strip() for h in header_line.split("|") if h.strip()]


def _map_column_names(header: list[str]) -> list[str]:
    """Map display column names to internal names using config."""
    # Get column mapping from config (display name -> internal name)
    mapping = Config.get_raw_data_column_map()
    # Invert the mapping since we need display -> internal
    mapping = {v: k for k, v in mapping.items()}

    return [mapping.get(col, col) for col in header]


def _process_cell_value(value: str, column_name: str, is_year_column: bool) -> Any:
    """Process a single cell value based on its column type."""
    if is_year_column:
        return int(value)

    if value == "N/A":
        return np.nan

    if column_name in ["FDI_pct_GDP", "TAX_pct_GDP"]:
        return float(value) if value != "N/A" else np.nan

    if column_name in ["POP", "LF"]:
        return float(value.replace(",", "")) if value != "N/A" else np.nan

    return float(value) if value != "N/A" else np.nan


def _parse_data_rows(
    lines: list[str], start_idx: int, header: list[str], renamed_columns: list[str]
) -> list[list[Any]]:
    """Parse data rows from markdown table."""
    data = []
    for i in range(start_idx, len(lines)):
        line = lines[i].strip()
        if not line or line.startswith("**Notes"):
            break

        row = [c.strip() for c in line.split("|") if c.strip()]
        if len(row) == len(header):
            processed = []
            for j, value in enumerate(row):
                is_year_column = j == 0
                processed_value = _process_cell_value(value, renamed_columns[j], is_year_column)
                processed.append(processed_value)
            data.append(processed)

    return data


def load_raw_data(input_file: str = "china_data_raw.md") -> pd.DataFrame:
    """Load raw data from a markdown table file.

    This file is expected to be in one of the standard output locations.

    Args:
        input_file: Name of the input file

    Returns:
        DataFrame containing the raw data

    Raises:
        FileNotFoundError: If the input file cannot be found
    """
    # Use the common find_file utility to locate the input file
    possible_locations_relative = get_search_locations_relative_to_root()["output_files"]

    md_file = find_file(input_file, possible_locations_relative)

    if md_file is None:
        msg = f"Raw data file not found: {input_file} in any of the expected locations."
        raise FileNotFoundError(msg)

    with Path(md_file).open(encoding="utf-8") as f:
        lines = f.readlines()

    # Find and parse header
    header_idx = _find_table_header(lines)
    header_line = lines[header_idx].strip()
    header = _parse_header(header_line)
    renamed_columns = _map_column_names(header)

    # Parse data rows
    data_start_idx = header_idx + 2
    data = _parse_data_rows(lines, data_start_idx, header, renamed_columns)

    return pd.DataFrame(data, columns=renamed_columns)


def load_imf_tax_revenue_data() -> pd.DataFrame:
    """Load IMF tax revenue data from CSV file.

    This file is expected to be in one of the standard input locations.

    Returns:
        DataFrame containing the tax revenue data
    """
    # Use the dedicated IMF loader module
    return load_imf_tax_data()
