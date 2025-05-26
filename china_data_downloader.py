#!/usr/bin/env python3
"""Download and aggregate raw economic data for China.

This script downloads economic data from multiple sources:
- World Bank World Development Indicators (WDI): GDP components, FDI, population
- Penn World Table (PWT): Real GDP, capital stock, human capital index
- IMF Fiscal Monitor: Tax revenue data (pre-downloaded from input directory)

The data is merged by year and output as a markdown file containing the raw data
with source attribution and download dates.
"""

import argparse
import logging
import time
from datetime import datetime
from pathlib import Path

import pandas as pd

from config import Config
from utils import find_file, get_output_directory
from utils.data_sources.fallback_loader import load_fallback_data
from utils.data_sources.imf_loader import load_imf_tax_data
from utils.data_sources.pwt_downloader import get_pwt_data
from utils.data_sources.wdi_downloader import download_wdi_data
from utils.logging_config import get_logger, setup_structured_logging
from utils.markdown_utils import render_markdown_table
from utils.path_constants import get_search_locations_relative_to_root

# Set up structured logging
if Config.STRUCTURED_LOGGING_ENABLED:
    setup_structured_logging(
        log_level=Config.STRUCTURED_LOGGING_LEVEL,
        log_file=Config.STRUCTURED_LOGGING_FILE,
        enable_json=Config.STRUCTURED_LOGGING_JSON_FORMAT,
        include_process_info=Config.STRUCTURED_LOGGING_INCLUDE_PROCESS_INFO,
    )
    logger = get_logger(__name__)
else:
    logging.basicConfig(level=logging.INFO, format=Config.LOG_FORMAT, datefmt=Config.LOG_DATE_FORMAT)
    logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download and integrate China economic data.")
    parser.add_argument(
        "--end-year",
        type=int,
        default=None,
        help="Last year to include in the output (default: current year)",
    )
    args = parser.parse_args()
    end_year = args.end_year if args.end_year else datetime.now().year

    # Get output directory using the common utility function
    output_dir = get_output_directory()
    logger.info(f"Output files will be saved to: {output_dir}")

    all_data = {}
    # Record the download date for WDI data
    wdi_download_date = datetime.now().strftime("%Y-%m-%d")

    # Try to download WDI data
    wdi_download_failed = False
    for code, name in Config.WDI_INDICATORS.items():
        data = download_wdi_data(code, end_year=end_year)
        if len(data) > 0:
            data = data[["year", code.replace(".", "_")]].rename(columns={code.replace(".", "_"): name})
            # Convert year to int once here instead of multiple times later
            data["year"] = data["year"].astype(int)
            all_data[name] = data
        else:
            logger.warning(f"Failed to download WDI indicator {code} ({name})")
            wdi_download_failed = True
        time.sleep(Config.DOWNLOAD_DELAY_SECONDS)

    # Load IMF tax data using the dedicated loader
    tax_data = load_imf_tax_data()
    if len(tax_data) > 0:
        all_data["TAX_pct_GDP"] = tax_data

    # Get IMF download date from download_date.txt if it exists
    imf_download_date = None
    possible_locations_relative = get_search_locations_relative_to_root()["input_files"]
    date_file = find_file("download_date.txt", possible_locations_relative)
    if date_file and Path(date_file).exists():
        try:
            with open(date_file, encoding="utf-8") as f:
                lines = f.readlines()

            # Parse the file content
            metadata = {}
            for line in lines:
                line = line.strip()
                if line and ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip()

            # Extract the download date
            if "download_date" in metadata:
                imf_download_date = metadata["download_date"]
                logger.info(f"Found IMF download date: {imf_download_date}")
        except Exception as e:
            logger.error(f"Error reading download_date.txt: {e}")

    # Record the download date for PWT data
    pwt_download_date = datetime.now().strftime("%Y-%m-%d")
    pwt_download_failed = False

    try:
        pwt_data = get_pwt_data()
    except Exception as e:
        logger.warning(f"Could not get PWT data: {e}")
        pwt_data = pd.DataFrame(columns=["year", "rgdpo", "rkna", "pl_gdpo", "cgdpo", "hc"])
        pwt_download_failed = True

    # Ensure year column is int for PWT data (already done in get_pwt_data, but ensure consistency)
    if len(pwt_data) > 0 and "year" in pwt_data.columns:
        pwt_data["year"] = pwt_data["year"].astype(int)
    all_data["PWT"] = pwt_data

    # Check if we need to use fallback data
    if (wdi_download_failed or pwt_download_failed) or all(len(data) == 0 for data in all_data.values()):
        logger.warning("Some downloads failed, attempting to use fallback data")
        fallback_data = load_fallback_data(output_dir)

        if fallback_data:
            # Replace failed downloads with fallback data
            for name, data in fallback_data.items():
                if name not in all_data or len(all_data[name]) == 0:
                    logger.info(f"Using fallback data for {name}")
                    all_data[name] = data

            # Update download dates to indicate fallback was used
            if wdi_download_failed:
                wdi_download_date = f"{wdi_download_date} (fallback used)"
            if pwt_download_failed:
                pwt_download_date = f"{pwt_download_date} (fallback used)"
        else:
            logger.error("Failed to load fallback data")

    # Optimize merging process - avoid redundant type conversions
    merged_data = None
    for data in all_data.values():
        if merged_data is None:
            merged_data = data.copy()
        else:
            # Ensure both dataframes have int year columns before merging
            if "year" in merged_data.columns:
                merged_data["year"] = merged_data["year"].astype(int)
            if "year" in data.columns:
                data = data.copy()  # Don't modify original
                data["year"] = data["year"].astype(int)
            merged_data = pd.merge(merged_data, data, on="year", how="outer")

    # Final cleanup of year column - do this once at the end
    if merged_data is not None and "year" in merged_data.columns:
        merged_data["year"] = pd.to_numeric(merged_data["year"], errors="coerce")
        merged_data = merged_data.dropna(subset=["year"])
        merged_data["year"] = merged_data["year"].astype(int)
        merged_data = merged_data.sort_values("year")

        all_years = pd.DataFrame({"year": range(1960, end_year + 1)})
        merged_data = pd.merge(all_years, merged_data, on="year", how="left")
    else:
        logger.error("No data available for processing")
        return

    # Pass download dates to the markdown renderer
    markdown_output = render_markdown_table(
        merged_data, wdi_date=wdi_download_date, pwt_date=pwt_download_date, imf_date=imf_download_date
    )

    output_file = Path(output_dir) / "china_data_raw.md"
    output_file.write_text(markdown_output, encoding="utf-8")
    logger.info("Data download and integration complete!")


if __name__ == "__main__":
    main()
