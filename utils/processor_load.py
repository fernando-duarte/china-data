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

    header_idx = None
    for i, line in enumerate(lines):
        if "| Year |" in line and "GDP" in line:
            header_idx = i
            break

    if header_idx is None:
        msg = "Could not find table header in the markdown file."
        raise ValueError(msg)

    header_line = lines[header_idx].strip()
    # Clean up header line by removing leading/trailing |
    if header_line.startswith("|"):
        header_line = header_line[1:]
    if header_line.endswith("|"):
        header_line = header_line[:-1]

    # Split by | and strip whitespace
    header = [h.strip() for h in header_line.split("|") if h.strip()]

    # Get column mapping from config (display name -> internal name)
    mapping = Config.get_raw_data_column_map()
    # Invert the mapping since we need display -> internal
    mapping = {v: k for k, v in mapping.items()}

    renamed = []
    for col in header:
        mapped_col = mapping.get(col, col)
        renamed.append(mapped_col)
    data_start_idx = header_idx + 2
    data = []
    for i in range(data_start_idx, len(lines)):
        line = lines[i].strip()
        if not line or line.startswith("**Notes"):
            break
        row = [c.strip() for c in line.split("|") if c.strip()]
        if len(row) == len(header):
            processed: list[Any] = []
            for j, value in enumerate(row):
                if j == 0:
                    processed.append(int(value))
                elif value == "N/A":
                    processed.append(np.nan)
                elif renamed[j] in ["FDI_pct_GDP", "TAX_pct_GDP"]:
                    processed.append(float(value) if value != "N/A" else np.nan)
                elif renamed[j] in ["POP", "LF"]:
                    processed.append(float(value.replace(",", "")) if value != "N/A" else np.nan)
                else:
                    processed.append(float(value) if value != "N/A" else np.nan)
            data.append(processed)
    return pd.DataFrame(data, columns=renamed)


def load_imf_tax_revenue_data() -> pd.DataFrame:
    """Load IMF tax revenue data from CSV file.
    
    This file is expected to be in one of the standard input locations.

    Returns:
        DataFrame containing the tax revenue data
    """
    # Use the dedicated IMF loader module
    return load_imf_tax_data()
