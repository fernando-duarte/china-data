import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from utils.data_sources.pwt_downloader import get_pwt_data


class TestPWTDownloader:
    """Test suite for PWT (Penn World Table) downloader."""
    
    @pytest.fixture
    def mock_pwt_data(self):
        """Create mock PWT data for testing."""
        return pd.DataFrame({
            'countrycode': ['CHN'] * 5 + ['USA'] * 5,
            'year': [2018, 2019, 2020, 2021, 2022] * 2,
            'rgdpo': [23456.78, 24567.89, 25678.90, 26789.01, 27890.12] * 2,
            'rkna': [0.95, 0.97, 0.99, 1.01, 1.03] * 2,
            'pl_gdpo': [0.45, 0.46, 0.47, 0.48, 0.49] * 2,
            'cgdpo': [12345.67, 13456.78, 14567.89, 15678.90, 16789.01] * 2,
            'hc': [2.34, 2.40, 2.45, 2.50, 2.55] * 2,
            'pop': [1400.5, 1410.2, 1420.1, 1430.0, 1440.0] * 2,
            'emp': [770.5, 775.2, 780.1, 785.0, 790.0] * 2,
            'avh': [2100, 2110, 2120, 2130, 2140] * 2,
            'ccon': [7000.5, 7500.2, 8000.1, 8500.0, 9000.0] * 2,
            'cda': [5000.5, 5200.2, 5400.1, 5600.0, 5800.0] * 2
        })
    
    @patch('pandas_datareader.wb.download')
    def test_get_pwt_data_success(self, mock_download, mock_pwt_data):
        """Test successful PWT data download."""
        # Set up mock
        mock_download.return_value = mock_pwt_data
        
        # Call function
        result = get_pwt_data()
        
        # Verify download was called with correct parameters
        mock_download.assert_called_once()
        call_args = mock_download.call_args
        assert call_args[1]['indicator'] == 'PWT'
        assert call_args[1]['country'] == 'all'
        assert call_args[1]['start'] == 1950
        assert call_args[1]['end'] == 2023
        
        # Verify result contains only China data
        assert len(result) == 5
        assert all(result['countrycode'] == 'CHN')
        
        # Verify required columns are present
        required_columns = ['year', 'rgdpo', 'rkna', 'pl_gdpo', 'cgdpo', 'hc']
        for col in required_columns:
            assert col in result.columns
    
    @patch('pandas_datareader.wb.download')
    def test_get_pwt_data_empty_response(self, mock_download):
        """Test handling of empty response from API."""
        # Set up mock to return empty DataFrame
        mock_download.return_value = pd.DataFrame()
        
        # Call function
        result = get_pwt_data()
        
        # Should return empty DataFrame
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    @patch('pandas_datareader.wb.download')
    def test_get_pwt_data_no_china_data(self, mock_download):
        """Test handling when no China data is present."""
        # Create data without China
        data_without_china = pd.DataFrame({
            'countrycode': ['USA', 'GBR', 'FRA'],
            'year': [2020, 2020, 2020],
            'rgdpo': [20000, 3000, 2500],
            'rkna': [1.0, 1.0, 1.0],
            'pl_gdpo': [1.0, 0.9, 0.85],
            'cgdpo': [20000, 2700, 2125],
            'hc': [3.5, 3.4, 3.3]
        })
        mock_download.return_value = data_without_china
        
        # Call function
        result = get_pwt_data()
        
        # Should return empty DataFrame
        assert len(result) == 0
    
    @patch('pandas_datareader.wb.download')
    def test_get_pwt_data_missing_columns(self, mock_download):
        """Test handling when some columns are missing."""
        # Create data with missing columns
        incomplete_data = pd.DataFrame({
            'countrycode': ['CHN'],
            'year': [2020],
            'rgdpo': [25678.90],
            # Missing other columns
        })
        mock_download.return_value = incomplete_data
        
        # Call function
        result = get_pwt_data()
        
        # Should still return the data, even if incomplete
        assert len(result) == 1
        assert 'rgdpo' in result.columns
    
    @patch('pandas_datareader.wb.download')
    def test_get_pwt_data_exception_handling(self, mock_download):
        """Test exception handling during download."""
        # Set up mock to raise exception
        mock_download.side_effect = Exception("Connection error")
        
        # Call function - should not raise exception
        result = get_pwt_data()
        
        # Should return empty DataFrame on error
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    @patch('pandas_datareader.wb.download')
    def test_get_pwt_data_data_types(self, mock_download, mock_pwt_data):
        """Test that data types are correct."""
        mock_download.return_value = mock_pwt_data
        
        result = get_pwt_data()
        
        # Check data types
        assert result['year'].dtype in [int, 'int64']
        assert result['rgdpo'].dtype in [float, 'float64']
        assert result['hc'].dtype in [float, 'float64']
    
    @patch('pandas_datareader.wb.download')
    def test_get_pwt_data_year_filtering(self, mock_download):
        """Test that data is filtered to reasonable year range."""
        # Create data with extreme years
        data_with_extreme_years = pd.DataFrame({
            'countrycode': ['CHN'] * 4,
            'year': [1900, 2020, 2021, 2100],  # Very old and future years
            'rgdpo': [100, 25678.90, 26789.01, 50000],
            'rkna': [0.5, 0.99, 1.01, 2.0],
            'pl_gdpo': [0.1, 0.47, 0.48, 1.0],
            'cgdpo': [50, 14567.89, 15678.90, 50000],
            'hc': [1.0, 2.45, 2.50, 4.0]
        })
        mock_download.return_value = data_with_extreme_years
        
        result = get_pwt_data()
        
        # Should include all years (filtering might be done elsewhere)
        assert len(result) == 4
    
    @patch('pandas_datareader.wb.download')
    def test_get_pwt_data_duplicate_years(self, mock_download):
        """Test handling of duplicate years."""
        # Create data with duplicate years
        data_with_duplicates = pd.DataFrame({
            'countrycode': ['CHN'] * 3,
            'year': [2020, 2020, 2021],
            'rgdpo': [25678.90, 25678.91, 26789.01],
            'rkna': [0.99, 0.99, 1.01],
            'pl_gdpo': [0.47, 0.47, 0.48],
            'cgdpo': [14567.89, 14567.90, 15678.90],
            'hc': [2.45, 2.45, 2.50]
        })
        mock_download.return_value = data_with_duplicates
        
        result = get_pwt_data()
        
        # Should return all rows (deduplication might be done elsewhere)
        assert len(result) == 3
    
    @patch('pandas_datareader.wb.download')
    def test_get_pwt_data_column_order(self, mock_download, mock_pwt_data):
        """Test that columns are in expected order."""
        mock_download.return_value = mock_pwt_data
        
        result = get_pwt_data()
        
        # Check that year is first column (common convention)
        assert list(result.columns)[0] == 'year'
    
    @patch('pandas_datareader.wb.download')
    @patch('logging.Logger.warning')
    def test_get_pwt_data_logs_warning_on_error(self, mock_log, mock_download):
        """Test that warnings are logged on errors."""
        mock_download.side_effect = Exception("API Error")
        
        result = get_pwt_data()
        
        # Should log warning
        mock_log.assert_called()
        
        # Should return empty DataFrame
        assert len(result) == 0 