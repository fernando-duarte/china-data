"""TODO: Add module docstring."""

import logging
import time
from datetime import datetime, timezone
from typing import Any

import pandas as pd
import requests
from pandas_datareader import wb

from config import Config
from utils.caching_utils import get_cached_session
from utils.error_handling import DataDownloadError, log_error_with_context, safe_dataframe_operation
from utils.validation_utils import INDICATOR_VALIDATION_RULES, validate_dataframe_with_rules

logger = logging.getLogger(__name__)


def _raise_missing_year_error(indicator_code: str) -> None:
    """Raise DataDownloadError for missing year column."""
    raise DataDownloadError(
        source="World Bank WDI",
        indicator=indicator_code,
        message="Downloaded data missing 'year' column",
    )


def _create_empty_dataframe(indicator_code: str) -> pd.DataFrame:
    """Create empty DataFrame with expected columns for consistency."""
    indicator_code_db_col = indicator_code.replace(".", "_")
    expected_cols = ["country", "year", indicator_code_db_col]
    return pd.DataFrame(columns=expected_cols)


def _download_raw_data(
    indicator_code: str, country_code: str, start_year: int, end_year: int, session: Any
) -> pd.DataFrame:
    """Download raw data from World Bank API."""
    reader = wb.WorldBankReader(
        symbols=indicator_code,
        countries=country_code,
        start=start_year,
        end=end_year,
        session=session,
    )
    reader.timeout = Config.REQUEST_TIMEOUT_SECONDS
    raw_data = reader.read()
    reader.close()

    return pd.DataFrame(raw_data) if raw_data is not None else pd.DataFrame()


def _process_downloaded_data(data: pd.DataFrame, indicator_code: str) -> pd.DataFrame:
    """Process and validate downloaded data."""
    if data.empty:
        logger.warning("No data returned for %s", indicator_code)
        return _create_empty_dataframe(indicator_code)

    # Process the data
    data = data.reset_index()
    indicator_code_db_col = indicator_code.replace(".", "_")
    data = data.rename(columns={indicator_code: indicator_code_db_col})

    # Validate year column exists
    if "year" not in data.columns:
        _raise_missing_year_error(indicator_code)

    # Convert and validate year data
    data["year"] = pd.to_numeric(data["year"], errors="coerce")
    data = data.dropna(subset=["year"])

    if data.empty:
        logger.warning("All year values became NA after conversion for %s", indicator_code)
        return _create_empty_dataframe(indicator_code)

    data["year"] = data["year"].astype(int)

    # Apply validation rules
    wdi_rules = {indicator_code_db_col: INDICATOR_VALIDATION_RULES.get(indicator_code_db_col, {})}
    validate_dataframe_with_rules(data, rules=wdi_rules, year_column="year")

    logger.info(
        "Successfully downloaded and validated %s (as %s) data with %d rows",
        indicator_code,
        indicator_code_db_col,
        len(data),
    )

    return data


def _handle_download_error(
    error: Exception, indicator_code: str, country_code: str, attempt: int, is_final_attempt: bool
) -> None:
    """Handle download errors with appropriate logging and retry logic."""
    error_context = {
        "indicator": indicator_code,
        "country": country_code,
        "attempt": attempt + 1,
        "max_retries": Config.MAX_RETRIES,
    }

    if isinstance(error, requests.exceptions.RequestException):
        error_type = "Network error"
    else:
        error_context["error_type"] = type(error).__name__
        error_type = "Unexpected error"

    if not is_final_attempt:
        log_message = (
            f"{error_type} on attempt {attempt + 1}, "
            f"retrying in {Config.RETRY_DELAY_SECONDS} seconds"
        )
        log_error_with_context(
            logger,
            log_message,
            error,
            error_context,
            level=logging.WARNING,
        )
        time.sleep(Config.RETRY_DELAY_SECONDS)
    else:
        log_error_with_context(
            logger,
            f"Failed to download {indicator_code} after {Config.MAX_RETRIES} attempts",
            error,
            error_context,
        )


@safe_dataframe_operation("WDI data download")
def download_wdi_data(
    indicator_code: str,
    country_code: str = "CN",
    start_year: int = Config.MIN_YEAR,
    end_year: int | None = None,
) -> pd.DataFrame:
    """Download World Development Indicators data from World Bank.

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
        end_year = datetime.now(timezone.utc).year

    logger.info(
        "Downloading %s data for %s (%d-%d)", indicator_code, country_code, start_year, end_year
    )

    last_error: Exception | None = None
    session = get_cached_session()

    for attempt in range(Config.MAX_RETRIES):
        try:
            # Download and process data
            raw_data = _download_raw_data(
                indicator_code, country_code, start_year, end_year, session
            )
            return _process_downloaded_data(raw_data, indicator_code)

        except (
            requests.exceptions.RequestException,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
        ) as e:
            last_error = e
            is_final_attempt = attempt == Config.MAX_RETRIES - 1
            _handle_download_error(e, indicator_code, country_code, attempt, is_final_attempt)

    # If we get here, all retries failed
    raise DataDownloadError(
        source="World Bank WDI",
        indicator=indicator_code,
        message=f"All {Config.MAX_RETRIES} download attempts failed",
        original_error=last_error,
    )
