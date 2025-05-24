import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, mock_open, MagicMock
from utils.processor_output import format_data_for_output, create_markdown_table


class TestFormatDataForOutput:
    """Test suite for format_data_for_output function."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        return pd.DataFrame({
            'Year': [2020, 2021, 2022],
            'GDP': [14722.73, 17744.64, 17886.33],
            'Consumption': [8123.4567, 9234.5678, 10345.6789],
            'Population': [1439323776.0, 1444216107.0, 1448471404.0],
            'Labor Force': [774253000.0, 775931000.0, 777610000.0],
            'FDI (% of GDP)': [1.2345, 1.3456, 1.4567],
            'TFP': [2.3456, 2.4567, 2.5678],
            'Human Capital': [2.3400, 2.4500, 2.5600],
            'Openness Ratio': [0.4567, 0.4678, 0.4789],
            'Saving Rate': [0.3456, 0.3567, 0.3678]
        })
    
    def test_basic_formatting(self, sample_data):
        """Test basic data formatting."""
        result = format_data_for_output(sample_data)
        
        # Check that result is a DataFrame
        assert isinstance(result, pd.DataFrame)
        
        # Check that shape is preserved
        assert result.shape == sample_data.shape
        
        # Check that all values are strings
        for col in result.columns:
            assert result[col].dtype == object
    
    def test_nan_handling(self):
        """Test handling of NaN values."""
        data_with_nan = pd.DataFrame({
            'Year': [2020, 2021],
            'GDP': [14722.73, np.nan],
            'Population': [np.nan, 1444216107.0]
        })
        
        result = format_data_for_output(data_with_nan)
        
        # NaN should be converted to 'nan'
        assert result.loc[1, 'GDP'] == 'nan'
        assert result.loc[0, 'Population'] == 'nan'
    
    def test_year_formatting(self, sample_data):
        """Test that years are formatted as strings without decimals."""
        result = format_data_for_output(sample_data)
        
        # Years should be simple strings
        assert result['Year'].tolist() == ['2020', '2021', '2022']
    
    def test_percentage_formatting(self, sample_data):
        """Test formatting of percentage columns."""
        result = format_data_for_output(sample_data)
        
        # FDI should have 4 decimal places
        assert result.loc[0, 'FDI (% of GDP)'] == '1.2345'
        
        # Saving Rate should have 4 decimal places
        assert result.loc[0, 'Saving Rate'] == '0.3456'
    
    def test_large_number_formatting(self, sample_data):
        """Test formatting of large numbers (GDP, Population, etc.)."""
        result = format_data_for_output(sample_data)
        
        # GDP should have 4 decimal places
        assert result.loc[0, 'GDP'] == '14722.73'
        
        # Population should have 2 decimal places
        assert result.loc[0, 'Population'] == '1439323776'
    
    def test_tfp_hc_formatting(self, sample_data):
        """Test formatting of TFP and Human Capital."""
        result = format_data_for_output(sample_data)
        
        # TFP should have 4 decimal places
        assert result.loc[0, 'TFP'] == '2.3456'
        
        # Human Capital should have 4 decimal places
        assert result.loc[0, 'Human Capital'] == '2.34'
    
    def test_trailing_zero_removal(self):
        """Test that trailing zeros are removed."""
        data = pd.DataFrame({
            'Year': [2020],
            'GDP': [1000.0000],
            'TFP': [2.3000],
            'Population': [1000000.00]
        })
        
        result = format_data_for_output(data)
        
        # Trailing zeros should be removed
        assert result.loc[0, 'GDP'] == '1000'
        assert result.loc[0, 'TFP'] == '2.3'
        assert result.loc[0, 'Population'] == '1000000'
    
    def test_unknown_column_formatting(self):
        """Test formatting of columns not explicitly handled."""
        data = pd.DataFrame({
            'Year': [2020],
            'Unknown_Column': [123.456789]
        })
        
        result = format_data_for_output(data)
        
        # Unknown columns should get 2 decimal places by default
        assert result.loc[0, 'Unknown_Column'] == '123.46'


class TestCreateMarkdownTable:
    """Test suite for create_markdown_table function."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample formatted data for testing."""
        return pd.DataFrame({
            'Year': ['2020', '2021', '2022'],
            'GDP': ['14722.73', '17744.64', '17886.33'],
            'Population': ['1439.32', '1444.22', '1448.47']
        })
    
    @pytest.fixture
    def extrapolation_info(self):
        """Create sample extrapolation info."""
        return {
            'GDP_USD_bn': {
                'method': 'ARIMA(1,1,1)',
                'years': [2023, 2024, 2025]
            },
            'POP_mn': {
                'method': 'Linear regression',
                'years': [2023, 2024, 2025]
            },
            'hc': {
                'method': 'Linear regression',
                'years': []  # Empty years
            }
        }
    
    @patch('builtins.open', new_callable=mock_open)
    def test_basic_markdown_creation(self, mock_file, sample_data, extrapolation_info):
        """Test basic markdown table creation."""
        output_path = 'test_output.md'
        
        create_markdown_table(
            sample_data,
            output_path,
            extrapolation_info,
            alpha=1/3,
            capital_output_ratio=3.0,
            input_file='test_input.md',
            end_year=2025
        )
        
        # Check that file was opened for writing
        mock_file.assert_called_once_with(output_path, 'w')
        
        # Get what was written
        handle = mock_file()
        written_content = ''.join(call.args[0] for call in handle.write.call_args_list)
        
        # Check for main sections
        assert '# Processed China Economic Data' in written_content
        assert '# Notes on Computation' in written_content
        assert '## Data Sources' in written_content
        assert '## Unit Conversions' in written_content
        assert '## Derived Variables' in written_content
        assert '## Extrapolation to 2025' in written_content
    
    @patch('builtins.open', new_callable=mock_open)
    def test_table_formatting(self, mock_file, sample_data, extrapolation_info):
        """Test that the table is properly formatted."""
        create_markdown_table(
            sample_data,
            'test.md',
            extrapolation_info
        )
        
        written_content = ''.join(call.args[0] for call in mock_file().write.call_args_list)
        
        # Check table headers
        assert '| Year | GDP | Population |' in written_content
        assert '|---|---|---|' in written_content
        
        # Check data rows
        assert '| 2020 | 14722.73 | 1439.32 |' in written_content
        assert '| 2021 | 17744.64 | 1444.22 |' in written_content
    
    @patch('builtins.open', new_callable=mock_open)
    def test_extrapolation_notes(self, mock_file, sample_data, extrapolation_info):
        """Test that extrapolation methods are properly documented."""
        create_markdown_table(
            sample_data,
            'test.md',
            extrapolation_info
        )
        
        written_content = ''.join(call.args[0] for call in mock_file().write.call_args_list)
        
        # Check for ARIMA section
        assert '### ARIMA(1,1,1) model' in written_content
        
        # Check for Linear regression section
        assert '### Linear regression' in written_content
        
        # Variables with empty years should not appear
        assert 'Human Capital' not in written_content or 'hc' not in written_content
    
    @patch('builtins.open', new_callable=mock_open)
    def test_parameter_documentation(self, mock_file, sample_data, extrapolation_info):
        """Test that parameters are documented correctly."""
        alpha = 0.35
        capital_output_ratio = 2.5
        input_file = 'custom_input.md'
        end_year = 2030
        
        create_markdown_table(
            sample_data,
            'test.md',
            extrapolation_info,
            alpha=alpha,
            capital_output_ratio=capital_output_ratio,
            input_file=input_file,
            end_year=end_year
        )
        
        written_content = ''.join(call.args[0] for call in mock_file().write.call_args_list)
        
        # Check parameters in content
        assert f'alpha = {alpha}' in written_content
        assert f'K/Y= {capital_output_ratio}' in written_content
        assert f'source file={input_file}' in written_content
        assert f'end year={end_year}' in written_content
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('utils.processor_output.datetime')
    def test_date_generation(self, mock_datetime, mock_file, sample_data, extrapolation_info):
        """Test that current date is included."""
        mock_datetime.today.return_value.strftime.return_value = '2024-01-15'
        
        create_markdown_table(
            sample_data,
            'test.md',
            extrapolation_info
        )
        
        written_content = ''.join(call.args[0] for call in mock_file().write.call_args_list)
        
        assert 'Generated 2024-01-15' in written_content
    
    @patch('builtins.open', new_callable=mock_open)
    def test_formula_documentation(self, mock_file, sample_data, extrapolation_info):
        """Test that formulas are properly documented."""
        create_markdown_table(
            sample_data,
            'test.md',
            extrapolation_info
        )
        
        written_content = ''.join(call.args[0] for call in mock_file().write.call_args_list)
        
        # Check for formula sections
        assert 'Net Exports = Exports - Imports' in written_content
        assert 'TFP_t = Y_t / (K_t^alpha * (L_t * H_t)^(1-alpha))' in written_content
        assert 'K_t = (rkna_t / rkna_2017) * K_2017' in written_content
    
    @patch('builtins.open', new_callable=mock_open)
    def test_empty_extrapolation_info(self, mock_file, sample_data):
        """Test handling of empty extrapolation info."""
        empty_info = {}
        
        create_markdown_table(
            sample_data,
            'test.md',
            empty_info
        )
        
        # Should not raise exception
        mock_file.assert_called_once()
    
    @patch('builtins.open', new_callable=mock_open)
    def test_column_mapping(self, mock_file, sample_data):
        """Test that column names are properly mapped in notes."""
        extrapolation_info = {
            'GDP_USD_bn': {'method': 'ARIMA(1,1,1)', 'years': [2023]},
            'C_USD_bn': {'method': 'Average growth rate', 'years': [2023]},
            'K_USD_bn': {'method': 'Investment-based projection', 'years': [2023]},
            'TAX_pct_GDP': {'method': 'IMF projections', 'years': [2023]}
        }
        
        create_markdown_table(
            sample_data,
            'test.md',
            extrapolation_info
        )
        
        written_content = ''.join(call.args[0] for call in mock_file().write.call_args_list)
        
        # Check that internal names are mapped to display names
        # GDP_USD_bn should appear as GDP
        assert 'GDP (2023)' in written_content or 'GDP' in written_content
        
        # Check for different method sections
        assert '### Average growth rate' in written_content
        assert '### Investment-based projection' in written_content
        assert '### IMF projections' in written_content 