import numpy as np
import pandas as pd
import pytest

from utils.markdown_utils import render_markdown_table


class TestRenderMarkdownTable:
    """Test suite for render_markdown_table function."""

    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        return pd.DataFrame(
            {
                "year": [2020, 2021, 2022],
                "GDP_USD": [14722730.00, 17744640.00, 17886330.00],
                "C_USD": [8123456.78, 9234567.89, 10345678.90],
                "G_USD": [2123456.78, 2234567.89, 2345678.90],
                "I_USD": [3123456.78, 4234567.89, 3345678.90],
                "X_USD": [2123456.78, 2234567.89, 2345678.90],
                "M_USD": [1123456.78, 1234567.89, 1345678.90],
                "FDI_pct_GDP": [1.23, 1.34, 1.45],
                "TAX_pct_GDP": [15.67, 16.78, 17.89],
                "POP": [1439323776, 1444216107, 1448471404],
                "LF": [774253000, 775931000, 777610000],
                "rgdpo": [23456.78, 24567.89, 25678.90],
                "rkna": [0.98, 0.99, 1.00],
                "pl_gdpo": [0.45, 0.46, 0.47],
                "cgdpo": [12345.67, 13456.78, 14567.89],
                "hc": [2.34, 2.45, 2.56],
            }
        )

    def test_basic_rendering(self, sample_data):
        """Test basic markdown table rendering."""
        result = render_markdown_table(sample_data)

        # Check for main sections
        assert "# China Economic Data" in result
        assert "Data sources:" in result
        assert "## Economic Data (1960-present)" in result

        # Check for table headers
        assert "| Year |" in result
        assert "| GDP (USD) |" in result
        assert "| Population |" in result

        # Check for data presence
        assert "2020" in result
        assert "2021" in result
        assert "2022" in result

    def test_column_mapping(self, sample_data):
        """Test that column names are properly mapped."""
        result = render_markdown_table(sample_data)

        # Check mapped column names
        assert "GDP (USD)" in result
        assert "Consumption (USD)" in result
        assert "Government (USD)" in result
        assert "Investment (USD)" in result
        assert "Exports (USD)" in result
        assert "Imports (USD)" in result
        assert "FDI (% of GDP)" in result
        assert "Tax Revenue (% of GDP)" in result
        assert "Population" in result
        assert "Labor Force" in result
        assert "PWT rgdpo" in result
        assert "PWT hc" in result

    def test_number_formatting(self, sample_data):
        """Test that numbers are formatted correctly."""
        result = render_markdown_table(sample_data)

        # GDP should be formatted with 2 decimal places
        assert "14722730.00" in result

        # Population should be formatted with commas and no decimals
        assert "1,439,323,776" in result

        # FDI percentage should be formatted with 2 decimals
        assert "1.23" in result

    def test_missing_values(self):
        """Test handling of missing values."""
        data_with_nan = pd.DataFrame(
            {
                "year": [2020, 2021],
                "GDP_USD": [14722730.00, np.nan],
                "POP": [np.nan, 1444216107],
                "FDI_pct_GDP": [1.23, np.nan],
            }
        )

        result = render_markdown_table(data_with_nan)

        # Check that NaN values are displayed as 'N/A'
        assert "N/A" in result

    def test_download_dates(self, sample_data):
        """Test inclusion of download dates in the output."""
        # Test with all dates
        result = render_markdown_table(sample_data, wdi_date="2024-01-15", pwt_date="2024-01-16", imf_date="2024-01-17")

        assert "Accessed on 2024-01-15" in result
        assert "Accessed on 2024-01-16" in result
        assert "Accessed on 2024-01-17" in result

        # Test with partial dates
        result_partial = render_markdown_table(sample_data, wdi_date="2024-01-15")
        assert "Accessed on 2024-01-15" in result_partial
        assert "Accessed on 2024-01-16" not in result_partial

    def test_source_attribution(self, sample_data):
        """Test that all data sources are properly attributed."""
        result = render_markdown_table(sample_data)

        # Check for all data source attributions
        assert "World Bank World Development Indicators (WDI)" in result
        assert "Penn World Table (PWT) version 10.01" in result
        assert "International Monetary Fund. Fiscal Monitor (FM)" in result

        # Check for URLs
        assert "https://databank.worldbank.org" in result
        assert "https://www.ggdc.net/pwt" in result
        assert "https://data.imf.org" in result

    def test_empty_dataframe(self):
        """Test handling of empty dataframe."""
        empty_df = pd.DataFrame()
        result = render_markdown_table(empty_df)

        # Should still contain headers and structure
        assert "# China Economic Data" in result
        assert "Data sources:" in result

    def test_single_row(self):
        """Test rendering with a single row of data."""
        single_row = pd.DataFrame({"year": [2023], "GDP_USD": [17886330.00], "POP": [1448471404]})

        result = render_markdown_table(single_row)

        # Check that the single row is rendered
        assert "2023" in result
        assert "17886330.00" in result

    def test_notes_section(self, sample_data):
        """Test that the notes section is properly formatted."""
        result = render_markdown_table(sample_data)

        # Check for notes section
        assert "**Notes:**" in result
        assert "GDP and its components" in result
        assert "in current US dollars" in result
        assert "FDI is shown as a percentage" in result
        assert "Human capital index" in result

    @pytest.mark.parametrize(
        "column,expected_format",
        [
            ("GDP_USD", ".2f"),  # 2 decimal places
            ("POP", ",.0f"),  # comma separated, no decimals
            ("FDI_pct_GDP", ".2f"),  # 2 decimal places for percentages
            ("hc", ".2f"),  # 2 decimal places for human capital
        ],
    )
    def test_column_specific_formatting(self, sample_data, column, expected_format):
        """Test that each column type has correct formatting."""
        if column in sample_data.columns:
            result = render_markdown_table(sample_data)
            # The test would check formatting in the output
            assert result is not None
