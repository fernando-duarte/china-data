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
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

import pandas as pd

from config import Config
from utils import find_file, get_output_directory
from utils.data_sources.imf_loader import load_imf_tax_data
from utils.data_sources.pwt_downloader import get_pwt_data
from utils.data_sources.wdi_downloader import download_wdi_data
from utils.markdown_utils import render_markdown_table
from utils.path_constants import get_search_locations_relative_to_root
from utils.error_handling import (
    FileOperationError,
    DataValidationError, 
    log_error_with_context,
    validate_dataframe_not_empty
)
from utils.validation_utils import validate_dataframe_with_rules, INDICATOR_VALIDATION_RULES

logging.basicConfig(
    level=logging.INFO, format=Config.LOG_FORMAT, datefmt=Config.LOG_DATE_FORMAT
)
logger = logging.getLogger(__name__)


def load_fallback_data(output_dir: str) -> Optional[Dict[str, pd.DataFrame]]:
    """
    Load data from existing china_data_raw.md file as fallback.
    
    Args:
        output_dir: Directory where china_data_raw.md is located
        
    Returns:
        Dictionary of dataframes by indicator name, or None if file not found
        
    Raises:
        FileOperationError: If file operations fail
        DataValidationError: If data validation fails
    """
    fallback_file = Path(output_dir) / "china_data_raw.md"
    if not fallback_file.exists():
        logger.warning(f"Fallback file {fallback_file} not found")
        return None
        
    logger.info(f"Loading fallback data from {fallback_file}")
    
    try:
        # Read the markdown file with explicit encoding
        try:
            content = fallback_file.read_text(encoding='utf-8')
        except (IOError, OSError) as e:
            raise FileOperationError(
                operation="read",
                filepath=str(fallback_file),
                message="Failed to read fallback file",
                original_error=e
            )
            
        if not content.strip():
            raise DataValidationError(
                column="fallback_file",
                message="Fallback file is empty",
                data_info=f"File: {fallback_file}"
            )
            
        # Find the table section
        lines = content.split('\n')
        table_start = None
        table_end = None
        
        for i, line in enumerate(lines):
            if line.startswith('| Year |'):
                table_start = i
            elif table_start is not None and line.strip() == '' and i > table_start + 2:
                table_end = i
                break
                
        if table_start is None:
            raise DataValidationError(
                column="fallback_file",
                message="Could not find data table in fallback file",
                data_info=f"File: {fallback_file}, Lines: {len(lines)}"
            )
            
        # Parse the table
        table_lines = lines[table_start:table_end]
        if len(table_lines) < 3:  # Header + separator + at least one data row
            raise DataValidationError(
                column="fallback_file",
                message="Insufficient table data in fallback file",
                data_info=f"Table lines: {len(table_lines)}"
            )
            
        headers = [h.strip() for h in table_lines[0].split('|')[1:-1]]
        
        # Skip the separator line
        data_lines = table_lines[2:]
        
        # Parse data with validation
        data = []
        parse_errors = []
        
        for line_num, line in enumerate(data_lines, start=table_start + 3):
            if line.strip():
                try:
                    values = [v.strip() for v in line.split('|')[1:-1]]
                    if len(values) != len(headers):
                        parse_errors.append(f"Line {line_num}: Expected {len(headers)} columns, got {len(values)}")
                        continue
                    data.append(values)
                except Exception as e:
                    parse_errors.append(f"Line {line_num}: Parse error - {str(e)}")
                    
        # Report parse errors but continue if we have some data
        if parse_errors:
            logger.warning(f"Parse errors in fallback file: {parse_errors[:Config.MAX_LOG_ERRORS_DISPLAYED]}")  # Show first N errors
            if len(parse_errors) > Config.MAX_LOG_ERRORS_DISPLAYED:
                logger.warning(f"... and {len(parse_errors) - Config.MAX_LOG_ERRORS_DISPLAYED} more parse errors")
                
        if not data:
            raise DataValidationError(
                column="fallback_file",
                message="No valid data rows found in fallback file",
                data_info=f"Parse errors: {len(parse_errors)}"
            )
                
        # Create DataFrame with validation
        try:
            df = pd.DataFrame(data, columns=headers)
        except Exception as e:
            raise DataValidationError(
                column="fallback_file",
                message=f"Failed to create DataFrame from parsed data: {str(e)}",
                data_info=f"Headers: {headers}, Data rows: {len(data)}"
            )
        
        # Convert numeric columns with error tracking
        conversion_errors = {}
        for col in df.columns:
            if col != 'Year':
                try:
                    # Replace 'N/A' and similar values with NaN
                    cleaned = df[col].replace(['N/A', 'nan', 'NaN', ''], pd.NA)
                    df[col] = pd.to_numeric(cleaned, errors='coerce')
                except Exception as e:
                    conversion_errors[col] = str(e)
            else:
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except Exception as e:
                    conversion_errors[col] = str(e)
                    
        if conversion_errors:
            logger.warning(f"Numeric conversion errors in fallback data: {conversion_errors}")
                
        # Validate that we have a Year column with valid data
        if 'Year' not in df.columns:
            raise DataValidationError(
                column="Year",
                message="Year column missing from fallback data",
                data_info=f"Available columns: {list(df.columns)}"
            )
            
        valid_years = df['Year'].dropna()
        if len(valid_years) == 0:
            raise DataValidationError(
                column="Year",
                message="No valid years found in fallback data",
                data_info=f"Year column values: {df['Year'].head().tolist()}"
            )
                
        # Split into separate dataframes by indicator with validation
        result = {}
        
        # WDI indicators
        wdi_mapping = {
            'GDP (USD)': 'GDP_USD',
            'Consumption (USD)': 'C_USD', 
            'Government (USD)': 'G_USD',
            'Investment (USD)': 'I_USD',
            'Exports (USD)': 'X_USD',
            'Imports (USD)': 'M_USD',
            'FDI (% of GDP)': 'FDI_pct_GDP',
            'Population': 'POP',
            'Labor Force': 'LF'
        }
        
        for col, name in wdi_mapping.items():
            if col in df.columns:
                indicator_df = df[['Year', col]].rename(columns={'Year': 'year', col: name}).dropna()
                if len(indicator_df) > 0:
                    result[name] = indicator_df
                    logger.debug(f"Loaded {len(indicator_df)} rows for {name} from fallback")
                else:
                    logger.warning(f"No valid data for {name} in fallback file")
                    
        # Tax data
        if 'Tax Revenue (% of GDP)' in df.columns:
            tax_df = df[['Year', 'Tax Revenue (% of GDP)']].rename(
                columns={'Year': 'year', 'Tax Revenue (% of GDP)': 'TAX_pct_GDP'}
            ).dropna()
            if len(tax_df) > 0:
                result['TAX_pct_GDP'] = tax_df
                logger.debug(f"Loaded {len(tax_df)} rows for TAX_pct_GDP from fallback")
            
        # PWT data
        pwt_cols = ['PWT rgdpo', 'PWT rkna', 'PWT pl_gdpo', 'PWT cgdpo', 'PWT hc']
        pwt_rename_map_for_validation = {
            'PWT rgdpo': 'rgdpo',
            'PWT rkna': 'rkna', 
            'PWT pl_gdpo': 'pl_gdpo',
            'PWT cgdpo': 'cgdpo',
            'PWT hc': 'hc'
        }
        pwt_rules_for_fallback = {k: INDICATOR_VALIDATION_RULES.get(v, {}) for k,v in pwt_rename_map_for_validation.items() if k in df.columns and v in INDICATOR_VALIDATION_RULES}

        temp_pwt_df_for_validation = df[['Year'] + [col for col in pwt_rename_map_for_validation if col in df.columns]].copy()
        temp_pwt_df_for_validation.rename(columns={'Year': 'year'}, inplace=True) # year col for validation func
        validate_dataframe_with_rules(temp_pwt_df_for_validation, rules=pwt_rules_for_fallback, year_column='year')
        temp_pwt_df_for_validation.rename(columns={'year': 'Year'}, inplace=True) # revert for PWT processing block

        pwt_available = [col for col in pwt_cols if col in df.columns]
        if pwt_available:
            cols_to_select = ['Year'] + pwt_available
            rename_dict = {k: v for k, v in pwt_rename_map_for_validation.items() if k in cols_to_select}
            pwt_df = df[cols_to_select].rename(columns=rename_dict).dropna(subset=[rename_dict[c] for c in pwt_available], how='all')
            if len(pwt_df) > 0:
                result['PWT'] = pwt_df
                logger.debug(f"Loaded {len(pwt_df)} rows for PWT from fallback")
            
        # Tax data - 'TAX_pct_GDP' is the key in rules
        if 'Tax Revenue (% of GDP)' in df.columns:
            tax_df_for_validation = df[['Year', 'Tax Revenue (% of GDP)']].rename(
                columns={'Year': 'year', 'Tax Revenue (% of GDP)': 'TAX_pct_GDP'}
            ).copy()
            validate_dataframe_with_rules(tax_df_for_validation, rules={"TAX_pct_GDP": INDICATOR_VALIDATION_RULES.get("TAX_pct_GDP", {})}, year_column='year')

        if not result:
            raise DataValidationError(
                column="fallback_data",
                message="No valid indicators found in fallback data",
                data_info=f"Available columns: {list(df.columns)}"
            )
            
        logger.info(f"Successfully loaded fallback data with {len(result)} indicators")
        return result
        
    except (FileOperationError, DataValidationError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        log_error_with_context(
            logger,
            "Unexpected error loading fallback data",
            e,
            context={'fallback_file': fallback_file}
        )
        raise FileOperationError(
            operation="parse",
            filepath=fallback_file,
            message="Unexpected error during fallback data parsing",
            original_error=e
        )


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
            with open(date_file, "r", encoding="utf-8") as f:
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
