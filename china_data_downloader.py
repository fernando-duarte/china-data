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
from typing import Optional, Dict

import pandas as pd

from config import Config
from utils import find_file, get_output_directory
from utils.data_sources.imf_loader import load_imf_tax_data
from utils.data_sources.pwt_downloader import get_pwt_data
from utils.data_sources.wdi_downloader import download_wdi_data
from utils.markdown_utils import render_markdown_table
from utils.path_constants import get_search_locations_relative_to_root

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
    """
    fallback_file = os.path.join(output_dir, "china_data_raw.md")
    if not os.path.exists(fallback_file):
        logger.warning(f"Fallback file {fallback_file} not found")
        return None
        
    logger.info(f"Loading fallback data from {fallback_file}")
    
    try:
        # Read the markdown file
        with open(fallback_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
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
            logger.error("Could not find data table in fallback file")
            return None
            
        # Parse the table
        table_lines = lines[table_start:table_end]
        headers = [h.strip() for h in table_lines[0].split('|')[1:-1]]
        
        # Skip the separator line
        data_lines = table_lines[2:]
        
        # Parse data
        data = []
        for line in data_lines:
            if line.strip():
                values = [v.strip() for v in line.split('|')[1:-1]]
                data.append(values)
                
        # Create DataFrame
        df = pd.DataFrame(data, columns=headers)
        
        # Convert numeric columns
        for col in df.columns:
            if col != 'Year':
                df[col] = pd.to_numeric(df[col].replace('N/A', pd.NA), errors='coerce')
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
        # Split into separate dataframes by indicator
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
                result[name] = df[['Year', col]].rename(columns={'Year': 'year', col: name}).dropna()
                
        # Tax data
        if 'Tax Revenue (% of GDP)' in df.columns:
            result['TAX_pct_GDP'] = df[['Year', 'Tax Revenue (% of GDP)']].rename(
                columns={'Year': 'year', 'Tax Revenue (% of GDP)': 'TAX_pct_GDP'}
            ).dropna()
            
        # PWT data
        pwt_cols = ['PWT rgdpo', 'PWT rkna', 'PWT pl_gdpo', 'PWT cgdpo', 'PWT hc']
        pwt_rename = {
            'Year': 'year',
            'PWT rgdpo': 'rgdpo',
            'PWT rkna': 'rkna', 
            'PWT pl_gdpo': 'pl_gdpo',
            'PWT cgdpo': 'cgdpo',
            'PWT hc': 'hc'
        }
        
        pwt_available = [col for col in pwt_cols if col in df.columns]
        if pwt_available:
            cols_to_select = ['Year'] + pwt_available
            rename_dict = {k: v for k, v in pwt_rename.items() if k in cols_to_select}
            result['PWT'] = df[cols_to_select].rename(columns=rename_dict).dropna(subset=[rename_dict[c] for c in pwt_available], how='all')
            
        logger.info(f"Successfully loaded fallback data with {len(result)} indicators")
        return result
        
    except Exception as e:
        logger.error(f"Error loading fallback data: {e}")
        return None


def main():
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
        if not data.empty:
            data = data[["year", code.replace(".", "_")]].rename(columns={code.replace(".", "_"): name})
            data["year"] = data["year"].astype(int)
            all_data[name] = data
        else:
            logger.warning(f"Failed to download WDI indicator {code} ({name})")
            wdi_download_failed = True
        time.sleep(1)

    # Load IMF tax data using the dedicated loader
    tax_data = load_imf_tax_data()
    if not tax_data.empty:
        all_data["TAX_pct_GDP"] = tax_data

    # Get IMF download date from download_date.txt if it exists
    imf_download_date = None
    possible_locations_relative = get_search_locations_relative_to_root()["input_files"]
    date_file = find_file("download_date.txt", possible_locations_relative)
    if date_file and os.path.exists(date_file):
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
    pwt_data["year"] = pwt_data["year"].astype(int)
    all_data["PWT"] = pwt_data

    # Check if we need to use fallback data
    if (wdi_download_failed or pwt_download_failed) or all(data.empty for data in all_data.values()):
        logger.warning("Some downloads failed, attempting to use fallback data")
        fallback_data = load_fallback_data(output_dir)
        
        if fallback_data:
            # Replace failed downloads with fallback data
            for name, data in fallback_data.items():
                if name not in all_data or all_data[name].empty:
                    logger.info(f"Using fallback data for {name}")
                    all_data[name] = data
                    
            # Update download dates to indicate fallback was used
            if wdi_download_failed:
                wdi_download_date = f"{wdi_download_date} (fallback used)"
            if pwt_download_failed:
                pwt_download_date = f"{pwt_download_date} (fallback used)"
        else:
            logger.error("Failed to load fallback data")

    merged_data = None
    for data in all_data.values():
        if merged_data is None:
            merged_data = data
        else:
            merged_data["year"] = merged_data["year"].astype(int)
            data["year"] = data["year"].astype(int)
            merged_data = pd.merge(merged_data, data, on="year", how="outer")

    merged_data["year"] = pd.to_numeric(merged_data["year"], errors="coerce")
    merged_data = merged_data.dropna(subset=["year"])
    merged_data["year"] = merged_data["year"].astype(int)
    merged_data = merged_data.sort_values("year")

    all_years = pd.DataFrame({"year": range(1960, end_year + 1)})
    merged_data = pd.merge(all_years, merged_data, on="year", how="left")

    # Pass download dates to the markdown renderer
    markdown_output = render_markdown_table(
        merged_data, wdi_date=wdi_download_date, pwt_date=pwt_download_date, imf_date=imf_download_date
    )

    with open(os.path.join(output_dir, "china_data_raw.md"), "w", encoding="utf-8") as f:
        f.write(markdown_output)
    logger.info("Data download and integration complete!")


if __name__ == "__main__":
    main()
