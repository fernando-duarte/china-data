#!/usr/bin/env python3
"""Process raw China economic data and produce analysis files.

This script processes the raw data downloaded by china_data_downloader.py to:
- Convert units to standardized formats (billions USD, millions people)
- Calculate capital stock using the perpetual inventory method
- Project human capital using linear regression
- Extrapolate time series to the specified end year using various methods
- Calculate derived economic indicators (TFP, savings, openness ratio, etc.)
- Output processed data in both markdown and CSV formats

The script uses configurable parameters for economic calculations (alpha, capital-output ratio)
and supports various extrapolation methods (ARIMA, linear regression, growth rates).
"""

import argparse
import logging
import sys
from typing import Any

import pandas as pd

from config import Config
from utils.capital import calculate_capital_stock
from utils.data_sources import load_imf_tax_data
from utils.economic_indicators import calculate_economic_indicators
from utils.output import create_markdown_table
from utils.processor_cli import parse_and_validate_args
from utils.processor_extrapolation import extrapolate_series_to_end_year
from utils.processor_hc import project_human_capital
from utils.processor_load import load_raw_data
from utils.processor_units import convert_units

logger = logging.getLogger(__name__)


def process_data(
    raw_data: pd.DataFrame, imf_tax_data: pd.DataFrame, args: argparse.Namespace
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Process raw economic data.

    Args:
        raw_data: Raw data from various sources
        imf_tax_data: IMF tax revenue data
        args: Command line arguments

    Returns:
        Processed DataFrame with all indicators and extrapolation information
    """
    try:
        # Convert units (e.g., USD to billions USD)
        processed_data = convert_units(raw_data)

        # Calculate capital stock
        processed_data = calculate_capital_stock(processed_data, capital_output_ratio=args.capital_output_ratio)

        # Project human capital
        processed_data = project_human_capital(processed_data, end_year=args.end_year)

        # Calculate economic indicators
        processed_data = calculate_economic_indicators(processed_data, alpha=args.alpha)

        # Merge IMF tax revenue projections if available
        if "TAX_pct_GDP" in processed_data.columns and len(imf_tax_data) > 0:
            # Only use projections for future years
            projected_years = [y for y in imf_tax_data["year"] if y > Config.IMF_PROJECTION_START_YEAR]
            if projected_years:
                logger.info(f"Using IMF tax revenue projections for years: {projected_years}")
                for year in projected_years:
                    if year in imf_tax_data["year"].values:
                        tax_value = imf_tax_data.loc[imf_tax_data.year == year, "TAX_pct_GDP"].iloc[0]
                        processed_data.loc[processed_data.year == year, "TAX_pct_GDP"] = tax_value

        # Extrapolate series to end year
        processed_data, extrapolation_info = extrapolate_series_to_end_year(
            processed_data, end_year=args.end_year, raw_data=raw_data
        )

        return processed_data, extrapolation_info

    except Exception as e:
        logger.error(f"Error processing data: {e}", exc_info=True)
        raise


def main() -> None:
    """Main entry point for data processing."""
    try:
        # Parse command line arguments
        args = parse_and_validate_args()

        # Configure structured logging
        if Config.STRUCTURED_LOGGING_ENABLED:
            from utils.logging_config import get_logger, setup_structured_logging

            setup_structured_logging(
                log_level=Config.STRUCTURED_LOGGING_LEVEL,
                log_file=Config.STRUCTURED_LOGGING_FILE,
                enable_json=Config.STRUCTURED_LOGGING_JSON_FORMAT,
                include_process_info=Config.STRUCTURED_LOGGING_INCLUDE_PROCESS_INFO,
            )
            # Use a different variable name to avoid redefinition
            structured_logger = get_logger(__name__)
        else:
            logging.basicConfig(
                level=logging.INFO,
                format=Config.LOG_FORMAT,
                datefmt=Config.LOG_DATE_FORMAT,
            )
            structured_logger = logging.getLogger(__name__)

        # Load raw data
        raw_data = load_raw_data(args.input_file)
        if raw_data.empty:
            structured_logger.error("Failed to load raw data")
            sys.exit(1)

        # Load IMF tax revenue data
        imf_tax_data = load_imf_tax_data()

        # Process data
        processed_data, extrapolation_info = process_data(raw_data, imf_tax_data, args)

        # Create output directory if it doesn't exist
        output_dir = Config.get_output_directory()

        # Save processed data
        output_base = output_dir / args.output_file
        csv_file = output_base.with_suffix(".csv")
        processed_data.to_csv(csv_file, index=False, encoding=Config.FILE_ENCODING)
        structured_logger.info("Saved processed data to %s", csv_file)

        # Create markdown output
        md_file = output_base.with_suffix(".md")
        create_markdown_table(processed_data, md_file, extrapolation_info)
        structured_logger.info("Created markdown table at %s", md_file)

        return

    except Exception as e:
        structured_logger.error("Error processing data: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
