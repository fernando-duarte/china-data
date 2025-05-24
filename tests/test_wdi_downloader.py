import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from utils.data_sources.wdi_downloader import download_wdi_data


class TestWDIDownloader:
    """Test suite for WDI (World Development Indicators) downloader."""
    
    @pytest.fixture
    def mock_wdi_data(self):
        """Create mock WDI data for testing."""
        return pd.DataFrame({
            'year': [2018, 2019, 2020, 2021, 2022],
            'NY_GDP_MKTP_CD': [13608151.86, 14279937.47, 14722730.70, 17734062.65, 17963170.52]
        })
    
    @patch('pandas_datareader.wb.download')
    def test_download_wdi_data_success(self, mock_download, mock_wdi_data):
        """Test successful WDI data download."""
        # Set up mock
        mock_download.return_value = mock_wdi_data
        
        # Call function
        indicator = 'NY.GDP.MKTP.CD'
        result = download_wdi_data(indicator)
        
        # Verify download was called with correct parameters
        mock_download.assert_called_once()
        call_args = mock_download.call_args
        
        # Check indicator
        assert call_args[1]['indicator'] == indicator
        
        # Check country
        assert call_args[1]['country'] == 'CHN'
        
        # Check date range
        assert call_args[1]['start'] == 1960
        assert 'end' in call_args[1]
        
        # Verify result
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5
        assert 'year' in result.columns
        assert 'NY_GDP_MKTP_CD' in result.columns
    
    @patch('pandas_datareader.wb.download')
    def test_download_wdi_data_custom_end_year(self, mock_download, mock_wdi_data):
        """Test WDI download with custom end year."""
        mock_download.return_value = mock_wdi_data
        
        # Call with custom end year
        result = download_wdi_data('NY.GDP.MKTP.CD', end_year=2030)
        
        # Check that end year was passed correctly
        call_args = mock_download.call_args
        assert call_args[1]['end'] == 2030
    
    @patch('pandas_datareader.wb.download')
    def test_download_wdi_data_empty_response(self, mock_download):
        """Test handling of empty response from API."""
        # Set up mock to return empty DataFrame
        mock_download.return_value = pd.DataFrame()
        
        # Call function
        result = download_wdi_data('NY.GDP.MKTP.CD')
        
        # Should return empty DataFrame
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    @patch('pandas_datareader.wb.download')
    def test_download_wdi_data_exception_handling(self, mock_download):
        """Test exception handling during download."""
        # Set up mock to raise exception
        mock_download.side_effect = Exception("Connection error")
        
        # Call function - should not raise exception
        result = download_wdi_data('NY.GDP.MKTP.CD')
        
        # Should return empty DataFrame on error
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    @patch('pandas_datareader.wb.download')
    @patch('logging.Logger.error')
    def test_download_wdi_data_logs_error(self, mock_log, mock_download):
        """Test that errors are logged."""
        error_msg = "API Error"
        mock_download.side_effect = Exception(error_msg)
        
        result = download_wdi_data('NY.GDP.MKTP.CD')
        
        # Should log error
        mock_log.assert_called()
        log_message = mock_log.call_args[0][0]
        assert "Error downloading" in log_message
        assert error_msg in str(mock_log.call_args)
    
    @patch('pandas_datareader.wb.download')
    def test_download_wdi_data_column_naming(self, mock_download):
        """Test that columns are named correctly."""
        # Create data with dots in column name
        data = pd.DataFrame({
            'year': [2020, 2021],
            'NY.GDP.MKTP.CD': [14722730.70, 17734062.65]
        })
        mock_download.return_value = data
        
        result = download_wdi_data('NY.GDP.MKTP.CD')
        
        # Column name should have dots replaced with underscores
        assert 'NY_GDP_MKTP_CD' in result.columns
        assert 'NY.GDP.MKTP.CD' not in result.columns
    
    @patch('pandas_datareader.wb.download')
    def test_download_wdi_data_year_column(self, mock_download, mock_wdi_data):
        """Test that year column is properly handled."""
        mock_download.return_value = mock_wdi_data
        
        result = download_wdi_data('NY.GDP.MKTP.CD')
        
        # Year should be integer type
        assert result['year'].dtype in [int, 'int64', 'int32']
        
        # Years should be in expected range
        assert result['year'].min() >= 1960
        assert result['year'].max() <= 2030
    
    @patch('pandas_datareader.wb.download')
    def test_download_wdi_data_different_indicators(self, mock_download):
        """Test downloading different indicators."""
        indicators = [
            'NY.GDP.MKTP.CD',  # GDP
            'NE.CON.PRVT.CD',  # Consumption
            'SP.POP.TOTL',     # Population
            'BX.KLT.DINV.WD.GD.ZS'  # FDI
        ]
        
        for indicator in indicators:
            # Reset mock
            mock_download.reset_mock()
            mock_download.return_value = pd.DataFrame({
                'year': [2020],
                indicator: [1000]
            })
            
            result = download_wdi_data(indicator)
            
            # Should call download with correct indicator
            assert mock_download.call_args[1]['indicator'] == indicator
    
    @patch('pandas_datareader.wb.download')
    def test_download_wdi_data_data_types(self, mock_download):
        """Test that data types are preserved correctly."""
        data = pd.DataFrame({
            'year': [2020, 2021],
            'NY.GDP.MKTP.CD': [14722730.70, 17734062.65]
        })
        mock_download.return_value = data
        
        result = download_wdi_data('NY.GDP.MKTP.CD')
        
        # Check data types
        assert result['year'].dtype in [int, 'int64', 'int32']
        assert result['NY_GDP_MKTP_CD'].dtype in [float, 'float64']
    
    @patch('pandas_datareader.wb.download')
    def test_download_wdi_data_duplicate_years(self, mock_download):
        """Test handling of duplicate years."""
        # Create data with duplicate years
        data_with_duplicates = pd.DataFrame({
            'year': [2020, 2020, 2021],
            'NY.GDP.MKTP.CD': [14722730.70, 14722730.71, 17734062.65]
        })
        mock_download.return_value = data_with_duplicates
        
        result = download_wdi_data('NY.GDP.MKTP.CD')
        
        # Should return all rows (deduplication might be done elsewhere)
        assert len(result) == 3
    
    @patch('pandas_datareader.wb.download')
    def test_download_wdi_data_missing_values(self, mock_download):
        """Test handling of missing values."""
        data_with_nan = pd.DataFrame({
            'year': [2019, 2020, 2021],
            'NY.GDP.MKTP.CD': [13608151.86, None, 17734062.65]
        })
        mock_download.return_value = data_with_nan
        
        result = download_wdi_data('NY.GDP.MKTP.CD')
        
        # Should preserve NaN values
        assert pd.isna(result.iloc[1]['NY_GDP_MKTP_CD'])
    
    @patch('pandas_datareader.wb.download')
    @patch('time.sleep')
    def test_no_sleep_in_download(self, mock_sleep, mock_download):
        """Test that download function doesn't include sleep (should be handled by caller)."""
        mock_download.return_value = pd.DataFrame({'year': [2020], 'NY.GDP.MKTP.CD': [1000]})
        
        download_wdi_data('NY.GDP.MKTP.CD')
        
        # Sleep should not be called within the function
        mock_sleep.assert_not_called()
    
    @patch('pandas_datareader.wb.download')
    def test_download_wdi_data_return_type(self, mock_download):
        """Test that function always returns a DataFrame."""
        # Test with valid data
        mock_download.return_value = pd.DataFrame({'year': [2020], 'NY.GDP.MKTP.CD': [1000]})
        result = download_wdi_data('NY.GDP.MKTP.CD')
        assert isinstance(result, pd.DataFrame)
        
        # Test with exception
        mock_download.side_effect = Exception("Error")
        result = download_wdi_data('NY.GDP.MKTP.CD')
        assert isinstance(result, pd.DataFrame)
        
        # Test with empty data
        mock_download.side_effect = None
        mock_download.return_value = pd.DataFrame()
        result = download_wdi_data('NY.GDP.MKTP.CD')
        assert isinstance(result, pd.DataFrame) 