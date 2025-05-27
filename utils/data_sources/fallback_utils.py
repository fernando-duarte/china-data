"""Fallback data loader for China economic data.

This module provides functionality to load data from existing ``china_data_raw.md`` files
as fallback when primary data sources are unavailable. It re-exports helper
functions from the ``fallback_parser`` and ``fallback_extractors`` modules.
"""

from .fallback_extractors import (
    _extract_pwt_data,
    _extract_tax_data,
    _extract_wdi_indicators,
    _split_into_indicators,
)
from .fallback_parser import (
    MIN_TABLE_LINES,
    _convert_column_to_numeric,
    _convert_to_numeric,
    _find_table_boundaries,
    _log_parse_errors,
    _parse_table_data,
    _read_and_parse_markdown_table,
)

__all__ = [
    "MIN_TABLE_LINES",
    "_convert_column_to_numeric",
    "_convert_to_numeric",
    "_extract_pwt_data",
    "_extract_tax_data",
    "_extract_wdi_indicators",
    "_find_table_boundaries",
    "_log_parse_errors",
    "_parse_table_data",
    "_read_and_parse_markdown_table",
    "_split_into_indicators",
]
