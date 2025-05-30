"""Core validation utility functions."""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from config import Config
from utils.error_handling import DataValidationError

from .validation_rules import MAX_PROJECTION_YEAR, MIN_PROJECTION_YEAR

logger = logging.getLogger(__name__)


def validate_year_range(df: pd.DataFrame, year_column: str = "year") -> None:
    """Validate that years are within a reasonable range defined in ``Config``."""
    if year_column not in df.columns:
        raise DataValidationError(
            column=year_column,
            message=f"Year column '{year_column}' not found for range validation.",
        )
    if not pd.api.types.is_numeric_dtype(df[year_column]):
        raise DataValidationError(
            column=year_column, message=f"Year column '{year_column}' is not numeric."
        )

    min_year = df[year_column].min()
    max_year = df[year_column].max()

    if min_year < Config.MIN_YEAR:
        logger.warning(
            "Data found for year %s, which is before Config.MIN_YEAR %s",
            min_year,
            Config.MIN_YEAR,
        )
    if max_year > Config.MAX_REASONABLE_YEAR:
        logger.warning(
            "Data found for year %s, which is after Config.MAX_REASONABLE_YEAR %s",
            max_year,
            Config.MAX_REASONABLE_YEAR,
        )


def validate_numeric_values(
    df: pd.DataFrame,
    column: str,
    *,
    min_value: float | None = None,
    max_value: float | None = None,
    allow_na: bool = True,
    strict_positive: bool = False,
) -> None:
    """Validate numeric column values against optional min/max bounds and strict positivity."""
    if column not in df.columns:
        # This column might not be present in all dataframes, so just log and return
        logger.debug("Column '%s' not found for numeric validation, skipping.", column)
        return

    if not pd.api.types.is_numeric_dtype(df[column]):
        raise DataValidationError(column=column, message=f"Column '{column}' is not numeric.")

    series_to_validate = df[column].dropna() if allow_na else df[column]
    if series_to_validate.empty and not allow_na and not df[column].empty:
        raise DataValidationError(
            column=column,
            message=f"Column '{column}' contains only NA values but allow_na is False.",
        )
    if series_to_validate.empty:  # if all were NA and allow_na is True
        return

    if strict_positive and (series_to_validate <= 0).any():
        invalid_values = series_to_validate[series_to_validate <= 0]
        raise DataValidationError(
            column=column,
            message=(
                f"Column '{column}' must be strictly positive. "
                f"Found: {invalid_values.head().tolist()}"
            ),
            data_info=f"Affected rows count: {len(invalid_values)}",
        )

    if min_value is not None and (series_to_validate < min_value).any():
        invalid_values = series_to_validate[series_to_validate < min_value]
        raise DataValidationError(
            column=column,
            message=(
                f"Values in column '{column}' are below minimum {min_value}. "
                f"Found: {invalid_values.head().tolist()}"
            ),
            data_info=f"Affected rows count: {len(invalid_values)}",
        )

    if max_value is not None and (series_to_validate > max_value).any():
        invalid_values = series_to_validate[series_to_validate > max_value]
        raise DataValidationError(
            column=column,
            message=(
                f"Values in column '{column}' are above maximum {max_value}. "
                f"Found: {invalid_values.head().tolist()}"
            ),
            data_info=f"Affected rows count: {len(invalid_values)}",
        )


def validate_dataframe_with_rules(
    df: pd.DataFrame,
    rules: dict[str, dict[str, Any]],
    year_column: str = "year",
) -> None:
    """Validate entire ``DataFrame`` based on a dictionary of rules for specific columns."""
    if not isinstance(df, pd.DataFrame):
        raise DataValidationError(column="dataframe", message="Input is not a pandas DataFrame.")

    if df.empty:
        logger.warning("DataFrame is empty, skipping rule-based validation.")
        return

    validate_year_range(df, year_column)

    for column_name, rule in rules.items():
        if column_name in df.columns:
            logger.debug("Validating column '%s' with rule: %s", column_name, rule)
            validate_numeric_values(
                df,
                column_name,
                min_value=rule.get("min_value"),
                max_value=rule.get("max_value"),
                allow_na=rule.get("allow_na", True),
                strict_positive=rule.get("strict_positive", False),
            )
        else:
            # This is not necessarily an error if a source doesn't provide all possible indicators
            logger.debug(
                "Column '%s' not found in DataFrame for validation, skipping.", column_name
            )


def validate_series(
    series_to_validate: pd.Series[float],
    strict_positive: bool = False,
    min_value: float | None = None,
    max_value: float | None = None,
) -> bool:
    """Validate a data series against specified criteria."""
    if series_to_validate.empty:
        return False

    if series_to_validate.isna().any():
        logger.warning("Found %s NaN values", series_to_validate.isna().sum())
        return False

    if strict_positive and (series_to_validate <= 0).any():
        invalid_values = series_to_validate[series_to_validate <= 0]
        logger.warning("Found %s non-positive values", len(invalid_values))
        return False

    if min_value is not None and (series_to_validate < min_value).any():
        invalid_values = series_to_validate[series_to_validate < min_value]
        logger.warning("Found %s values below minimum %s", len(invalid_values), min_value)
        return False

    if max_value is not None and (series_to_validate > max_value).any():
        invalid_values = series_to_validate[series_to_validate > max_value]
        logger.warning("Found %s values above maximum %s", len(invalid_values), max_value)
        return False

    return True


def validate_alpha(alpha: float) -> bool:
    """Validate the alpha parameter (capital share in production function)."""
    return 0 < alpha < 1


def validate_capital_output_ratio(ratio: float) -> bool:
    """Validate the capital-output ratio."""
    return ratio > 0


def validate_end_year(year: int) -> bool:
    """Validate the end year for projections."""
    return MIN_PROJECTION_YEAR <= year <= MAX_PROJECTION_YEAR
