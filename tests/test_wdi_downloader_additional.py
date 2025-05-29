import logging
from unittest.mock import patch

import pandas as pd
import pytest
import requests

from utils.data_sources.wdi_downloader import download_wdi_data
from utils.error_handling import DataDownloadError

logger = logging.getLogger(__name__)


class TestWDIDownloaderAdditional:
    """Additional tests for WDI downloader."""

    @patch("pandas_datareader.wb.WorldBankReader")
    def test_download_wdi_data_column_naming(self, mock_wb_reader_class):
        """Test that columns are named correctly."""
        # Create data with dots in column name
        data = pd.DataFrame({"year": [2020, 2021], "NY.GDP.MKTP.CD": [14722730.70, 17734062.65]})
        mock_wb_reader_class.return_value.read.return_value = data

        result = download_wdi_data("NY.GDP.MKTP.CD")

        # Column name should have dots replaced with underscores
        assert "NY_GDP_MKTP_CD" in result.columns
        assert "NY.GDP.MKTP.CD" not in result.columns

    @patch("pandas_datareader.wb.WorldBankReader")
    def test_download_wdi_data_year_column(self, mock_wb_reader_class):
        """Test that year column is properly handled."""
        data = pd.DataFrame({"year": [2020, 2021], "NY.GDP.MKTP.CD": [14722730.70, 17734062.65]})
        mock_wb_reader_class.return_value.read.return_value = data

        result = download_wdi_data("NY.GDP.MKTP.CD")

        # Year should be integer type
        assert result["year"].dtype in [int, "int64", "int32"]

        # Years should be in expected range
        assert result["year"].min() >= 1960
        assert result["year"].max() <= 2030

    @patch("pandas_datareader.wb.WorldBankReader")
    def test_download_wdi_data_data_types(self, mock_wb_reader_class):
        """Test that data types are preserved correctly."""
        data = pd.DataFrame({"year": [2020, 2021], "NY.GDP.MKTP.CD": [14722730.70, 17734062.65]})
        mock_wb_reader_class.return_value.read.return_value = data

        result = download_wdi_data("NY.GDP.MKTP.CD")

        # Check data types
        assert result["year"].dtype in [int, "int64", "int32"]
        assert result["NY_GDP_MKTP_CD"].dtype in [float, "float64"]

    @patch("pandas_datareader.wb.WorldBankReader")
    def test_download_wdi_data_return_type(self, mock_wb_reader_class):
        """Test that function always returns a DataFrame."""
        # Test with valid data
        data = pd.DataFrame({"year": [2020], "NY.GDP.MKTP.CD": [1000]})
        mock_wb_reader_class.return_value.read.return_value = data
        result = download_wdi_data("NY.GDP.MKTP.CD")
        assert isinstance(result, pd.DataFrame)

        # Test with exception -> should raise DataDownloadError
        mock_wb_reader_class.return_value.read.side_effect = requests.exceptions.RequestException("Error")
        with pytest.raises(DataDownloadError):
            download_wdi_data("NY.GDP.MKTP.CD")

        # Test with empty data
        mock_wb_reader_class.return_value.read.side_effect = None
        mock_wb_reader_class.return_value.read.return_value = pd.DataFrame()
        result = download_wdi_data("NY.GDP.MKTP.CD")
        assert isinstance(result, pd.DataFrame)
