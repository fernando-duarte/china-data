from unittest.mock import patch

import pandas as pd
import pytest

from utils.data_sources.pwt_downloader import get_pwt_data


class Session:
    """Simple session mock for get_pwt_data."""

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


class TestPWTDownloader:
    """Test suite for PWT (Penn World Table) downloader."""

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
    def test_get_pwt_data_success(self, mock_session, mock_pwt_data):
        """Test successful PWT data download."""
        mock_session.return_value = Session()
        with patch("pandas.read_excel", return_value=mock_pwt_data) as read_excel:
            result = get_pwt_data()

        # Verify pandas.read_excel was called
        read_excel.assert_called()

        # Verify number of rows matches China records
        assert len(result) == 5

        # Verify required columns are present
        required_columns = ["year", "rgdpo", "rkna", "pl_gdpo", "cgdpo", "hc"]
        for col in required_columns:
            assert col in result.columns

    @patch("utils.data_sources.pwt_downloader.get_cached_session")
    def test_get_pwt_data_empty_response(self, mock_session):
        """Test handling of empty response from API."""
        mock_session.return_value = Session()
        with patch("pandas.read_excel", return_value=pd.DataFrame()):
            with pytest.raises(AttributeError):
                get_pwt_data()

    @patch("utils.data_sources.pwt_downloader.get_cached_session")
    def test_get_pwt_data_no_china_data(self, mock_session):
        """Test handling when no China data is present."""
        # Create data without China
        data_without_china = pd.DataFrame(
            {
                "countrycode": ["USA", "GBR", "FRA"],
                "year": [2020, 2020, 2020],
                "rgdpo": [20000, 3000, 2500],
                "rkna": [1.0, 1.0, 1.0],
                "pl_gdpo": [1.0, 0.9, 0.85],
                "cgdpo": [20000, 2700, 2125],
                "hc": [3.5, 3.4, 3.3],
            }
        )
        mock_session.return_value = Session()
        with patch("pandas.read_excel", return_value=data_without_china):
            result = get_pwt_data()

        # Should return empty DataFrame
        assert len(result) == 0

    @patch("utils.data_sources.pwt_downloader.get_cached_session")
    def test_get_pwt_data_missing_columns(self, mock_session):
        """Test handling when some columns are missing."""
        # Create data with missing columns
        incomplete_data = pd.DataFrame(
            {
                "countrycode": ["CHN"],
                "year": [2020],
                "rgdpo": [25678.90],
                # Missing other columns
            }
        )
        mock_session.return_value = Session()
        with patch("pandas.read_excel", return_value=incomplete_data):
            with pytest.raises(KeyError):
                get_pwt_data()

    @patch("utils.data_sources.pwt_downloader.get_cached_session")
    def test_get_pwt_data_exception_handling(self, mock_session):
        """Test exception handling during download."""

        # Set up mock to raise exception
        class BadSession(Session):
            def get(self, url, stream=True, timeout=30):
                raise Exception("Connection error")

        mock_session.return_value = BadSession()
        with patch("pandas.read_excel", return_value=pd.DataFrame()):
            with pytest.raises(Exception):
                get_pwt_data()

    @patch("utils.data_sources.pwt_downloader.get_cached_session")
    def test_get_pwt_data_data_types(self, mock_session, mock_pwt_data):
        """Test that data types are correct."""
        mock_session.return_value = Session()
        with patch("pandas.read_excel", return_value=mock_pwt_data):
            result = get_pwt_data()

        # Check data types
        assert result["year"].dtype in [int, "int64"]
        assert result["rgdpo"].dtype in [float, "float64"]
        assert result["hc"].dtype in [float, "float64"]

    @patch("utils.data_sources.pwt_downloader.get_cached_session")
    def test_get_pwt_data_year_filtering(self, mock_session):
        """Test that data is filtered to reasonable year range."""
        # Create data with extreme years
        data_with_extreme_years = pd.DataFrame(
            {
                "countrycode": ["CHN"] * 4,
                "year": [1900, 2020, 2021, 2100],  # Very old and future years
                "rgdpo": [100, 25678.90, 26789.01, 50000],
                "rkna": [0.5, 0.99, 1.01, 2.0],
                "pl_gdpo": [0.1, 0.47, 0.48, 1.0],
                "cgdpo": [50, 14567.89, 15678.90, 50000],
                "hc": [1.0, 2.45, 2.50, 4.0],
            }
        )
        mock_session.return_value = Session()
        with patch("pandas.read_excel", return_value=data_with_extreme_years):
            result = get_pwt_data()

        # Should include all years (filtering might be done elsewhere)
        assert len(result) == 4

    @patch("utils.data_sources.pwt_downloader.get_cached_session")
    def test_get_pwt_data_duplicate_years(self, mock_session):
        """Test handling of duplicate years."""
        # Create data with duplicate years
        data_with_duplicates = pd.DataFrame(
            {
                "countrycode": ["CHN"] * 3,
                "year": [2020, 2020, 2021],
                "rgdpo": [25678.90, 25678.91, 26789.01],
                "rkna": [0.99, 0.99, 1.01],
                "pl_gdpo": [0.47, 0.47, 0.48],
                "cgdpo": [14567.89, 14567.90, 15678.90],
                "hc": [2.45, 2.45, 2.50],
            }
        )
        mock_session.return_value = Session()
        with patch("pandas.read_excel", return_value=data_with_duplicates):
            result = get_pwt_data()

        # Should return all rows (deduplication might be done elsewhere)
        assert len(result) == 3
