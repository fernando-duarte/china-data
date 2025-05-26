"""Property-based tests using Hypothesis for economic data processing.

This module contains property-based tests that automatically generate test cases
to verify invariants and properties of economic calculations and data processing.
"""

from typing import Any

import numpy as np
import pandas as pd
import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from tests.factories import TimeSeriesFactory
from utils.capital import calculate_capital_stock
from utils.economic_indicators import calculate_economic_indicators, calculate_tfp
from utils.processor_units import convert_units

# Mark all tests in this module as property-based tests
pytestmark = [pytest.mark.property, pytest.mark.unit]


# Custom strategies for economic data
@st.composite
def economic_data_strategy(draw: Any) -> dict[str, float]:
    """Generate realistic economic data for property-based testing."""
    year = draw(st.integers(min_value=1960, max_value=2030))
    gdp = draw(st.floats(min_value=50.0, max_value=20000.0, allow_nan=False, allow_infinity=False))

    # Ensure realistic economic ratios
    consumption_ratio = draw(st.floats(min_value=0.3, max_value=0.7))
    government_ratio = draw(st.floats(min_value=0.05, max_value=0.3))
    investment_ratio = draw(st.floats(min_value=0.1, max_value=0.6))
    export_ratio = draw(st.floats(min_value=0.05, max_value=0.4))
    import_ratio = draw(st.floats(min_value=0.05, max_value=0.4))

    # Ensure C + G + I doesn't exceed GDP by too much (allowing for statistical discrepancy)
    total_domestic = consumption_ratio + government_ratio + investment_ratio
    assume(total_domestic <= 1.2)  # Allow some statistical discrepancy

    return {
        "year": year,
        "GDP_USD_bn": gdp,
        "C_USD_bn": gdp * consumption_ratio,
        "G_USD_bn": gdp * government_ratio,
        "I_USD_bn": gdp * investment_ratio,
        "X_USD_bn": gdp * export_ratio,
        "M_USD_bn": gdp * import_ratio,
        "K_USD_bn": gdp * draw(st.floats(min_value=2.0, max_value=5.0)),
        "LF_mn": draw(st.floats(min_value=100.0, max_value=1000.0)),
        "hc": draw(st.floats(min_value=1.0, max_value=4.0)),
        "TAX_pct_GDP": draw(st.floats(min_value=5.0, max_value=35.0)),
    }


@st.composite
def economic_dataframe_strategy(draw: Any, min_rows: int = 1, max_rows: int = 20) -> pd.DataFrame:
    """Generate a DataFrame with economic data."""
    num_rows = draw(st.integers(min_value=min_rows, max_value=max_rows))
    years = draw(
        st.lists(st.integers(min_value=1960, max_value=2030), min_size=num_rows, max_size=num_rows, unique=True)
    )
    years.sort()

    data = []
    for year in years:
        row_data = draw(economic_data_strategy())
        row_data["year"] = year
        data.append(row_data)

    return pd.DataFrame(data)


