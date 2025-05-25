"""Tests for the format_data_for_output function."""

import numpy as np
import pandas as pd
import pytest

from utils.processor_output import format_data_for_output


class TestFormatDataForOutput:
    """Test suite for format_data_for_output function."""

    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        return pd.DataFrame(
            {
                "Year": [2020, 2021, 2022],
                "GDP": [14722.73, 17744.64, 17886.33],
                "Consumption": [8123.4567, 9234.5678, 10345.6789],
                "Population": [1439323776.0, 1444216107.0, 1448471404.0],
                "Labor Force": [774253000.0, 775931000.0, 777610000.0],
                "FDI (% of GDP)": [1.2345, 1.3456, 1.4567],
                "TFP": [2.3456, 2.4567, 2.5678],
                "Human Capital": [2.3400, 2.4500, 2.5600],
                "Openness Ratio": [0.4567, 0.4678, 0.4789],
                "Saving Rate": [0.3456, 0.3567, 0.3678],
            }
        )

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
        data_with_nan = pd.DataFrame(
            {"Year": [2020, 2021], "GDP": [14722.73, np.nan], "Population": [np.nan, 1444216107.0]}
        )

        result = format_data_for_output(data_with_nan)

        # NaN should be converted to 'nan'
        assert result.loc[1, "GDP"] == "nan"
        assert result.loc[0, "Population"] == "nan"

    def test_year_formatting(self, sample_data):
        """Test that years are formatted as strings without decimals."""
        result = format_data_for_output(sample_data)

        # Years should be simple strings
        assert result["Year"].tolist() == ["2020", "2021", "2022"]

    def test_percentage_formatting(self, sample_data):
        """Test formatting of percentage columns."""
        result = format_data_for_output(sample_data)

        # FDI should have 4 decimal places
        assert result.loc[0, "FDI (% of GDP)"] == "1.2345"

        # Saving Rate should have 4 decimal places
        assert result.loc[0, "Saving Rate"] == "0.3456"

    def test_large_number_formatting(self, sample_data):
        """Test formatting of large numbers (GDP, Population, etc.)."""
        result = format_data_for_output(sample_data)

        # GDP should have 4 decimal places
        assert result.loc[0, "GDP"] == "14722.73"

        # Population should have 2 decimal places
        assert result.loc[0, "Population"] == "1439323776"

    def test_tfp_hc_formatting(self, sample_data):
        """Test formatting of TFP and Human Capital."""
        result = format_data_for_output(sample_data)

        # TFP should have 4 decimal places
        assert result.loc[0, "TFP"] == "2.3456"

        # Human Capital should have 4 decimal places
        assert result.loc[0, "Human Capital"] == "2.34"

    def test_trailing_zero_removal(self):
        """Test that trailing zeros are removed."""
        data = pd.DataFrame({"Year": [2020], "GDP": [1000.0000], "TFP": [2.3000], "Population": [1000000.00]})

        result = format_data_for_output(data)

        # Trailing zeros should be removed
        assert result.loc[0, "GDP"] == "1000"
        assert result.loc[0, "TFP"] == "2.3"
        assert result.loc[0, "Population"] == "1000000"

    def test_unknown_column_formatting(self):
        """Test formatting of columns not explicitly handled."""
        data = pd.DataFrame({"Year": [2020], "Unknown_Column": [123.456789]})

        result = format_data_for_output(data)

        # Unknown columns should get 2 decimal places by default
        assert result.loc[0, "Unknown_Column"] == "123.46" 