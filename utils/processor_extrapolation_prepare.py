"""Data preparation utilities for series extrapolation."""

from typing import Any

import numpy as np
import pandas as pd

from .processor_extrapolation_constants import GDP_COMPONENT_COLUMNS


def _prepare(
    data_df: pd.DataFrame, end_year: int
) -> tuple[pd.DataFrame, dict[str, Any], list[int], list[str]]:
    """Prepare data for extrapolation by adding missing years and identifying columns."""
    max_year = data_df.year.max()
    if max_year >= end_year:
        missing = False
        key = [*GDP_COMPONENT_COLUMNS, "POP_mn", "LF_mn"]
        for year in [end_year - 1, end_year]:
            for var in key:
                if var in data_df.columns and pd.isna(
                    data_df.loc[data_df.year == year, var].to_numpy()[0]
                ):
                    missing = True
                    break
            if missing:
                break
        if not missing:
            return data_df, {}, [], []
        years_to_add = [end_year - 1, end_year]
    else:
        years_to_add = list(range(max_year + 1, end_year + 1))
    new_years_df = pd.DataFrame({"year": years_to_add})
    updated_df = pd.concat([data_df, new_years_df], ignore_index=True)
    numeric_cols = updated_df.select_dtypes(include=[np.number]).columns.tolist()
    cols_to_extrapolate = [c for c in numeric_cols if c != "year"]
    return updated_df, {}, years_to_add, cols_to_extrapolate
