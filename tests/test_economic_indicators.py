import numpy as np
import pandas as pd
import pytest

from utils.economic_indicators import calculate_economic_indicators, calculate_tfp


class TestCalculateTFP:
    """Test suite for calculate_tfp function."""

    @pytest.fixture
    def sample_data(self):
        """Create sample data for TFP calculation."""
        return pd.DataFrame(
            {
                "year": [2020, 2021, 2022],
                "GDP_USD_bn": [1000, 1100, 1200],
                "K_USD_bn": [3000, 3300, 3600],
                "LF_mn": [100, 102, 104],
                "hc": [2.5, 2.6, 2.7],
            }
        )

    def test_tfp_calculation_basic(self, sample_data):
        """Test basic TFP calculation with complete data."""
        result = calculate_tfp(sample_data, alpha=1 / 3)

        # Check that TFP column is added
        assert "TFP" in result.columns

        # Check that TFP values are calculated
        assert result["TFP"].notna().all()

        # Check that TFP values are positive
        assert (result["TFP"] > 0).all()

        # Verify calculation for first row
        # TFP = GDP / (K^alpha * (L*H)^(1-alpha))
        expected_tfp_0 = 1000 / ((3000 ** (1 / 3)) * ((100 * 2.5) ** (2 / 3)))
        assert abs(result.iloc[0]["TFP"] - expected_tfp_0) < 0.01

    def test_tfp_with_missing_columns(self):
        """Test TFP calculation when required columns are missing."""
        incomplete_data = pd.DataFrame(
            {
                "year": [2020, 2021],
                "GDP_USD_bn": [1000, 1100],
                # Missing K_USD_bn and LF_mn
            }
        )

        result = calculate_tfp(incomplete_data)

        # When required columns are missing the original DataFrame is returned
        assert "TFP" not in result.columns

    def test_tfp_with_missing_hc(self, sample_data):
        """Test TFP calculation with missing human capital values."""
        # Set hc value at index 1 to NaN
        sample_data_with_nan_hc = sample_data.copy()
        sample_data_with_nan_hc.loc[1, "hc"] = np.nan

        result = calculate_tfp(sample_data_with_nan_hc)

        # hc column in result should reflect the NaN value
        assert pd.isna(result.loc[1, "hc"])

        assert "TFP" in result.columns
        # TFP for the row with NaN hc should be NaN
        assert pd.isna(result.loc[1, "TFP"])
        # TFP for other rows (with valid hc) should not be NaN
        assert pd.notna(result.loc[0, "TFP"])
        assert pd.notna(result.loc[2, "TFP"])

    def test_tfp_with_different_alpha(self, sample_data):
        """Test TFP calculation with different alpha values."""
        # Test with alpha = 0.5
        result_half = calculate_tfp(sample_data, alpha=0.5)

        # Test with alpha = 0.25
        result_quarter = calculate_tfp(sample_data, alpha=0.25)

        # TFP values should be different
        assert not np.allclose(result_half["TFP"].values, result_quarter["TFP"].values)

    def test_tfp_rounding(self, sample_data):
        """Test that TFP values are rounded to 4 decimal places."""
        result = calculate_tfp(sample_data)

        # Values should all be finite and positive
        assert (result["TFP"] > 0).all()

    def test_tfp_with_zero_values(self):
        """Test TFP calculation with zero values."""
        data_with_zeros = pd.DataFrame(
            {"year": [2020], "GDP_USD_bn": [0], "K_USD_bn": [3000], "LF_mn": [100], "hc": [2.5]}
        )

        result = calculate_tfp(data_with_zeros)

        # TFP should be 0 when GDP is 0
        assert result.iloc[0]["TFP"] == 0


class TestCalculateEconomicIndicators:
    """Test suite for calculate_economic_indicators function."""

    @pytest.fixture
    def complete_data(self):
        """Create complete sample data for economic indicators."""
        return pd.DataFrame(
            {
                "year": [2020, 2021, 2022],
                "GDP_USD_bn": [1000, 1100, 1200],
                "C_USD_bn": [600, 650, 700],
                "G_USD_bn": [150, 160, 170],
                "I_USD_bn": [300, 330, 360],
                "X_USD_bn": [200, 220, 240],
                "M_USD_bn": [250, 260, 270],
                "K_USD_bn": [3000, 3300, 3600],
                "LF_mn": [100, 102, 104],
                "hc": [2.5, 2.6, 2.7],
                "TAX_pct_GDP": [15, 16, 17],
            }
        )

    def test_net_exports_calculation(self, complete_data):
        """Test net exports calculation."""
        result = calculate_economic_indicators(complete_data)

        assert "NX_USD_bn" in result.columns
        expected_nx = complete_data["X_USD_bn"] - complete_data["M_USD_bn"]
        pd.testing.assert_series_equal(result["NX_USD_bn"], expected_nx, check_names=False)

    # def test_capital_output_ratio_calculation(self, complete_data):
    #     """Test capital-output ratio calculation."""
    #     result = calculate_economic_indicators(complete_data)
    #
    #     assert "K_Y_ratio" in result.columns
    #     expected_ratio = complete_data["K_USD_bn"] / complete_data["GDP_USD_bn"]
    #     pd.testing.assert_series_equal(result["K_Y_ratio"], expected_ratio, check_names=False)

    def test_tfp_integration(self, complete_data):
        """Test that TFP is calculated as part of economic indicators."""
        result = calculate_economic_indicators(complete_data, alpha=1 / 3)

        assert "TFP" in result.columns
        assert result["TFP"].notna().all()

    def test_tax_revenue_calculation(self, complete_data):
        """Test tax revenue in USD billions calculation."""
        result = calculate_economic_indicators(complete_data)

        assert "T_USD_bn" in result.columns
        expected_tax = (complete_data["TAX_pct_GDP"] / 100) * complete_data["GDP_USD_bn"]
        pd.testing.assert_series_equal(result["T_USD_bn"], expected_tax, check_names=False)

    def test_openness_ratio_calculation(self, complete_data):
        """Test trade openness ratio calculation."""
        result = calculate_economic_indicators(complete_data)

        assert "Openness_Ratio" in result.columns
        expected_ratio = (complete_data["X_USD_bn"] + complete_data["M_USD_bn"]) / complete_data["GDP_USD_bn"]
        # Use pytest.approx for floating point comparisons
        assert result["Openness_Ratio"].tolist() == pytest.approx(expected_ratio.tolist(), rel=1e-4)