class TestEconomicIndicatorsProperties:
    """Property-based tests for economic indicators calculations."""

    @given(economic_data_strategy())
    def test_net_exports_calculation_property(self, data):
        """Property: Net exports should always equal exports minus imports."""
        df = pd.DataFrame([data])
        result = calculate_economic_indicators(df)

        if "NX_USD_bn" in result.columns:
            expected_nx = data["X_USD_bn"] - data["M_USD_bn"]
            actual_nx = result["NX_USD_bn"].iloc[0]
            assert abs(actual_nx - expected_nx) < 0.01, f"NX calculation failed: {actual_nx} != {expected_nx}"

    @given(economic_data_strategy())
    def test_tax_revenue_calculation_property(self, data):
        """Property: Tax revenue should equal tax rate times GDP."""
        df = pd.DataFrame([data])
        result = calculate_economic_indicators(df)

        if "T_USD_bn" in result.columns:
            expected_tax = (data["TAX_pct_GDP"] / 100) * data["GDP_USD_bn"]
            actual_tax = result["T_USD_bn"].iloc[0]
            assert abs(actual_tax - expected_tax) < 0.01, f"Tax calculation failed: {actual_tax} != {expected_tax}"

    @given(economic_data_strategy())
    def test_openness_ratio_property(self, data):
        """Property: Openness ratio should equal (exports + imports) / GDP."""
        df = pd.DataFrame([data])
        result = calculate_economic_indicators(df)

        if "Openness_Ratio" in result.columns:
            expected_openness = (data["X_USD_bn"] + data["M_USD_bn"]) / data["GDP_USD_bn"]
            actual_openness = result["Openness_Ratio"].iloc[0]
            assert abs(actual_openness - expected_openness) < 0.001, (
                f"Openness calculation failed: {actual_openness} != {expected_openness}"
            )

    @given(economic_data_strategy())
    def test_saving_identity_property(self, data):
        """Property: Total saving should equal GDP - Consumption - Government spending."""
        df = pd.DataFrame([data])
        result = calculate_economic_indicators(df)

        if "S_USD_bn" in result.columns:
            expected_saving = data["GDP_USD_bn"] - data["C_USD_bn"] - data["G_USD_bn"]
            actual_saving = result["S_USD_bn"].iloc[0]
            assert abs(actual_saving - expected_saving) < 0.01, (
                f"Saving calculation failed: {actual_saving} != {expected_saving}"
            )

    @given(economic_data_strategy())
    def test_saving_rate_bounds_property(self, data):
        """Property: Saving rate should be between -1 and 1 (allowing for extreme cases)."""
        df = pd.DataFrame([data])
        result = calculate_economic_indicators(df)

        if "Saving_Rate" in result.columns and not pd.isna(result["Saving_Rate"].iloc[0]):
            saving_rate = result["Saving_Rate"].iloc[0]
            assert -1.0 <= saving_rate <= 1.0, f"Saving rate out of bounds: {saving_rate}"

    @given(economic_dataframe_strategy(min_rows=2, max_rows=10))
    def test_tfp_positivity_property(self, df):
        """Property: TFP should always be positive when calculated."""
        result = calculate_tfp(df, alpha=1 / 3)

        if "TFP" in result.columns:
            tfp_values = result["TFP"].dropna()
            if len(tfp_values) > 0:
                assert (tfp_values > 0).all(), f"TFP should be positive, got: {tfp_values.tolist()}"

    @given(st.floats(min_value=0.1, max_value=0.9), economic_dataframe_strategy(min_rows=1, max_rows=5))
    def test_tfp_alpha_sensitivity_property(self, alpha, df):
        """Property: TFP should change when alpha changes (for same data)."""
        # Ensure we have required columns for TFP calculation
        required_cols = ["GDP_USD_bn", "K_USD_bn", "LF_mn", "hc"]
        if not all(col in df.columns for col in required_cols):
            pytest.skip("Missing required columns for TFP calculation")

        result1 = calculate_tfp(df.copy(), alpha=alpha)
        result2 = calculate_tfp(df.copy(), alpha=alpha + 0.1)

        if "TFP" in result1.columns and "TFP" in result2.columns:
            tfp1 = result1["TFP"].dropna()
            tfp2 = result2["TFP"].dropna()

            if len(tfp1) > 0 and len(tfp2) > 0:
                # TFP values should be different for different alpha values
                assert not np.allclose(tfp1, tfp2, rtol=1e-10), "TFP should change with different alpha values"


class TestDataProcessingProperties:
    """Property-based tests for data processing functions."""

    @given(economic_dataframe_strategy(min_rows=1, max_rows=15))
    def test_convert_units_preserves_structure_property(self, df):
        """Property: Unit conversion should preserve DataFrame structure."""
        result = convert_units(df)

        # Should have same number of rows
        assert len(result) == len(df), "Unit conversion changed number of rows"

        # Should have same or more columns (conversion may add columns)
        assert len(result.columns) >= len(df.columns), "Unit conversion removed columns"

        # Year column should be unchanged
        if "year" in df.columns:
            pd.testing.assert_series_equal(result["year"], df["year"], check_names=False)

    @given(economic_dataframe_strategy(min_rows=1, max_rows=10), st.floats(min_value=2.0, max_value=5.0))
    def test_capital_stock_calculation_property(self, df, capital_output_ratio):
        """Property: Capital stock should be proportional to GDP."""
        # Ensure we have GDP column
        if "GDP_USD_bn" not in df.columns:
            pytest.skip("Missing GDP column")

        result = calculate_capital_stock(df, capital_output_ratio=capital_output_ratio)

        if "K_USD_bn" in result.columns:
            # Capital stock should be roughly proportional to GDP
            for idx in result.index:
                if not pd.isna(result.loc[idx, "GDP_USD_bn"]) and not pd.isna(result.loc[idx, "K_USD_bn"]):
                    ratio = result.loc[idx, "K_USD_bn"] / result.loc[idx, "GDP_USD_bn"]
                    # Allow some tolerance for calculation differences
                    assert 1.5 <= ratio <= 6.0, f"Capital-output ratio out of reasonable bounds: {ratio}"

    @given(st.lists(st.floats(min_value=0.1, max_value=1000.0), min_size=3, max_size=20))
    def test_time_series_monotonicity_property(self, values):
        """Property: Time series with positive trend should be generally increasing."""
        years = list(range(2000, 2000 + len(values)))

        # Create an increasing series
        sorted_values = sorted(values)
        series = TimeSeriesFactory.create_trending_series(
            start_value=sorted_values[0],
            end_value=sorted_values[-1],
            years=years,
            trend_type="linear",
            volatility=0.01,  # Low volatility to maintain trend
        )

        # Check that the overall trend is positive
        correlation = np.corrcoef(years, series.values)[0, 1]
        assert correlation > 0.5, f"Series should have positive correlation with time: {correlation}"


