"""TODO: Add module docstring."""

import logging
from typing import Any

import pandas as pd

from .processor_extrapolation_apply import _apply_methods
from .processor_extrapolation_prepare import _prepare
from .processor_extrapolation_utils import _fill_missing_key_variables

logger = logging.getLogger(__name__)


def _finalize(
    data_df: pd.DataFrame,
    years_to_add: list[int],
    raw_data: pd.DataFrame,
    cols: list[str],
    info: dict[str, Any],
    *,
    end_year: int,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Finalize extrapolation by filling missing key variables and updating metadata."""
    data_df = _fill_missing_key_variables(data_df, years_to_add)

    for col in cols:
        if col in raw_data.columns:
            raw_non_nan = raw_data[["year", col]].dropna()
            if len(raw_non_nan) == 0:
                continue
            last_actual_year = int(raw_non_nan["year"].max())
        else:
            hist = data_df[["year", col]].dropna()
            if len(hist) == 0:
                continue
            last_actual_year = int(hist["year"].max())

        if last_actual_year < end_year:
            extrap_years = list(range(last_actual_year + 1, end_year + 1))
            if extrap_years:
                method = info.get(col, {}).get("method", "Extrapolated")
                info[col] = {"method": method, "years": extrap_years}

    return data_df, info


def extrapolate_series_to_end_year(
    data: pd.DataFrame, end_year: int = 2025, raw_data: pd.DataFrame | None = None
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Extrapolate time series data to the specified end year."""
    data_df, info, years_to_add, cols = _prepare(data.copy(), end_year)
    if not years_to_add and not info:
        return data_df, info
    data_df, info = _apply_methods(data_df, years_to_add, cols, info)
    data_df, info = _finalize(
        data_df,
        years_to_add,
        raw_data if raw_data is not None else data,
        cols,
        info,
        end_year=end_year,
    )
    return data_df, info
