"""Helper utilities for data extrapolation methods.

This module provides common functionality for preparing data for extrapolation,
including validation and data structure handling.
"""

import logging
from dataclasses import dataclass

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class ExtrapolationPrepResult:
    """Result container for extrapolation data preparation.

    Attributes:
        df_result: The DataFrame containing the data to be extrapolated.
        historical_data: Historical data subset used for extrapolation, if available.
        years_to_project_filtered: Filtered list of years to project, if applicable.
        success: Whether the preparation was successful.
        message: Message describing the preparation result or any errors.
    """

    df_result: pd.DataFrame
    historical_data: pd.DataFrame | None = None
    years_to_project_filtered: list[int] | None = None
    success: bool = False
    message: str = ""


def prepare_extrapolation_data(
    df: pd.DataFrame,
    col: str,
    years_to_project: list[int],
    min_data_points: int,
    method_name: str,
) -> ExtrapolationPrepResult:
    """Prepares data for extrapolation, handling common checks.

    Returns:
        ExtrapolationPrepResult: Object containing preparation results.
    """
    df_copy = df.copy()

    if col not in df_copy.columns or df_copy[col].isna().all():
        return ExtrapolationPrepResult(df_result=df_copy, success=False, message="No data")

    historical = df_copy[["year", col]].dropna()

    if len(historical) < min_data_points:
        logger.info(
            "Insufficient data for %s on %s (need %d, have %d)",
            method_name,
            col,
            min_data_points,
            len(historical),
        )
        return ExtrapolationPrepResult(
            df_result=df_copy,
            historical_data=historical,
            success=False,
            message=f"Insufficient data (need {min_data_points})",
        )

    last_year = int(historical["year"].max())
    years_filtered = [y for y in years_to_project if y > last_year]

    if not years_filtered:
        return ExtrapolationPrepResult(
            df_result=df_copy,
            historical_data=historical,
            success=False,
            message="No years to project",
        )

    return ExtrapolationPrepResult(
        df_result=df_copy,
        historical_data=historical,
        years_to_project_filtered=years_filtered,
        success=True,
        message="",
    )
