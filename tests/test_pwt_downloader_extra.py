from unittest.mock import patch

import pandas as pd
import pytest
import requests

from utils.data_sources.pwt_downloader import get_pwt_data


class Session:
    def get(self, url, stream=True, timeout=30):
        class Resp:
            def raise_for_status(self):
                pass

            def iter_content(self, chunk_size=8192):
                yield b"data"

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                pass

        return Resp()


class TestPWTDownloaderExtra:
    """Additional tests for PWT downloader."""

    @pytest.fixture
    def mock_pwt_data(self):
        """Create mock PWT data for testing."""
        return pd.DataFrame(
            {
                "countrycode": ["CHN"] * 5 + ["USA"] * 5,
                "year": [2018, 2019, 2020, 2021, 2022] * 2,
                "rgdpo": [23456.78, 24567.89, 25678.90, 26789.01, 27890.12] * 2,
                "rkna": [0.95, 0.97, 0.99, 1.01, 1.03] * 2,
                "pl_gdpo": [0.45, 0.46, 0.47, 0.48, 0.49] * 2,
                "cgdpo": [12345.67, 13456.78, 14567.89, 15678.90, 16789.01] * 2,
                "hc": [2.34, 2.40, 2.45, 2.50, 2.55] * 2,
                "pop": [1400.5, 1410.2, 1420.1, 1430.0, 1440.0] * 2,
                "emp": [770.5, 775.2, 780.1, 785.0, 790.0] * 2,
                "avh": [2100, 2110, 2120, 2130, 2140] * 2,
                "ccon": [7000.5, 7500.2, 8000.1, 8500.0, 9000.0] * 2,
                "cda": [5000.5, 5200.2, 5400.1, 5600.0, 5800.0] * 2,
            }
        )

    @patch("utils.data_sources.pwt_downloader.get_cached_session")
    def test_get_pwt_data_column_order(self, mock_session, mock_pwt_data):
        """Test that columns are in expected order."""
        mock_session.return_value = Session()
        with patch("pandas.read_excel", return_value=mock_pwt_data):
            result = get_pwt_data()

        # Check that year is first column (common convention)
        assert next(iter(result.columns)) == "year"

    @patch("utils.data_sources.pwt_downloader.get_cached_session")
    @patch("logging.Logger.error")
    def test_get_pwt_data_logs_warning_on_error(self, mock_log, mock_session):
        """Test that errors are logged on download failure."""
        api_error_msg = "API Error"

        class BadSession:
            def get(self, url, stream=True, timeout=30):
                raise requests.exceptions.RequestException(api_error_msg)

        mock_session.return_value = BadSession()
        with (
            patch("pandas.read_excel", return_value=pd.DataFrame()),
            pytest.raises(requests.exceptions.RequestException, match="API Error"),
        ):
            get_pwt_data()

        mock_log.assert_called()
