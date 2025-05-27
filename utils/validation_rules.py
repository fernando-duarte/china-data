"""Constants and indicator validation rules."""

from __future__ import annotations

from typing import Any

from config import Config

# Constants for validation
MIN_PROJECTION_YEAR = 2020
MAX_PROJECTION_YEAR = 2100

# Mapping of indicators to their validation requirements
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

# Generic validation rules for other indicators
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