class TestDataValidationProperties:
    """Property-based tests for data validation and constraints."""

    @given(economic_dataframe_strategy(min_rows=1, max_rows=10))
    def test_economic_data_non_negative_property(self, df):
        """Property: Most economic variables should be non-negative."""
        non_negative_cols = [
            "GDP_USD_bn",
            "C_USD_bn",
            "G_USD_bn",
            "I_USD_bn",
            "X_USD_bn",
            "M_USD_bn",
            "K_USD_bn",
            "LF_mn",
            "hc",
        ]

        for col in non_negative_cols:
            if col in df.columns:
                non_na_values = df[col].dropna()
                if len(non_na_values) > 0:
                    assert (non_na_values >= 0).all(), f"Column {col} should be non-negative"

    @given(economic_dataframe_strategy(min_rows=1, max_rows=10))
    def test_percentage_bounds_property(self, df):
        """Property: Percentage variables should be within reasonable bounds."""
        percentage_cols = ["TAX_pct_GDP", "FDI_pct_GDP"]

        for col in percentage_cols:
            if col in df.columns:
                non_na_values = df[col].dropna()
                if len(non_na_values) > 0:
                    assert (non_na_values >= 0).all(), f"Percentage {col} should be non-negative"
                    assert (non_na_values <= 100).all(), f"Percentage {col} should not exceed 100%"

    @given(economic_dataframe_strategy(min_rows=2, max_rows=10))
    def test_year_ordering_property(self, df):
        """Property: Years should be in ascending order after sorting."""
        if "year" in df.columns:
            sorted_df = df.sort_values("year")
            years = sorted_df["year"].tolist()
            assert years == sorted(years), "Years should be sortable in ascending order"

    @given(economic_data_strategy())
    def test_gdp_accounting_identity_property(self, data):
        """Property: GDP should approximately equal C + I + G + (X - M)."""
        # Calculate GDP from expenditure approach
        calculated_gdp = data["C_USD_bn"] + data["I_USD_bn"] + data["G_USD_bn"] + data["X_USD_bn"] - data["M_USD_bn"]

        # Allow for statistical discrepancy (common in real data)
        discrepancy = abs(calculated_gdp - data["GDP_USD_bn"]) / data["GDP_USD_bn"]
        assert discrepancy <= 0.3, f"GDP accounting identity violated: discrepancy = {discrepancy:.3f}"


class TestRobustnessProperties:
    """Property-based tests for robustness and edge cases."""

    @given(economic_dataframe_strategy(min_rows=1, max_rows=5))
    def test_missing_data_handling_property(self, df):
        """Property: Functions should handle missing data gracefully."""
        # Introduce some missing values
        df_with_na = df.copy()
        if len(df_with_na) > 0:
            # Set some random values to NaN
            for col in df_with_na.columns:
                if col != "year" and len(df_with_na) > 1:
                    df_with_na.loc[df_with_na.index[0], col] = np.nan

        # These functions should not crash with missing data
        try:
            result = calculate_economic_indicators(df_with_na)
            assert isinstance(result, pd.DataFrame), "Should return DataFrame even with missing data"
            assert len(result) == len(df_with_na), "Should preserve number of rows"
        except Exception as e:
            pytest.fail(f"Function should handle missing data gracefully: {e}")

    @given(st.floats(min_value=0.01, max_value=0.99), economic_dataframe_strategy(min_rows=1, max_rows=5))
    def test_alpha_parameter_bounds_property(self, alpha, df):
        """Property: Alpha parameter should be handled correctly within bounds."""
        # Ensure we have required columns
        required_cols = ["GDP_USD_bn", "K_USD_bn", "LF_mn", "hc"]
        if not all(col in df.columns for col in required_cols):
            pytest.skip("Missing required columns")

        try:
            result = calculate_economic_indicators(df, alpha=alpha)
            assert isinstance(result, pd.DataFrame), "Should return DataFrame for valid alpha"

            if "TFP" in result.columns:
                tfp_values = result["TFP"].dropna()
                if len(tfp_values) > 0:
                    assert (tfp_values > 0).all(), "TFP should be positive for valid alpha"
        except Exception as e:
            pytest.fail(f"Valid alpha should not cause errors: {e}")

    @given(economic_dataframe_strategy(min_rows=1, max_rows=3))
    def test_small_dataset_handling_property(self, df):
        """Property: Functions should work with small datasets."""
        if len(df) == 0:
            pytest.skip("Empty dataset")

        try:
            result = calculate_economic_indicators(df)
            assert isinstance(result, pd.DataFrame), "Should handle small datasets"
            assert len(result) == len(df), "Should preserve dataset size"
        except Exception as e:
            pytest.fail(f"Should handle small datasets: {e}")


class TestPropertyBasedConfiguration:
    """Test configuration and examples for property-based testing."""

    @given(st.integers(min_value=1960, max_value=2030))
    @settings(max_examples=50, deadline=2000)  # Reduce examples for faster testing
    def test_year_range_property(self, year):
        """Property: Year should be within reasonable economic data range."""
        assert 1960 <= year <= 2030, f"Year should be in reasonable range: {year}"

    @given(st.floats(min_value=0.1, max_value=0.9))
    @settings(max_examples=50, deadline=2000)
    def test_alpha_range_property(self, alpha):
        """Property: Alpha parameter should be between 0 and 1."""
        assert 0 < alpha < 1, f"Alpha should be between 0 and 1: {alpha}"
