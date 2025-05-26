"""Fallback data loader for China economic data.

This module provides functionality to load data from existing china_data_raw.md files
as fallback when primary data sources are unavailable.
"""

import logging
from pathlib import Path

import pandas as pd

from config import Config
from utils.error_handling import DataValidationError, FileOperationError

logger = logging.getLogger(__name__)

# Constants
MIN_TABLE_LINES = 3


def _find_table_boundaries(lines: list[str]) -> tuple[int | None, int | None]:
    """Find the start and end of the markdown table.

    Args:
        lines: List of lines from the file

    Returns:
        Tuple of (table_start, table_end) indices
    """
    table_start = None
    table_end = None

    for i, line in enumerate(lines):
        if line.startswith("| Year |"):
            table_start = i
        elif table_start is not None and line.strip() == "" and i > table_start + 2:
            table_end = i
            break

    return table_start, table_end


def _parse_table_data(table_lines: list[str], table_start: int) -> tuple[list[str], list[list[str]], list[str]]:
    """Parse table data from markdown lines.

    Args:
        table_lines: Lines containing the table
        table_start: Starting line number for error reporting

    Returns:
        Tuple of (headers, data_rows, parse_errors)
    """
    headers = [h.strip() for h in table_lines[0].split("|")[1:-1]]
    data_lines = table_lines[2:]  # Skip separator line
    data = []
    parse_errors = []

    for line_num, line in enumerate(data_lines, start=table_start + 3):
        if line.strip():
            try:
                values = [v.strip() for v in line.split("|")[1:-1]]
                if len(values) != len(headers):
                    error_msg = f"Line {line_num}: Expected {len(headers)} columns, got {len(values)}"
                    parse_errors.append(error_msg)
                    continue
                data.append(values)
            except (ValueError, IndexError) as e:
                parse_errors.append(f"Line {line_num}: Parse error - {e!s}")

    return headers, data, parse_errors


def _log_parse_errors(parse_errors: list[str]) -> None:
    """Log parse errors with truncation if too many.

    Args:
        parse_errors: List of error messages
    """
    if not parse_errors:
        return

    max_errors = Config.MAX_LOG_ERRORS_DISPLAYED
    logger.warning("Parse errors in fallback file: %s", parse_errors[:max_errors])

    if len(parse_errors) > max_errors:
        additional_errors = len(parse_errors) - max_errors
        logger.warning("... and %d more parse errors", additional_errors)


