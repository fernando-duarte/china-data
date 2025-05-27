"""Functions for handling output operations in the China data processor."""

import logging
from pathlib import Path
from typing import Any

import pandas as pd

from utils.output.markdown_generator import create_markdown_table

logger = logging.getLogger(__name__)


def prepare_output_data(
    processed_df: pd.DataFrame, output_columns: list[str], column_map: dict[str, str]
) -> pd.DataFrame:
    """Prepare data for output by selecting and renaming columns.

    Args:
        processed_df: The processed dataframe
        output_columns: List of columns to include in output
        column_map: Mapping from internal column names to output column names

    Returns:
        DataFrame ready for output
    """
    # Check which output columns are missing
    missing_columns = [col for col in output_columns if col not in processed_df.columns]

    if missing_columns:
        logger.warning("Some output columns are missing from the data: %s", missing_columns)

    logger.info("Using %s output columns: %s", len(output_columns), output_columns)

    # Check for duplicate years
    duplicated_years: list[int] = []
    if "year" in processed_df.columns:
        duplicated_years_array = processed_df[processed_df.duplicated(subset=["year"], keep=False)]["year"].unique()
        duplicated_years = duplicated_years_array.tolist()

    if len(duplicated_years) > 0:
        logger.warning("Found duplicate years in data: %s. Will keep first occurrence only.", duplicated_years)

    # Drop duplicates
    df_unique = processed_df.drop_duplicates(subset=["year"], keep="first")
    logger.info(
        "Data contains %s unique years from %s to %s",
        df_unique.shape[0],
        df_unique["year"].min(),
        df_unique["year"].max(),
    )

    # Select and rename columns
    final_df = df_unique[output_columns].rename(columns={col: column_map[col] for col in output_columns})
    logger.info("Final data frame has %s rows and %s columns", final_df.shape[0], final_df.shape[1])

    return final_df


def save_output_files(
    formatted_df: pd.DataFrame,
    output_dir: str | Path,
    output_base: str,
    extrapolation_info: dict[str, Any],
    *,
    end_year: int,
) -> bool:
    """Save output files in CSV and markdown formats.

    Args:
        formatted_df: The formatted dataframe to save
        output_dir: Output directory path
        output_base: Base name for output files
        extrapolation_info: Information about extrapolation methods used
        end_year: End year for the data

    Returns:
        True if all files were saved successfully, False otherwise
    """
    success = True
    output_dir = Path(output_dir)

    # Save CSV output
    csv_path = output_dir / f"{output_base}.csv"
    logger.info("Writing CSV to: %s", csv_path)
    try:
        formatted_df.to_csv(csv_path, index=False, na_rep="nan")
        logger.info("Successfully wrote CSV data to %s", csv_path)
    except (OSError, PermissionError, ValueError):
        logger.exception("Error writing CSV file")
        success = False

    # Save markdown output
    md_path = output_dir / f"{output_base}.md"
    logger.info("Creating markdown table at: %s", md_path)
    try:
        create_markdown_table(
            formatted_df,
            str(md_path),
            extrapolation_info,
            end_year=end_year,
        )
        logger.info("Successfully created markdown table at %s", md_path)
    except (OSError, PermissionError, ValueError):
        logger.exception("Error creating markdown table")
        success = False

    return success


def prepare_final_dataframe(df: pd.DataFrame, column_map: dict[str, str]) -> pd.DataFrame:
    """Prepare final dataframe for output (backward compatibility alias).

    Args:
        df: Input dataframe
        column_map: Mapping from internal column names to output column names

    Returns:
        DataFrame with selected and renamed columns, duplicates removed
    """
    # Drop duplicates based on year if present
    df_unique = df.drop_duplicates(subset=["year"], keep="first") if "year" in df.columns else df.drop_duplicates()

    # Select only columns that exist in both the dataframe and the column map
    available_columns = [col for col in column_map if col in df_unique.columns]

    # Select and rename columns
    return df_unique[available_columns].rename(columns={col: column_map[col] for col in available_columns})
