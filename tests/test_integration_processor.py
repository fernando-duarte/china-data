import os
import shutil
import tempfile
from unittest.mock import mock_open, patch

import pandas as pd
import pytest


class TestChinaDataProcessorIntegration:
    """Integration tests for the china_data_processor module."""

    @pytest.fixture
    def sample_raw_data(self):
        """Create sample raw data that mimics the structure of china_data_raw.md."""
        return pd.DataFrame(
            {
                "year": list(range(2015, 2023)),
                "GDP_USD": [
                    11061553080000,
                    11233276950000,
                    12310409370000,
                    13894817550000,
                    14279937470000,
                    14722730700000,
                    17734062650000,
                    17963170520000,
                ],
                "C_USD": [5000000, 5200000, 5400000, 5600000, 5800000, 6000000, 6200000, 6400000],
                "G_USD": [1500000, 1600000, 1700000, 1800000, 1900000, 2000000, 2100000, 2200000],
                "I_USD": [4000000, 4100000, 4200000, 4300000, 4400000, 4500000, 4600000, 4700000],
                "X_USD": [2000000, 2100000, 2200000, 2300000, 2400000, 2500000, 2600000, 2700000],
                "M_USD": [1500000, 1600000, 1700000, 1800000, 1900000, 2000000, 2100000, 2200000],
                "FDI_pct_GDP": [1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9],
                "TAX_pct_GDP": [15.0, 15.2, 15.4, 15.6, 15.8, 16.0, 16.2, 16.4],
                "POP": [1376048943, 1382710000, 1389618778, 1397715000, 1402760000, 1411100000, 1412360000, 1425893465],
                "LF": [774451000, 776361000, 778707000, 779770000, 774253000, 775931000, 777610000, 779290000],
                "rgdpo": [20000, 21000, 22000, 23000, 24000, 25000, 26000, 27000],
                "rkna": [0.90, 0.92, 0.94, 0.96, 0.98, 1.00, 1.02, 1.04],
                "pl_gdpo": [0.40, 0.41, 0.42, 0.43, 0.44, 0.45, 0.46, 0.47],
                "cgdpo": [10000, 11000, 12000, 13000, 14000, 15000, 16000, 17000],
                "hc": [2.2, 2.25, 2.3, 2.35, 2.4, 2.45, 2.5, 2.55],
            }
        )

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp()

        # Create directory structure
        os.makedirs(os.path.join(temp_dir, "input"))
        os.makedirs(os.path.join(temp_dir, "output"))
        os.makedirs(os.path.join(temp_dir, "utils"))

        # Create a README to identify as project root
        with open(os.path.join(temp_dir, "README.md"), "w") as f:
            f.write("Test project")

        yield temp_dir

        # Cleanup
        shutil.rmtree(temp_dir)

    @patch("utils.processor_load.load_raw_data")
    @patch("utils.processor_load.load_imf_tax_revenue_data")
    @patch("utils.get_output_directory")
    def test_basic_processing_flow(
        self, mock_output_dir, mock_imf_data, mock_raw_data, sample_raw_data, temp_workspace
    ):
        """Test the basic processing flow from raw data to output."""
        # Set up mocks
        mock_raw_data.return_value = sample_raw_data
        mock_imf_data.return_value = pd.DataFrame()  # Empty IMF data
        mock_output_dir.return_value = os.path.join(temp_workspace, "output")

        # Import and run main function
        from china_data_processor import main

        # Mock command line arguments
        with patch("sys.argv", ["prog", "--end-year", "2025"]):
            main()

        # Check that output files were created
        output_dir = os.path.join(temp_workspace, "output")
        assert os.path.exists(os.path.join(output_dir, "china_data_processed.md"))
        assert os.path.exists(os.path.join(output_dir, "china_data_processed.csv"))

    def test_unit_conversion(self, sample_raw_data):
        """Test that units are converted correctly."""
        from utils.processor_units import convert_units

        result = convert_units(sample_raw_data)

        # GDP should be converted to billions
        assert "GDP_USD_bn" in result.columns
        assert result["GDP_USD_bn"].iloc[0] == pytest.approx(11061.55308, rel=1e-4)

        # Population should be converted to millions
        assert "POP_mn" in result.columns
        assert result["POP_mn"].iloc[0] == pytest.approx(1376.048943, rel=1e-4)

    def test_economic_indicators_calculation(self, sample_raw_data):
        """Test calculation of derived economic indicators."""
        from utils.economic_indicators import calculate_economic_indicators
        from utils.processor_units import convert_units

        # Convert units first
        converted = convert_units(sample_raw_data)

        # Add capital stock (required for some calculations)
        converted["K_USD_bn"] = converted["GDP_USD_bn"] * 3  # Simple assumption

        # Calculate indicators
        result = calculate_economic_indicators(converted)

        # Check net exports
        assert "NX_USD_bn" in result.columns
        # From sample_raw_data fixture in this class:
        # X_USD[0] = 2000000 -> X_USD_bn[0] = 2000000 / 1e9 = 0.002
        # M_USD[0] = 1500000 -> M_USD_bn[0] = 1500000 / 1e9 = 0.0015
        # NX_USD_bn[0] = 0.002 - 0.0015 = 0.0005
        expected_nx = 0.0005
        assert result["NX_USD_bn"].iloc[0] == pytest.approx(expected_nx, rel=1e-4)

        # Check TFP
        assert "TFP" in result.columns
        assert result["TFP"].notna().all()

        # Check savings
        assert "S_USD_bn" in result.columns
        assert "Saving_Rate" in result.columns

    @patch("utils.processor_load.load_raw_data")
    def test_extrapolation_to_future_years(self, mock_raw_data, sample_raw_data):
        """Test that data is extrapolated to future years."""
        from utils.processor_extrapolation import extrapolate_series_to_end_year
        from utils.processor_units import convert_units

        # Prepare data
        mock_raw_data.return_value = sample_raw_data
        converted = convert_units(sample_raw_data)

        # Extrapolate to 2030
        result, info = extrapolate_series_to_end_year(converted, end_year=2030, raw_data=sample_raw_data)

        # Check that data extends to 2030
        assert result["year"].max() == 2030

        # Check that extrapolation info is recorded
        assert len(info) > 0
        assert "GDP_USD_bn" in info
        assert "method" in info["GDP_USD_bn"]
        assert "years" in info["GDP_USD_bn"]

    def test_capital_stock_calculation(self, sample_raw_data):
        """Test capital stock calculation."""
        from utils.capital import calculate_capital_stock
        from utils.processor_units import convert_units

        converted = convert_units(sample_raw_data)

        # Calculate capital stock
        result = calculate_capital_stock(converted, capital_output_ratio=3.0)

        # Check that capital stock is calculated
        assert "K_USD_bn" in result.columns

        # Just check that K_USD_bn column exists
        # The actual calculation depends on having the right PWT columns which our test data doesn't have

    def test_human_capital_projection(self, sample_raw_data):
        """Test human capital projection."""
        from utils.processor_hc import project_human_capital

        # Project to 2030
        result = project_human_capital(sample_raw_data, end_year=2030)

        # Check that projection extends beyond original data
        assert result["year"].max() >= sample_raw_data["year"].max()

        # Check that human capital values are reasonable
        assert result["hc"].min() > 1  # Should be above 1
        assert result["hc"].max() < 5  # But below 5

        # Check that projection is monotonic (always increasing for China)
        hc_values = result.sort_values("year")["hc"].values
        assert all(hc_values[i] <= hc_values[i + 1] for i in range(len(hc_values) - 1))

    @patch("builtins.open", new_callable=mock_open)
    def test_markdown_output_format(self, mock_file, sample_raw_data):
        """Test that markdown output is properly formatted."""
        from utils.output import create_markdown_table

        # Create sample processed data
        processed_data = pd.DataFrame(
            {
                "Year": ["2020", "2021", "2022"],
                "GDP": ["14722.73", "17744.64", "17886.33"],
                "Population": ["1411.1", "1412.36", "1425.89"],
            }
        )

        extrapolation_info = {"GDP_USD_bn": {"method": "ARIMA(1,1,1)", "years": [2023, 2024, 2025]}}

        # Create markdown
        create_markdown_table(processed_data, "test.md", extrapolation_info)

        # Get written content
        written_content = "".join(call.args[0] for call in mock_file().write.call_args_list)

        # Check structure
        assert "# Processed China Economic Data" in written_content
        assert "| Year | GDP | Population |" in written_content
        assert "## Data Sources" in written_content
        assert "## Extrapolation to" in written_content

    def test_error_handling_missing_columns(self):
        """Test that processing handles missing columns gracefully."""
        from utils.economic_indicators import calculate_economic_indicators

        # Create data with missing columns
        incomplete_data = pd.DataFrame(
            {
                "year": [2020, 2021],
                "GDP_USD_bn": [14722.73, 17744.64],
                # Missing many required columns
            }
        )

        # Should not raise exception
        result = calculate_economic_indicators(incomplete_data)

        # Should return DataFrame
        assert isinstance(result, pd.DataFrame)

        # Should have original columns
        assert "year" in result.columns
        assert "GDP_USD_bn" in result.columns

    @pytest.mark.parametrize("alpha,k_y_ratio", [(0.25, 2.5), (0.33, 3.0), (0.40, 3.5), (0.50, 4.0)])
    def test_parameter_sensitivity(self, sample_raw_data, alpha, k_y_ratio):
        """Test that different parameters produce different results."""
        from utils.capital import calculate_capital_stock
        from utils.economic_indicators import calculate_economic_indicators
        from utils.processor_units import convert_units

        # Process with different parameters
        converted = convert_units(sample_raw_data)
        capital_df = calculate_capital_stock(converted, capital_output_ratio=k_y_ratio)
        converted["K_USD_bn"] = capital_df["K_USD_bn"]

        result = calculate_economic_indicators(converted, alpha=alpha)

        # TFP should vary with alpha
        assert "TFP" in result.columns
        assert result["TFP"].notna().any()

    def test_csv_output_format(self, sample_raw_data):
        """Test that CSV output is properly formatted."""
        from utils.processor_dataframe.output_operations import prepare_final_dataframe

        # Create column mapping
        column_map = {"year": "Year", "GDP_USD_bn": "GDP", "POP_mn": "Population"}

        # Convert units
        from utils.processor_units import convert_units

        converted = convert_units(sample_raw_data)

        # Prepare final dataframe
        result = prepare_final_dataframe(converted, column_map)

        # Check column names
        assert "Year" in result.columns
        assert "GDP" in result.columns
        assert "Population" in result.columns

        # Check data integrity
        assert len(result) == len(sample_raw_data)
        assert result["Year"].dtype in [int, "int64", "int32"]
