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

import logging

from config import Config

# Use relative imports based on new structure
from utils import get_output_directory
from utils.capital import calculate_capital_stock, project_capital_stock
from utils.economic_indicators import calculate_economic_indicators
from utils.processor_cli import parse_arguments
from utils.processor_extrapolation import extrapolate_series_to_end_year
from utils.processor_hc import project_human_capital
from utils.processor_load import load_imf_tax_revenue_data, load_raw_data
from utils.processor_output import format_data_for_output
from utils.processor_units import convert_units

# Import the refactored functions from their new locations
from utils.processor_dataframe.merge_operations import (
    merge_dataframe_column,
    merge_projections,
    merge_tax_data,
)
from utils.processor_dataframe.metadata_operations import get_projection_metadata
from utils.processor_dataframe.output_operations import (
    prepare_final_dataframe,
    save_output_files,
)

logging.basicConfig(
    level=logging.INFO, format=Config.LOG_FORMAT, datefmt=Config.LOG_DATE_FORMAT
)
logger = logging.getLogger(__name__)


def main() -> None:
    # INITIALIZATION
    args = parse_arguments()
    input_file = args.input_file
    alpha = args.alpha
    output_base = args.output_file
    capital_output_ratio = args.capital_output_ratio
    end_year = args.end_year

    output_dir = get_output_directory()
    logger.info(f"Output files will be saved to: {output_dir}")

    # DATA LOADING
    logger.info("Loading raw data sources")
    raw_data = load_raw_data(input_file=input_file)
    imf_tax_data = load_imf_tax_revenue_data()

    # DATA PREPROCESSING
    logger.info("Converting units")
    processed = convert_units(raw_data)

    # PROJECTIONS & CALCULATIONS
    projection_info = {}

    # Capital Stock Calculation
    logger.info("Calculating capital stock")
    capital_df = calculate_capital_stock(processed, capital_output_ratio)
    processed, _ = merge_dataframe_column(processed, capital_df, "K_USD_bn", "capital stock")

    # Human Capital Projection
    # Human capital projection
    logger.info(f"Projecting human capital to {end_year}")
    hc_proj = project_human_capital(raw_data, end_year=end_year)

    # Merge human capital projections
    processed, hc_info = merge_projections(processed, hc_proj, "hc", "Linear regression", "human capital")

    # Merge tax data
    logger.info("Processing tax revenue data")
    processed, tax_info = merge_tax_data(processed, imf_tax_data)

    # Extrapolate base series to end year
    logger.info(f"Extrapolating base series to end year {end_year}")
    try:
        processed, extrapolation_info = extrapolate_series_to_end_year(
            processed, end_year=end_year, raw_data=raw_data
        )
        logger.info(f"Extrapolation complete - info contains {len(extrapolation_info)} series")
    except Exception as e:
        logger.error(f"Error during extrapolation: {e}")
        extrapolation_info = {}

    # Capital Stock Projection (after investment has been extrapolated)
    logger.info(f"Projecting capital stock to {end_year} using extrapolated investment")
    logger.info("Using unsmoothed capital data")
    k_proj = project_capital_stock(processed, end_year=end_year)

    # Merge capital stock projections
    processed, k_info = merge_projections(
        processed, k_proj, "K_USD_bn", "Investment-based projection", "capital stock"
    )

    # Calculate economic indicators using extrapolated variables
    logger.info("Calculating derived economic indicators from extrapolated variables")
    processed = calculate_economic_indicators(processed, alpha=alpha, logger=logger)

    # DOCUMENTATION - Record projection methods
    logger.info("Recording projection methods for all variables")

    # Human Capital metadata
    hc_metadata = get_projection_metadata(processed, hc_proj, raw_data, "hc", "Linear regression", end_year)
    if hc_metadata:
        projection_info["hc"] = hc_metadata

    # Physical Capital metadata
    k_metadata = get_projection_metadata(
        processed, k_proj, processed, "K_USD_bn", "Investment-based projection", end_year
    )
    if k_metadata:
        projection_info["K_USD_bn"] = k_metadata

    # Tax revenue metadata
    if "TAX_pct_GDP" in processed.columns and not imf_tax_data.empty:
        try:
            projected_years = [y for y in imf_tax_data["year"] if y > 2023]
            if projected_years:
                projection_info["TAX_pct_GDP"] = {"method": "IMF projections", "years": projected_years}
                logger.info(
                    f"Set tax revenue projection method to IMF projections for years "
                    f"{min(projected_years)}-{max(projected_years)}"
                )
        except Exception as e:
            logger.warning(f"Error recording tax projection info: {e}")

    # Update projection info with extrapolation info
    projection_info.update(extrapolation_info)

    # OUTPUT PREPARATION
    # Prepare output data
    logger.info("Preparing data for output")

    try:
        # Prepare final dataframe using column map from config
        final_df = prepare_final_dataframe(processed, Config.OUTPUT_COLUMN_MAP)

        # Format data for output
        formatted = format_data_for_output(final_df)

        # Save to output files
        save_output_files(
            formatted,
            output_dir,
            output_base,
            projection_info,
            alpha,
            capital_output_ratio,
            input_file,
            end_year,
        )
    except Exception as e:
        logger.error(f"Error preparing output data: {e}")
        raise


if __name__ == "__main__":
    main()
