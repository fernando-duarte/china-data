from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest

from config import Config
from utils.economic_indicators import calculate_economic_indicators, calculate_tfp


class TestEconomicIndicatorsExtra:
    """Additional tests for economic indicators."""
    def test_total_savings_calculation(self, complete_data):
        """Test total savings calculation."""
        result = calculate_economic_indicators(complete_data)

        assert "S_USD_bn" in result.columns
        expected_savings = complete_data["GDP_USD_bn"] - complete_data["C_USD_bn"] - complete_data["G_USD_bn"]
        pd.testing.assert_series_equal(result["S_USD_bn"], expected_savings, check_names=False)

    def test_private_savings_calculation(self, complete_data):
        """Test private savings calculation."""
        result = calculate_economic_indicators(complete_data)

        assert "S_priv_USD_bn" in result.columns
        # Private savings = GDP - Tax - Consumption
        expected_priv_savings = complete_data["GDP_USD_bn"] - result["T_USD_bn"] - complete_data["C_USD_bn"]
        pd.testing.assert_series_equal(result["S_priv_USD_bn"], expected_priv_savings, check_names=False)

    def test_public_savings_calculation(self, complete_data):
        """Test public savings calculation."""
        result = calculate_economic_indicators(complete_data)

        assert "S_pub_USD_bn" in result.columns
        # Public savings = Tax - Government spending
        expected_pub_savings = result["T_USD_bn"] - complete_data["G_USD_bn"]
        pd.testing.assert_series_equal(result["S_pub_USD_bn"], expected_pub_savings, check_names=False)

    def test_saving_rate_calculation(self, complete_data):
        """Test saving rate calculation."""
        result = calculate_economic_indicators(complete_data)

        assert "Saving_Rate" in result.columns
        # Calculate expected_rate then round it to the same precision as in the code
        expected_rate_unrounded = result["S_USD_bn"] / complete_data["GDP_USD_bn"]
        expected_rate_rounded = expected_rate_unrounded.round(Config.DECIMAL_PLACES_RATIOS)

        assert result["Saving_Rate"].tolist() == pytest.approx(
            expected_rate_rounded.tolist()
        )  # Default approx tolerance

    def test_missing_columns_handling(self):
        """Test handling of missing columns for various calculations."""
        partial_data = pd.DataFrame(
            {
                "year": [2020, 2021],
                "GDP_USD_bn": [1000, 1100],
                "C_USD_bn": [600, 650],
                # Missing other columns
            }
        )

        # Should not raise exception
        result = calculate_economic_indicators(partial_data)

        # Check that result is returned
        assert isinstance(result, pd.DataFrame)

        # Columns that couldn't be calculated should exist but be NaN
        assert "NX_USD_bn" in result.columns
        assert result["NX_USD_bn"].isna().all()  # Missing X and M should result in NaN
        # assert "K_Y_ratio" not in result.columns  # Missing K - K_Y_ratio is not calculated by this func

    def test_with_custom_logger(self, complete_data):
        """Test that custom logger is used when provided."""
        mock_logger = MagicMock()

        calculate_economic_indicators(complete_data, logger=mock_logger)

        # Logger should have been called
        assert mock_logger.info.called

        # Check for specific log messages
        mock_logger.info.assert_any_call("Calculating net exports (NX_USD_bn)")

    def test_nan_handling(self):
        """Test handling of NaN values in input data."""
        data_with_nan = pd.DataFrame(
            {
                "year": [2020, 2021, 2022],
                "GDP_USD_bn": [1000, np.nan, 1200],
                "C_USD_bn": [600, 650, np.nan],
                "G_USD_bn": [150, 160, 170],
                "X_USD_bn": [200, 220, 240],
                "M_USD_bn": [250, np.nan, 270],
            }
        )

        result = calculate_economic_indicators(data_with_nan)

        # Net exports should have NaN where M is NaN
        assert pd.isna(result.loc[1, "NX_USD_bn"])

        # Savings should have NaN where GDP or C is NaN
        assert pd.isna(result.loc[1, "S_USD_bn"])
        assert pd.isna(result.loc[2, "S_USD_bn"])

    @pytest.mark.parametrize("alpha", [0.25, 0.33, 0.5, 0.75])
    def test_different_alpha_values(self, complete_data, alpha):
        """Test calculation with different alpha values."""
        result = calculate_economic_indicators(complete_data, alpha=alpha)

        # TFP should be calculated with the given alpha
        assert "TFP" in result.columns
        assert result["TFP"].notna().all()

    def test_all_indicators_present(self, complete_data):
        """Test that all expected indicators are calculated with complete data."""
        result = calculate_economic_indicators(complete_data)

        expected_columns = [
            "NX_USD_bn",
            # "K_Y_ratio", # Not calculated by this function
            "TFP",
            "T_USD_bn",
            "Openness_Ratio",
            "S_USD_bn",
            "S_priv_USD_bn",
            "S_pub_USD_bn",
            "Saving_Rate",
        ]

        for col in expected_columns:
            assert col in result.columns, f"Missing column: {col}"