def _read_and_parse_markdown_table(file_path: Path) -> pd.DataFrame:
    """Parse markdown table from fallback file into DataFrame."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except OSError as e:
        raise FileOperationError(
            operation="read", filepath=str(file_path), message="Failed to read fallback file", original_error=e
        ) from e

    if not content.strip():
        raise DataValidationError(
            column="fallback_file",
            message="Fallback file is empty",
            data_info=f"File: {file_path}",
        )

    lines = content.split("\n")
    table_start, table_end = _find_table_boundaries(lines)

    if table_start is None:
        raise DataValidationError(
            column="fallback_file",
            message="Could not find data table in fallback file",
            data_info=f"File: {file_path}, Lines: {len(lines)}",
        )

    table_lines = lines[table_start:table_end]
    if len(table_lines) < MIN_TABLE_LINES:
        raise DataValidationError(
            column="fallback_file",
            message="Insufficient table data in fallback file",
            data_info=f"Table lines: {len(table_lines)}",
        )

    headers, data, parse_errors = _parse_table_data(table_lines, table_start)
    _log_parse_errors(parse_errors)

    if not data:
        raise DataValidationError(
            column="fallback_file",
            message="No valid data rows found in fallback file",
            data_info=f"Parse errors: {len(parse_errors)}",
        )

    return pd.DataFrame(data, columns=headers)


def _convert_column_to_numeric(fallback_data: pd.DataFrame, col: str) -> str | None:
    """Convert a single column to numeric, returning error message if failed.

    Args:
        fallback_data: DataFrame to modify
        col: Column name to convert

    Returns:
        Error message if conversion failed, None if successful
    """
    try:
        if col != "Year":
            cleaned = fallback_data[col].replace(["N/A", "nan", "NaN", ""], pd.NA)
            fallback_data[col] = pd.to_numeric(cleaned, errors="coerce")
        else:
            fallback_data[col] = pd.to_numeric(fallback_data[col], errors="coerce")
    except (ValueError, TypeError) as e:
        return str(e)

    return None


def _convert_to_numeric(fallback_data: pd.DataFrame) -> pd.DataFrame:
    """Convert DataFrame columns to numeric types with error tracking."""
    conversion_errors = {}

    for col in fallback_data.columns:
        error_msg = _convert_column_to_numeric(fallback_data, col)
        if error_msg:
            conversion_errors[col] = error_msg

    if conversion_errors:
        logger.warning("Numeric conversion errors in fallback data: %s", conversion_errors)

    # Validate Year column
    if "Year" not in fallback_data.columns:
        raise DataValidationError(
            column="Year",
            message="Year column missing from fallback data",
            data_info=f"Available columns: {list(fallback_data.columns)}",
        )

    valid_years = fallback_data["Year"].dropna()
    if len(valid_years) == 0:
        raise DataValidationError(
            column="Year",
            message="No valid years found in fallback data",
            data_info=f"Year column values: {fallback_data['Year'].head().tolist()}",
        )

    return fallback_data


def _extract_wdi_indicators(fallback_data: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Extract WDI indicators from fallback data.

    Args:
        fallback_data: DataFrame with fallback data

    Returns:
        Dictionary of WDI indicator DataFrames
    """
    result = {}

    # Get WDI indicators mapping from config
    raw_data_mapping = Config.get_raw_data_column_map()
    # Filter for WDI indicators only (exclude PWT columns)
    wdi_mapping = {
        display: internal
        for internal, display in raw_data_mapping.items()
        if not display.startswith("PWT") and display != "Year"
    }

    for col, name in wdi_mapping.items():
        if col in fallback_data.columns:
            indicator_df = fallback_data[["Year", col]].rename(columns={"Year": "year", col: name}).dropna()
            if len(indicator_df) > 0:
                result[name] = indicator_df
                logger.debug("Loaded %d rows for %s from fallback", len(indicator_df), name)

    return result


def _extract_tax_data(fallback_data: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Extract tax data from fallback data.

    Args:
        fallback_data: DataFrame with fallback data

    Returns:
        Dictionary with tax data if available
    """
    result = {}

    if "Tax Revenue (% of GDP)" in fallback_data.columns:
        tax_df = (
            fallback_data[["Year", "Tax Revenue (% of GDP)"]]
            .rename(columns={"Year": "year", "Tax Revenue (% of GDP)": "TAX_pct_GDP"})
            .dropna()
        )
        if len(tax_df) > 0:
            result["TAX_pct_GDP"] = tax_df
            logger.debug("Loaded %d rows for TAX_pct_GDP from fallback", len(tax_df))

    return result


def _extract_pwt_data(fallback_data: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Extract PWT data from fallback data.

    Args:
        fallback_data: DataFrame with fallback data

    Returns:
        Dictionary with PWT data if available
    """
    result = {}

    # Get PWT data mapping from config
    raw_data_mapping = Config.get_raw_data_column_map()
    pwt_rename_map = {display: internal for internal, display in raw_data_mapping.items() if display.startswith("PWT")}
    pwt_cols = list(pwt_rename_map.keys())

    pwt_available = [col for col in pwt_cols if col in fallback_data.columns]
    if pwt_available:
        cols_to_select = ["Year", *pwt_available]
        rename_dict = {k: v for k, v in pwt_rename_map.items() if k in cols_to_select}
        pwt_df = (
            fallback_data[cols_to_select]
            .rename(columns=rename_dict)
            .dropna(subset=[rename_dict[c] for c in pwt_available], how="all")
        )
        if len(pwt_df) > 0:
            result["PWT"] = pwt_df
            logger.debug("Loaded %d rows for PWT from fallback", len(pwt_df))

    return result


def _split_into_indicators(fallback_data: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Split DataFrame into separate dataframes by indicator type."""
    result = {}

    # Extract different types of indicators
    result.update(_extract_wdi_indicators(fallback_data))
    result.update(_extract_tax_data(fallback_data))
    result.update(_extract_pwt_data(fallback_data))

    return result
