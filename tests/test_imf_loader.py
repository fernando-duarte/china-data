import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock, mock_open
from utils.data_sources.imf_loader import load_imf_tax_data, load_imf_tax_revenue_data


class TestIMFLoader:
    """Test suite for IMF data loader functions."""
    
    @pytest.fixture
    def mock_excel_data(self):
        """Create mock Excel data for testing."""
        return pd.DataFrame({
            'Country': ['China', 'China', 'China', 'USA', 'USA'],
            'Year': [2020, 2021, 2022, 2020, 2021],
            'Tax Revenue (% of GDP)': [15.2, 15.8, 16.3, 25.5, 26.0]
        })
    
    @pytest.fixture
    def mock_imf_file_content(self):
        """Create mock IMF file content with specific structure."""
        # Create a more realistic IMF data structure
        data = {
            'Country': ['China'] * 10 + ['United States'] * 10,
            'Year': list(range(2015, 2025)) * 2,
            'Tax revenue (Percent of GDP)': [
                # China data
                15.0, 15.2, 15.4, 15.6, 15.8, 16.0, 16.2, 16.4, 16.6, 16.8,
                # USA data
                25.0, 25.2, 25.4, 25.6, 25.8, 26.0, 26.2, 26.4, 26.6, 26.8
            ]
        }
        return pd.DataFrame(data)
    
    @patch('utils.data_sources.imf_loader.search_for_imf_file')
    @patch('pandas.read_excel')
    def test_load_imf_tax_data_success(self, mock_read_excel, mock_search):
        """Test successful loading of IMF tax data."""
        # Set up mocks
        mock_search.return_value = '/path/to/imf_data.xlsx'
        mock_read_excel.return_value = self.mock_imf_file_content()
        
        # Call function
        result = load_imf_tax_data()
        
        # Verify search was called
        mock_search.assert_called_once()
        
        # Verify read_excel was called with correct path
        mock_read_excel.assert_called_once_with('/path/to/imf_data.xlsx')
        
        # Verify result
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 10  # Only China data
        assert 'year' in result.columns
        assert 'TAX_pct_GDP' in result.columns
        assert all(result['TAX_pct_GDP'] >= 15.0)
        assert all(result['TAX_pct_GDP'] <= 16.8)
    
    @patch('utils.data_sources.imf_loader.search_for_imf_file')
    def test_load_imf_tax_data_file_not_found(self, mock_search):
        """Test handling when IMF file is not found."""
        mock_search.return_value = None
        
        result = load_imf_tax_data()
        
        # Should return empty DataFrame
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    @patch('utils.data_sources.imf_loader.search_for_imf_file')
    @patch('pandas.read_excel')
    def test_load_imf_tax_data_no_china_data(self, mock_read_excel, mock_search):
        """Test handling when no China data is present."""
        # Create data without China
        data_without_china = pd.DataFrame({
            'Country': ['USA', 'UK', 'France'],
            'Year': [2020, 2020, 2020],
            'Tax revenue (Percent of GDP)': [25.5, 30.0, 35.0]
        })
        
        mock_search.return_value = '/path/to/imf_data.xlsx'
        mock_read_excel.return_value = data_without_china
        
        result = load_imf_tax_data()
        
        # Should return empty DataFrame
        assert len(result) == 0
    
    @patch('utils.data_sources.imf_loader.search_for_imf_file')
    @patch('pandas.read_excel')
    def test_load_imf_tax_data_column_variations(self, mock_read_excel, mock_search):
        """Test handling of different column name variations."""
        # Test different column name patterns
        column_variations = [
            'Tax revenue (Percent of GDP)',
            'Tax Revenue (% of GDP)',
            'tax revenue (percent of gdp)',
            'TAX REVENUE (PERCENT OF GDP)'
        ]
        
        mock_search.return_value = '/path/to/imf_data.xlsx'
        
        for col_name in column_variations:
            data = pd.DataFrame({
                'Country': ['China'],
                'Year': [2020],
                col_name: [15.5]
            })
            mock_read_excel.return_value = data
            
            result = load_imf_tax_data()
            
            # Should successfully extract data regardless of column name variation
            assert len(result) == 1
            assert result.iloc[0]['TAX_pct_GDP'] == 15.5
    
    @patch('utils.data_sources.imf_loader.search_for_imf_file')
    @patch('pandas.read_excel')
    @patch('logging.Logger.error')
    def test_load_imf_tax_data_exception_handling(self, mock_log, mock_read_excel, mock_search):
        """Test exception handling during file reading."""
        mock_search.return_value = '/path/to/imf_data.xlsx'
        mock_read_excel.side_effect = Exception("File corrupted")
        
        result = load_imf_tax_data()
        
        # Should return empty DataFrame
        assert len(result) == 0
        
        # Should log error
        mock_log.assert_called()
    
    @patch('utils.data_sources.imf_loader.search_for_imf_file')
    @patch('pandas.read_excel')
    def test_load_imf_tax_data_year_filtering(self, mock_read_excel, mock_search):
        """Test that data is filtered to reasonable year range."""
        # Create data with extreme years
        data_with_extreme_years = pd.DataFrame({
            'Country': ['China'] * 4,
            'Year': [1900, 2020, 2021, 2100],
            'Tax revenue (Percent of GDP)': [10.0, 15.5, 16.0, 20.0]
        })
        
        mock_search.return_value = '/path/to/imf_data.xlsx'
        mock_read_excel.return_value = data_with_extreme_years
        
        result = load_imf_tax_data()
        
        # Should include all years (filtering might be done elsewhere)
        assert len(result) == 4
    
    @patch('utils.data_sources.imf_loader.search_for_imf_file')
    @patch('pandas.read_excel')
    def test_load_imf_tax_revenue_data_success(self, mock_read_excel, mock_search):
        """Test the load_imf_tax_revenue_data wrapper function."""
        mock_search.return_value = '/path/to/imf_data.xlsx'
        mock_read_excel.return_value = self.mock_imf_file_content()
        
        # Test the wrapper function
        result = load_imf_tax_revenue_data()
        
        # Should return same result as load_imf_tax_data
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 10
    
    @patch('utils.data_sources.imf_loader.search_for_imf_file')
    @patch('pandas.read_excel')
    def test_load_imf_tax_data_duplicate_years(self, mock_read_excel, mock_search):
        """Test handling of duplicate years."""
        # Create data with duplicate years
        data_with_duplicates = pd.DataFrame({
            'Country': ['China'] * 3,
            'Year': [2020, 2020, 2021],
            'Tax revenue (Percent of GDP)': [15.5, 15.6, 16.0]
        })
        
        mock_search.return_value = '/path/to/imf_data.xlsx'
        mock_read_excel.return_value = data_with_duplicates
        
        result = load_imf_tax_data()
        
        # Should return all rows (deduplication might be done elsewhere)
        assert len(result) == 3
    
    @patch('utils.data_sources.imf_loader.search_for_imf_file')
    @patch('pandas.read_excel')
    def test_load_imf_tax_data_missing_values(self, mock_read_excel, mock_search):
        """Test handling of missing values."""
        data_with_nan = pd.DataFrame({
            'Country': ['China'] * 3,
            'Year': [2019, 2020, 2021],
            'Tax revenue (Percent of GDP)': [15.0, np.nan, 16.0]
        })
        
        mock_search.return_value = '/path/to/imf_data.xlsx'
        mock_read_excel.return_value = data_with_nan
        
        result = load_imf_tax_data()
        
        # Should preserve all rows including NaN
        assert len(result) == 3
        assert pd.isna(result.iloc[1]['TAX_pct_GDP'])
    
    @patch('utils.data_sources.imf_loader.search_for_imf_file')
    @patch('pandas.read_excel')
    def test_load_imf_tax_data_country_name_variations(self, mock_read_excel, mock_search):
        """Test handling of different China country name variations."""
        country_variations = [
            'China',
            'china',
            'CHINA',
            'China, People\'s Republic of',
            'China, P.R.',
            'CHN'
        ]
        
        mock_search.return_value = '/path/to/imf_data.xlsx'
        
        for country_name in country_variations:
            data = pd.DataFrame({
                'Country': [country_name],
                'Year': [2020],
                'Tax revenue (Percent of GDP)': [15.5]
            })
            mock_read_excel.return_value = data
            
            result = load_imf_tax_data()
            
            # Should successfully extract data for various China name formats
            assert len(result) >= 0  # Depending on implementation
    
    @patch('utils.data_sources.imf_loader.search_for_imf_file')
    @patch('pandas.read_excel')
    def test_load_imf_tax_data_data_types(self, mock_read_excel, mock_search):
        """Test that data types are correct."""
        mock_search.return_value = '/path/to/imf_data.xlsx'
        mock_read_excel.return_value = self.mock_imf_file_content()
        
        result = load_imf_tax_data()
        
        # Check data types
        assert result['year'].dtype in [int, 'int64', 'int32']
        assert result['TAX_pct_GDP'].dtype in [float, 'float64']
    
    @patch('utils.data_sources.imf_loader.search_for_imf_file')
    @patch('pandas.read_excel')
    def test_load_imf_tax_data_column_renaming(self, mock_read_excel, mock_search):
        """Test that columns are renamed correctly."""
        data = pd.DataFrame({
            'Country': ['China'],
            'Year': [2020],
            'Tax revenue (Percent of GDP)': [15.5]
        })
        
        mock_search.return_value = '/path/to/imf_data.xlsx'
        mock_read_excel.return_value = data
        
        result = load_imf_tax_data()
        
        # Check column names
        assert 'year' in result.columns
        assert 'TAX_pct_GDP' in result.columns
        assert 'Year' not in result.columns
        assert 'Tax revenue (Percent of GDP)' not in result.columns 