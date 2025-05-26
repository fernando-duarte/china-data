"""Data validation utilities."""

import logging
from typing import Any

import pandas as pd

from config import Config
from utils.error_handling import DataValidationError

logger = logging.getLogger(__name__)


def validate_year_range(df: pd.DataFrame, year_column: str = "year") -> None:
    """Validate that years are within a reasonable range defined in Config."""
    if year_column not in df.columns:
        raise DataValidationError(
            column=year_column, message=f"Year column '{year_column}' not found for range validation."
        )
    if not pd.api.types.is_numeric_dtype(df[year_column]):
        raise DataValidationError(column=year_column, message=f"Year column '{year_column}' is not numeric.")

    min_year = df[year_column].min()
    max_year = df[year_column].max()

    if min_year < Config.MIN_YEAR:
        logger.warning(f"Data found for year {min_year}, which is before Config.MIN_YEAR {Config.MIN_YEAR}")
    if max_year > Config.MAX_REASONABLE_YEAR:
        logger.warning(
            f"Data found for year {max_year}, which is after Config.MAX_REASONABLE_YEAR {Config.MAX_REASONABLE_YEAR}"
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
        logger.debug(f"Column '{column}' not found for numeric validation, skipping.")
        return

    if not pd.api.types.is_numeric_dtype(df[column]):
        raise DataValidationError(column=column, message=f"Column '{column}' is not numeric.")

    series_to_validate = df[column].dropna() if allow_na else df[column]
    if series_to_validate.empty and not allow_na and not df[column].empty:
        raise DataValidationError(
            column=column, message=f"Column '{column}' contains only NA values but allow_na is False."
        )
    if series_to_validate.empty:  # if all were NA and allow_na is True
        return

    if strict_positive and (series_to_validate <= 0).any():
        invalid_values = series_to_validate[series_to_validate <= 0]
        raise DataValidationError(
            column=column,
            message=f"Column '{column}' must be strictly positive. Found: {invalid_values.head().tolist()}",
            data_info=f"Affected rows count: {len(invalid_values)}",
        )

    if min_value is not None and (series_to_validate < min_value).any():
        invalid_values = series_to_validate[series_to_validate < min_value]
        raise DataValidationError(
            column=column,
            message=(
                f"Values in column '{column}' are below minimum {min_value}. Found: {invalid_values.head().tolist()}"
            ),
            data_info=f"Affected rows count: {len(invalid_values)}",
        )

    if max_value is not None and (series_to_validate > max_value).any():
        invalid_values = series_to_validate[series_to_validate > max_value]
        raise DataValidationError(
            column=column,
            message=(
                f"Values in column '{column}' are above maximum {max_value}. Found: {invalid_values.head().tolist()}"
            ),
            data_info=f"Affected rows count: {len(invalid_values)}",
        )


# Add more specific validation functions based on data source documentation and tests
# For WDI (World Development Indicators)
# GDP (NY.GDP.MKTP.CD): Must be positive. No specific max, but outliers can be checked.
# Population (SP.POP.TOTL): Must be positive.
# FDI (% of GDP) (BX.KLT.DINV.WD.GD.ZS): Can be negative, usually within -100 to 100, but large fluctuations possible.

# For PWT (Penn World Table)
# rgdpo (Output-side real GDP at current PPPs): Must be positive.
# rkna (Capital stock at current PPPs): Must be positive.
# hc (Human capital index): Typically between 1 and 4-5.
# pl_gdpo (Price level of GDP): Typically positive, relative to US.

INDICATOR_VALIDATION_RULES: dict[str, dict[str, Any]] = {
    # WDI original codes (before renaming)
    "NY_GDP_MKTP_CD": {"strict_positive": True},
    "NE_CON_PRVT_CD": {"strict_positive": True},  # Consumption
    "NE_CON_GOVT_CD": {"strict_positive": True},  # Government Spending
    "NE_GDI_TOTL_CD": {"strict_positive": True},  # Investment
    "NE_EXP_GNFS_CD": {"strict_positive": True},  # Exports
    "NE_IMP_GNFS_CD": {"strict_positive": True},  # Imports
    "SP_POP_TOTL": {
        "strict_positive": True,
        "min_value": Config.POPULATION_MIN,
    },  # Population, min 1000 to be reasonable
    "SL_TLF_TOTL_IN": {"strict_positive": True, "min_value": Config.LABOR_FORCE_MIN},  # Labor Force
    "BX_KLT_DINV_WD_GD_ZS": {
        "min_value": Config.FDI_PCT_GDP_MIN,
        "max_value": Config.FDI_PCT_GDP_MAX,
    },  # FDI % GDP, wider range for safety
    # PWT original column names (before renaming in merged_data)
    "rgdpo": {"strict_positive": True},
    "rkna": {"strict_positive": True},
    "hc": {"min_value": Config.HUMAN_CAPITAL_MIN, "max_value": Config.HUMAN_CAPITAL_MAX},  # Human Capital Index
    "pl_gdpo": {"strict_positive": True},  # Price Level
    "cgdpo": {"strict_positive": True},  # Consumption GDP Output side
    # IMF data (already renamed)
    "TAX_pct_GDP": {"min_value": Config.TAX_PCT_GDP_MIN, "max_value": Config.TAX_PCT_GDP_MAX},  # Tax as % of GDP
}


def validate_dataframe_with_rules(
    df: pd.DataFrame, rules: dict[str, dict[str, Any]], year_column: str = "year"
) -> None:
    """Validate entire DataFrame based on a dictionary of rules for specific columns."""
    if not isinstance(df, pd.DataFrame):
        raise DataValidationError(column="dataframe", message="Input is not a pandas DataFrame.")

    if df.empty:
        logger.warning("DataFrame is empty, skipping rule-based validation.")
        return

    validate_year_range(df, year_column)

    for column_name, rule in rules.items():
        if column_name in df.columns:
            logger.debug(f"Validating column '{column_name}' with rule: {rule}")
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
            logger.debug(f"Column '{column_name}' not found in DataFrame for validation, skipping.")


def validate_series(
    series_to_validate: pd.Series[float],
    strict_positive: bool = False,
    min_value: float | None = None,
    max_value: float | None = None,
) -> bool:
    """Validate a data series against specified criteria.

    Args:
        series_to_validate: Series to validate
        strict_positive: Whether values must be strictly positive
        min_value: Minimum allowed value (inclusive)
        max_value: Maximum allowed value (inclusive)

    Returns:
        bool: True if validation passes, False otherwise
    """
    if series_to_validate.empty:
        return False

    # Check for NaN values
    if series_to_validate.isna().any():
        logger.warning(f"Found {series_to_validate.isna().sum()} NaN values")
        return False

    # Check for strictly positive values if required
    if strict_positive and (series_to_validate <= 0).any():
        invalid_values = series_to_validate[series_to_validate <= 0]
        logger.warning(f"Found {len(invalid_values)} non-positive values")
        return False

    # Check minimum value if specified
    if min_value is not None and (series_to_validate < min_value).any():
        invalid_values = series_to_validate[series_to_validate < min_value]
        logger.warning(f"Found {len(invalid_values)} values below minimum {min_value}")
        return False

    # Check maximum value if specified
    if max_value is not None and (series_to_validate > max_value).any():
        invalid_values = series_to_validate[series_to_validate > max_value]
        logger.warning(f"Found {len(invalid_values)} values above maximum {max_value}")
        return False

    return True


# Validation rules for different indicators
VALIDATION_RULES: dict[str, dict[str, bool | float | None]] = {
    # Population must be positive and reasonably large
    "SP_POP_TOTL": {"strict_positive": True, "min_value": Config.POPULATION_MIN},
    # Labor force must be positive and reasonably large
    "SL_TLF_TOTL_IN": {"strict_positive": True, "min_value": Config.LABOR_FORCE_MIN},
    # FDI (% of GDP) can be negative but within reasonable bounds
    "BX_KLT_DINV_WD_GD_ZS": {"min_value": Config.FDI_PCT_GDP_MIN, "max_value": Config.FDI_PCT_GDP_MAX},
    # Human capital index has typical bounds
    "hc": {"min_value": Config.HUMAN_CAPITAL_MIN, "max_value": Config.HUMAN_CAPITAL_MAX},
    # Tax revenue as % of GDP must be between 0 and 100
    "TAX_pct_GDP": {"min_value": Config.TAX_PCT_GDP_MIN, "max_value": Config.TAX_PCT_GDP_MAX},
}


def validate_alpha(alpha: float) -> bool:
    """Validate the alpha parameter (capital share in production function)."""
    return 0 < alpha < 1


def validate_capital_output_ratio(ratio: float) -> bool:
    """Validate the capital-output ratio."""
    return ratio > 0


def validate_end_year(year: int) -> bool:
    """Validate the end year for projections."""
    return 2020 <= year <= 2100
