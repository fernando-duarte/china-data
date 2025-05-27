"""Data validation utilities."""

from .validation_core import (
    validate_alpha,
    validate_capital_output_ratio,
    validate_dataframe_with_rules,
    validate_end_year,
    validate_numeric_values,
    validate_series,
    validate_year_range,
)
from .validation_rules import (
    INDICATOR_VALIDATION_RULES,
    MAX_PROJECTION_YEAR,
    MIN_PROJECTION_YEAR,
    VALIDATION_RULES,
)

__all__ = [
    "INDICATOR_VALIDATION_RULES",
    "MAX_PROJECTION_YEAR",
    "MIN_PROJECTION_YEAR",
    "VALIDATION_RULES",
    "validate_alpha",
    "validate_capital_output_ratio",
    "validate_dataframe_with_rules",
    "validate_end_year",
    "validate_numeric_values",
    "validate_series",
    "validate_year_range",
]
