"""
Fallback data loader for China economic data.

This module provides functionality to load data from existing china_data_raw.md files
as fallback when primary data sources are unavailable.
"""

import logging
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from config import Config
from utils.error_handling import DataValidationError, FileOperationError, log_error_with_context
from utils.validation_utils import INDICATOR_VALIDATION_RULES, validate_dataframe_with_rules

logger = logging.getLogger(__name__)


def _read_and_parse_markdown_table(file_path: Path) -> pd.DataFrame:
    """Parse markdown table from fallback file into DataFrame."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except (IOError, OSError) as e:
        raise FileOperationError(
            operation="read", filepath=str(file_path), message="Failed to read fallback file", original_error=e
        )

    if not content.strip():
        raise DataValidationError(column="fallback_file", message="Fallback file is empty", data_info=f"File: {file_path}")

    lines = content.split("\n")
    table_start = None
    table_end = None

    for i, line in enumerate(lines):
        if line.startswith("| Year |"):
            table_start = i
        elif table_start is not None and line.strip() == "" and i > table_start + 2:
            table_end = i
            break

    if table_start is None:
        raise DataValidationError(
            column="fallback_file",
            message="Could not find data table in fallback file",
            data_info=f"File: {file_path}, Lines: {len(lines)}",
        )

    table_lines = lines[table_start:table_end]
    if len(table_lines) < 3:
        raise DataValidationError(
            column="fallback_file",
            message="Insufficient table data in fallback file",
            data_info=f"Table lines: {len(table_lines)}",
        )

    headers = [h.strip() for h in table_lines[0].split("|")[1:-1]]
    data_lines = table_lines[2:]  # Skip separator line
    data = []
    parse_errors = []

    for line_num, line in enumerate(data_lines, start=table_start + 3):
        if line.strip():
            try:
                values = [v.strip() for v in line.split("|")[1:-1]]
                if len(values) != len(headers):
                    parse_errors.append(f"Line {line_num}: Expected {len(headers)} columns, got {len(values)}")
                    continue
                data.append(values)
            except Exception as e:
                parse_errors.append(f"Line {line_num}: Parse error - {str(e)}")

    if parse_errors:
        logger.warning(f"Parse errors in fallback file: {parse_errors[:Config.MAX_LOG_ERRORS_DISPLAYED]}")
        if len(parse_errors) > Config.MAX_LOG_ERRORS_DISPLAYED:
            logger.warning(f"... and {len(parse_errors) - Config.MAX_LOG_ERRORS_DISPLAYED} more parse errors")

    if not data:
        raise DataValidationError(
            column="fallback_file", message="No valid data rows found in fallback file", data_info=f"Parse errors: {len(parse_errors)}"
        )

    return pd.DataFrame(data, columns=headers)


def _convert_to_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """Convert DataFrame columns to numeric types with error tracking."""
    conversion_errors = {}
    for col in df.columns:
        if col != "Year":
            try:
                cleaned = df[col].replace(["N/A", "nan", "NaN", ""], pd.NA)
                df[col] = pd.to_numeric(cleaned, errors="coerce")
            except Exception as e:
                conversion_errors[col] = str(e)
        else:
            try:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            except Exception as e:
                conversion_errors[col] = str(e)

    if conversion_errors:
        logger.warning(f"Numeric conversion errors in fallback data: {conversion_errors}")

    # Validate Year column
    if "Year" not in df.columns:
        raise DataValidationError(
            column="Year", message="Year column missing from fallback data", data_info=f"Available columns: {list(df.columns)}"
        )

    valid_years = df["Year"].dropna()
    if len(valid_years) == 0:
        raise DataValidationError(
            column="Year", message="No valid years found in fallback data", data_info=f"Year column values: {df['Year'].head().tolist()}"
        )

    return df


def _split_into_indicators(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Split DataFrame into separate dataframes by indicator type."""
    result = {}

    # WDI indicators mapping
    wdi_mapping = {
        "GDP (USD)": "GDP_USD",
        "Consumption (USD)": "C_USD",
        "Government (USD)": "G_USD",
        "Investment (USD)": "I_USD",
        "Exports (USD)": "X_USD",
        "Imports (USD)": "M_USD",
        "FDI (% of GDP)": "FDI_pct_GDP",
        "Population": "POP",
        "Labor Force": "LF",
    }

    for col, name in wdi_mapping.items():
        if col in df.columns:
            indicator_df = df[["Year", col]].rename(columns={"Year": "year", col: name}).dropna()
            if len(indicator_df) > 0:
                result[name] = indicator_df
                logger.debug(f"Loaded {len(indicator_df)} rows for {name} from fallback")

    # Tax data
    if "Tax Revenue (% of GDP)" in df.columns:
        tax_df = df[["Year", "Tax Revenue (% of GDP)"]].rename(columns={"Year": "year", "Tax Revenue (% of GDP)": "TAX_pct_GDP"}).dropna()
        if len(tax_df) > 0:
            result["TAX_pct_GDP"] = tax_df
            logger.debug(f"Loaded {len(tax_df)} rows for TAX_pct_GDP from fallback")

    # PWT data processing
    pwt_cols = ["PWT rgdpo", "PWT rkna", "PWT pl_gdpo", "PWT cgdpo", "PWT hc"]
    pwt_rename_map = {"PWT rgdpo": "rgdpo", "PWT rkna": "rkna", "PWT pl_gdpo": "pl_gdpo", "PWT cgdpo": "cgdpo", "PWT hc": "hc"}

    pwt_available = [col for col in pwt_cols if col in df.columns]
    if pwt_available:
        cols_to_select = ["Year"] + pwt_available
        rename_dict = {k: v for k, v in pwt_rename_map.items() if k in cols_to_select}
        pwt_df = df[cols_to_select].rename(columns=rename_dict).dropna(subset=[rename_dict[c] for c in pwt_available], how="all")
        if len(pwt_df) > 0:
            result["PWT"] = pwt_df
            logger.debug(f"Loaded {len(pwt_df)} rows for PWT from fallback")

    return result


def load_fallback_data(output_dir: str) -> Optional[Dict[str, pd.DataFrame]]:
    """
    Load data from existing china_data_raw.md file as fallback.

    Args:
        output_dir: Directory where china_data_raw.md is located

    Returns:
        Dictionary of dataframes by indicator name, or None if file not found

    Raises:
        FileOperationError: If file operations fail
        DataValidationError: If data validation fails
    """
    fallback_file = Path(output_dir) / "china_data_raw.md"
    if not fallback_file.exists():
        logger.warning(f"Fallback file {fallback_file} not found")
        return None

    logger.info(f"Loading fallback data from {fallback_file}")

    try:
        # Parse markdown table
        df = _read_and_parse_markdown_table(fallback_file)

        # Convert to numeric types
        df = _convert_to_numeric(df)

        # Split into indicators
        result = _split_into_indicators(df)

        if not result:
            raise DataValidationError(
                column="fallback_data",
                message="No valid indicators found in fallback data",
                data_info=f"Available columns: {list(df.columns)}",
            )

        logger.info(f"Successfully loaded fallback data with {len(result)} indicators")
        return result

    except (FileOperationError, DataValidationError):
        raise
    except Exception as e:
        log_error_with_context(logger, "Unexpected error loading fallback data", e, context={"fallback_file": fallback_file})
        raise FileOperationError(
            operation="parse", filepath=str(fallback_file), message="Unexpected error during fallback data parsing", original_error=e
        )
