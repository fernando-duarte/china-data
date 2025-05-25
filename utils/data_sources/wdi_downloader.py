import logging
import time
from datetime import datetime
from typing import Optional

import pandas as pd
import pandas_datareader.wb as wb
import requests

from config import Config
from utils.error_handling import (
    DataDownloadError, 
    safe_dataframe_operation, 
    log_error_with_context
)

logger = logging.getLogger(__name__)


@safe_dataframe_operation("WDI data download")
def download_wdi_data(indicator_code: str, country_code: str = "CN", start_year: int = Config.MIN_YEAR, end_year: Optional[int] = None) -> pd.DataFrame:
    """
    Download World Development Indicators data from World Bank.
    
    Args:
        indicator_code: WDI indicator code (e.g., 'NY.GDP.MKTP.CD')
        country_code: Country code (default: 'CN' for China)
        start_year: Start year for data (default: from Config.MIN_YEAR)
        end_year: End year for data (default: current year)
        
    Returns:
        DataFrame with year and indicator data, or empty DataFrame on error
        
    Raises:
        DataDownloadError: If download fails after all retries
    """
    if end_year is None:
        end_year = datetime.now().year

    logger.info(f"Downloading {indicator_code} data for {country_code} ({start_year}-{end_year})")
    
    last_error = None
    
    for attempt in range(Config.MAX_RETRIES):
        try:
            # Download data with timeout
            data = wb.download(
                country=country_code, 
                indicator=indicator_code, 
                start=start_year, 
                end=end_year
            )
            
            if data is None or len(data) == 0:
                logger.warning(f"No data returned for {indicator_code}")
                return pd.DataFrame(columns=["country", "year", indicator_code.replace(".", "_")])
            
            # Process the data
            data = data.reset_index()
            data = data.rename(columns={indicator_code: indicator_code.replace(".", "_")})
            
            # Validate the result
            if "year" not in data.columns:
                raise DataDownloadError(
                    source="World Bank WDI",
                    indicator=indicator_code,
                    message="Downloaded data missing 'year' column"
                )
            
            logger.info(f"Successfully downloaded {indicator_code} data with {len(data)} rows")
            return data
            
        except requests.exceptions.RequestException as e:
            last_error = e
            error_context = {
                'indicator': indicator_code,
                'country': country_code,
                'attempt': attempt + 1,
                'max_retries': Config.MAX_RETRIES
            }
            
            if attempt < Config.MAX_RETRIES - 1:
                log_error_with_context(
                    logger, 
                    f"Network error on attempt {attempt + 1}, retrying in {Config.RETRY_DELAY_SECONDS} seconds",
                    e,
                    error_context,
                    level=logging.WARNING
                )
                time.sleep(Config.RETRY_DELAY_SECONDS)
            else:
                log_error_with_context(
                    logger,
                    f"Failed to download {indicator_code} after {Config.MAX_RETRIES} attempts",
                    e,
                    error_context
                )
                
        except Exception as e:
            last_error = e
            error_context = {
                'indicator': indicator_code,
                'country': country_code,
                'attempt': attempt + 1,
                'max_retries': Config.MAX_RETRIES,
                'error_type': type(e).__name__
            }
            
            if attempt < Config.MAX_RETRIES - 1:
                log_error_with_context(
                    logger,
                    f"Unexpected error on attempt {attempt + 1}, retrying in {Config.RETRY_DELAY_SECONDS} seconds",
                    e,
                    error_context,
                    level=logging.WARNING
                )
                time.sleep(Config.RETRY_DELAY_SECONDS)
            else:
                log_error_with_context(
                    logger,
                    f"Failed to download {indicator_code} after {Config.MAX_RETRIES} attempts",
                    e,
                    error_context
                )
    
    # If we get here, all retries failed
    raise DataDownloadError(
        source="World Bank WDI",
        indicator=indicator_code,
        message=f"All {Config.MAX_RETRIES} download attempts failed",
        original_error=last_error
    )
