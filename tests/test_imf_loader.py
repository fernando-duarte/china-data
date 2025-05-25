from unittest.mock import MagicMock, mock_open, patch

import numpy as np
import pandas as pd
import pytest

from utils.data_sources.imf_loader import load_imf_tax_data, check_and_update_hash


class TestIMFLoader:
    """Test suite for IMF data loader functions."""

    @pytest.fixture
    def mock_csv_data(self):
        """Create mock CSV data for testing."""
        return pd.DataFrame({
            "COUNTRY": ["CHN", "CHN", "CHN", "USA", "USA"],
            "FREQUENCY": ["A", "A", "A", "A", "A"],
            "INDICATOR": ["G1_S13_POGDP_PT", "G1_S13_POGDP_PT", "G1_S13_POGDP_PT", "G1_S13_POGDP_PT", "G1_S13_POGDP_PT"],
            "TIME_PERIOD": [2020, 2021, 2022, 2020, 2021],
            "OBS_VALUE": [15.2, 15.8, 16.3, 25.5, 26.0],
        })

    @patch("utils.data_sources.imf_loader.check_and_update_hash")
    @patch("utils.data_sources.imf_loader.find_file")
    @patch("pandas.read_csv")
    def test_load_imf_tax_data_success(self, mock_read_csv, mock_find_file, mock_check_hash, mock_csv_data):
        """Test successful loading of IMF tax data."""
        # Set up mocks
        mock_check_hash.return_value = True  # Mock the hash check
        mock_find_file.return_value = "/path/to/dataset_DEFAULT_INTEGRATION_IMF.FAD_FM_5.0.0.csv"
        mock_read_csv.return_value = mock_csv_data

        # Call function
        result = load_imf_tax_data()

        # Verify check_and_update_hash was called
        mock_check_hash.assert_called_once()

        # Verify find_file was called
        mock_find_file.assert_called()

        # Verify read_csv was called with correct path
        mock_read_csv.assert_called_once_with("/path/to/dataset_DEFAULT_INTEGRATION_IMF.FAD_FM_5.0.0.csv")

        # Verify result
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3  # Only China data
        assert "year" in result.columns
        assert "TAX_pct_GDP" in result.columns
        assert all(result["TAX_pct_GDP"] >= 15.0)
        assert all(result["TAX_pct_GDP"] <= 16.3)

    @patch("utils.data_sources.imf_loader.check_and_update_hash")
    @patch("utils.data_sources.imf_loader.find_file")
    def test_load_imf_tax_data_file_not_found(self, mock_find_file, mock_check_hash):
        """Test handling when IMF file is not found."""
        mock_check_hash.return_value = False
        mock_find_file.return_value = None

        result = load_imf_tax_data()

        # Should return empty DataFrame
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        assert list(result.columns) == ["year", "TAX_pct_GDP"]

    @patch("utils.data_sources.imf_loader.check_and_update_hash")
    @patch("utils.data_sources.imf_loader.find_file")
    @patch("pandas.read_csv")
    def test_load_imf_tax_data_no_china_data(self, mock_read_csv, mock_find_file, mock_check_hash):
        """Test handling when no China data is present."""
        # Create data without China
        data_without_china = pd.DataFrame({
            "COUNTRY": ["USA", "UK", "FRA"],
            "FREQUENCY": ["A", "A", "A"],
            "INDICATOR": ["G1_S13_POGDP_PT", "G1_S13_POGDP_PT", "G1_S13_POGDP_PT"],
            "TIME_PERIOD": [2020, 2020, 2020],
            "OBS_VALUE": [25.5, 30.0, 35.0],
        })

        mock_check_hash.return_value = True
        mock_find_file.return_value = "/path/to/imf_data.csv"
        mock_read_csv.return_value = data_without_china

        result = load_imf_tax_data()

        # Should return empty DataFrame
        assert len(result) == 0

    @patch("utils.data_sources.imf_loader.check_and_update_hash")
    @patch("utils.data_sources.imf_loader.find_file")
    @patch("pandas.read_csv")
    def test_load_imf_tax_data_data_types(self, mock_read_csv, mock_find_file, mock_check_hash, mock_csv_data):
        """Test that data types are correct."""
        mock_check_hash.return_value = True
        mock_find_file.return_value = "/path/to/imf_data.csv"
        mock_read_csv.return_value = mock_csv_data

        result = load_imf_tax_data()

        # Check data types
        assert result["year"].dtype in [int, "int64", "int32"]
        assert result["TAX_pct_GDP"].dtype in [float, "float64"]

    @patch("utils.data_sources.imf_loader.find_file")
    @patch("builtins.open", new_callable=mock_open, read_data=b"test data")
    @patch("os.path.exists")
    def test_check_and_update_hash_new_file(self, mock_exists, mock_file, mock_find_file):
        """Test check_and_update_hash when download_date.txt doesn't exist."""
        # Mock file locations
        mock_find_file.side_effect = [
            "/path/to/dataset_DEFAULT_INTEGRATION_IMF.FAD_FM_5.0.0.csv",  # IMF file
            None  # download_date.txt doesn't exist
        ]
        mock_exists.return_value = False

        result = check_and_update_hash()

        # Should return True (hash was updated)
        assert result == True

    @patch("utils.data_sources.imf_loader.find_file")
    def test_check_and_update_hash_no_imf_file(self, mock_find_file):
        """Test check_and_update_hash when IMF file is not found."""
        mock_find_file.return_value = None

        result = check_and_update_hash()

        # Should return False
        assert result == False
