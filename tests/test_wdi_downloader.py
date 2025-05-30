import logging
from datetime import UTC, datetime
from unittest import mock
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
import requests

from config import Config
from utils.data_sources.wdi_downloader import download_wdi_data
from utils.error_handling import DataDownloadError

logger = logging.getLogger(__name__)


class TestWDIDownloader:
    """Test suite for WDI (World Development Indicators) downloader."""

    @pytest.fixture
    def sample_wdi_data(self):
        """Create sample WDI data for mocking."""
        # This data should resemble what WorldBankReader().read() returns
        # It has 'country' and 'year' in the index initially
        idx = pd.MultiIndex.from_product(
            [["China"], list(range(2020, 2025))], names=["country", "year"]
        )
        return pd.DataFrame({"NY.GDP.MKTP.CD": [1.5e13, 1.6e13, 1.7e13, 1.8e13, 1.9e13]}, index=idx)

    @patch("pandas_datareader.wb.WorldBankReader")
    def test_download_wdi_data_success(self, mock_wb_reader_class, sample_wdi_data):
        """Test successful WDI data download."""
        # Configure the mock WorldBankReader instance and its read() method
        mock_reader_instance = mock_wb_reader_class.return_value
        mock_reader_instance.read.return_value = sample_wdi_data

        result = download_wdi_data("NY.GDP.MKTP.CD")

        mock_wb_reader_class.assert_called_once_with(
            symbols="NY.GDP.MKTP.CD",
            countries="CN",
            start=1960,  # Default start year from Config
            end=datetime.now(UTC).year,  # Default end year
            session=mock.ANY,  # Check that a session object was passed
        )
        mock_reader_instance.read.assert_called_once()
        mock_reader_instance.close.assert_called_once()

        assert not result.empty
        # After processing in download_wdi_data, columns are 'country', 'year', 'NY_GDP_MKTP_CD'
        assert list(result.columns) == ["country", "year", "NY_GDP_MKTP_CD"]
        assert result["year"].iloc[0] == 2020
        assert result["NY_GDP_MKTP_CD"].iloc[0] == 1.5e13

    @patch("pandas_datareader.wb.WorldBankReader")
    def test_download_wdi_data_custom_end_year(self, mock_wb_reader_class, sample_wdi_data):
        """Test WDI data download with a custom end year."""
        mock_reader_instance = mock_wb_reader_class.return_value
        mock_reader_instance.read.return_value = sample_wdi_data

        custom_end_year = 2030
        download_wdi_data("NY.GDP.MKTP.CD", end_year=custom_end_year)

        mock_wb_reader_class.assert_called_once_with(
            symbols="NY.GDP.MKTP.CD",
            countries="CN",
            start=1960,
            end=custom_end_year,
            session=mock.ANY,
        )

    @patch("pandas_datareader.wb.WorldBankReader")
    def test_download_wdi_data_empty_response(self, mock_wb_reader_class):
        """Test WDI data download when API returns an empty DataFrame."""
        mock_reader_instance = mock_wb_reader_class.return_value
        mock_reader_instance.read.return_value = pd.DataFrame()  # Empty dataframe

        result = download_wdi_data("NY.GDP.MKTP.CD")
        assert result.empty
        # Check for expected columns even if empty
        assert list(result.columns) == ["country", "year", "NY_GDP_MKTP_CD"]

    @patch("pandas_datareader.wb.WorldBankReader")
    def test_download_wdi_data_exception_handling(self, mock_wb_reader_class):
        """Test exception handling during WDI data download attempt."""
        mock_reader_instance = mock_wb_reader_class.return_value
        mock_reader_instance.read.side_effect = requests.exceptions.RequestException("API Error")

        with pytest.raises(DataDownloadError):
            download_wdi_data("NY.GDP.MKTP.CD")

        assert mock_reader_instance.read.call_count == Config.MAX_RETRIES

    @patch("utils.data_sources.wdi_downloader.logger")  # Patch module logger
    @patch("pandas_datareader.wb.WorldBankReader")
    def test_download_wdi_data_logs_error(self, mock_wb_reader_class, mock_logger_wdi):
        """Test that errors are logged during WDI download attempts."""
        mock_reader_instance = mock_wb_reader_class.return_value
        mock_reader_instance.read.side_effect = requests.exceptions.RequestException(
            "Simulated API Error"
        )

        with pytest.raises(DataDownloadError):
            download_wdi_data("NY.GDP.MKTP.CD")

        # Check for warning logs during retries
        warning_calls = [
            call for call in mock_logger_wdi.log.call_args_list if call[0][0] == logging.WARNING
        ]
        assert len(warning_calls) > 0, "Expected warning logs during retries"

        # Check for error log after all retries fail
        error_calls = [
            call for call in mock_logger_wdi.log.call_args_list if call[0][0] == logging.ERROR
        ]
        assert len(error_calls) > 0, "Expected error log after all retries failed"

    @patch("pandas_datareader.wb.WorldBankReader")
    def test_download_wdi_data_different_indicators(self, mock_wb_reader_class, sample_wdi_data):
        """Test downloading different WDI indicators."""
        mock_reader_instance = mock_wb_reader_class.return_value
        mock_reader_instance.read.return_value = sample_wdi_data

        indicator_gdp = "NY.GDP.MKTP.CD"
        indicator_pop = "SP.POP.TOTL"  # Population indicator

        download_wdi_data(indicator_gdp)
        call_args_gdp = mock_wb_reader_class.call_args
        assert call_args_gdp[1]["symbols"] == indicator_gdp

        # Reset mock for next call if necessary or use different mock instances
        mock_wb_reader_class.reset_mock()
        mock_reader_instance.reset_mock()  # also reset instance mock
        mock_reader_instance.read.return_value = sample_wdi_data  # re-assign after reset

        download_wdi_data(indicator_pop)
        call_args_pop = mock_wb_reader_class.call_args
        assert call_args_pop[1]["symbols"] == indicator_pop

    @patch("pandas_datareader.wb.WorldBankReader")
    def test_download_wdi_data_duplicate_years(self, mock_wb_reader_class):
        """Test handling of data with duplicate years (should not happen from API)."""
        # WorldBankReader should already handle this, but if it didn't:
        idx = pd.MultiIndex.from_tuples(
            [("China", 2020), ("China", 2020), ("China", 2021)], names=["country", "year"]
        )
        dup_data = pd.DataFrame({"NY.GDP.MKTP.CD": [1e13, 1.1e13, 1.2e13]}, index=idx)

        mock_reader_instance = mock_wb_reader_class.return_value
        mock_reader_instance.read.return_value = dup_data

        # The current code doesn't explicitly drop duplicates, relies on source or later processing.
        # For this test, we expect the validation to pass if types are correct.
        result = download_wdi_data("NY.GDP.MKTP.CD")
        assert len(result) == 3  # Or 2 if duplicates were dropped (they are not currently)
        # This test might need refinement based on desired duplicate handling policy at this stage.

    @patch("pandas_datareader.wb.WorldBankReader")
    def test_download_wdi_data_missing_values(self, mock_wb_reader_class):
        """Test WDI data with missing values (NaNs)."""
        idx = pd.MultiIndex.from_product(
            [["China"], list(range(2020, 2023))], names=["country", "year"]
        )
        data_with_nans = pd.DataFrame({"NY.GDP.MKTP.CD": [1.5e13, np.nan, 1.7e13]}, index=idx)
        mock_reader_instance = mock_wb_reader_class.return_value
        mock_reader_instance.read.return_value = data_with_nans

        result = download_wdi_data("NY.GDP.MKTP.CD")
        assert pd.isna(result.loc[result["year"] == 2021, "NY_GDP_MKTP_CD"].iloc[0])
        assert pd.notna(result.loc[result["year"] == 2020, "NY_GDP_MKTP_CD"].iloc[0])

    @patch("time.sleep")  # Mock time.sleep within wdi_downloader context
    @patch("pandas_datareader.wb.WorldBankReader")
    def test_no_sleep_in_successful_download(
        self, mock_wb_reader_class, mock_sleep, sample_wdi_data
    ):
        """Test that time.sleep is not called on a successful download (only on retries)."""
        mock_reader_instance = mock_wb_reader_class.return_value
        mock_reader_instance.read.return_value = sample_wdi_data

        download_wdi_data("NY.GDP.MKTP.CD")
        mock_sleep.assert_not_called()  # This should pass if download is successful on first try
