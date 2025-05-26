"""Functions for handling metadata in the China data processor."""

import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


def _get_projected_years_from_original(
    original_df: pd.DataFrame, column_name: str, end_year: int, cutoff_year: int | None = None
) -> list[int] | None:
    """Get projected years for a column present in original data."""
    col_data = original_df[["year", column_name]].dropna()

    if len(col_data) == 0:
        return None

    last_data_year = col_data["year"].max()

    # If projection extends beyond last available data
    if last_data_year < end_year:
        if cutoff_year:
            projected_years = list(range(max(int(cutoff_year), int(last_data_year) + 1), end_year + 1))
        else:
            projected_years = list(range(int(last_data_year) + 1, end_year + 1))

        return projected_years if projected_years else None

    return None


def _get_projected_years_from_projection_df(
    processed_df: pd.DataFrame, projection_df: pd.DataFrame, column_name: str
) -> list[int] | None:
    """Get projected years for a column from projection dataframe."""
    proj_data = projection_df[["year", column_name]].dropna()
    orig_data = processed_df[["year", column_name]].dropna()

    if len(proj_data) == 0 or len(orig_data) == 0:
        return None

    # Find years that were projected (in projection but not in original)
    orig_years = set(orig_data["year"].tolist())
    projected_years = [y for y in proj_data["year"].tolist() if y not in orig_years]

    return projected_years if projected_years else None


def get_projection_metadata(
    processed_df: pd.DataFrame,
    projection_df: pd.DataFrame | None,
    original_df: pd.DataFrame,
    column_name: str,
    method_name: str,
    *,
    end_year: int,
    cutoff_year: int | None = None,
) -> dict[str, Any] | None:
    """Generate projection metadata for a specific column.

    Args:
        processed_df: The processed dataframe
        projection_df: The projection dataframe
        original_df: The original dataframe with raw data
        column_name: The column to generate metadata for
        method_name: The projection method used
        end_year: The end year for projections
        cutoff_year: Optional cutoff year to consider projections after

    Returns:
        Projection metadata if applicable, None otherwise
    """
    try:
        if column_name not in processed_df.columns:
            return None

        projected_years = None

        if column_name in original_df.columns:
            # For columns present in original data, find last non-NA year
            projected_years = _get_projected_years_from_original(original_df, column_name, end_year, cutoff_year)
        elif projection_df is not None and column_name in projection_df.columns:
            # Special case for projection dataframes
            projected_years = _get_projected_years_from_projection_df(processed_df, projection_df, column_name)

        if projected_years:
            logger.info(
                "Set %s projection method to %s for years %s-%s",
                column_name,
                method_name,
                min(projected_years),
                max(projected_years),
            )
            return {"method": method_name, "years": projected_years}

    except (KeyError, ValueError, TypeError) as e:
        logger.warning("Error generating metadata for %s: %s", column_name, e)

    return None
