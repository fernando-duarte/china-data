"""Demonstration tests showing how to use the test data factories.

This module provides examples of how to use the factory_boy factories
for creating realistic test data in various testing scenarios.
"""

import numpy as np
import pandas as pd

from tests.factories import (
    DataFrameFactory,
    EconomicDataFactory,
    IMFTaxDataFactory,
    PWTDataFactory,
    TimeSeriesFactory,
    create_china_growth_scenario,
    create_complete_economic_data,
    create_data_with_missing_values,
    create_minimal_economic_data,
)
from utils.economic_indicators import calculate_economic_indicators
from utils.processor_units import convert_units


class TestFactoryBasics:
    """Basic tests demonstrating factory usage."""

    def test_economic_data_factory_single_row(self):
        """Test creating a single economic data row."""
        data = EconomicDataFactory.build()

        # Check that all expected fields are present
        expected_fields = [
            "year",
            "GDP_USD_bn",
            "C_USD_bn",
            "G_USD_bn",
            "I_USD_bn",
            "X_USD_bn",
            "M_USD_bn",
            "K_USD_bn",
            "LF_mn",
            "hc",
            "TAX_pct_GDP",
        ]

        for field in expected_fields:
            assert field in data, f"Missing field: {field}"
            assert data[field] is not None, f"Field {field} should not be None"

        # Check realistic ranges
        assert 1960 <= data["year"] <= 2030
        assert 50.0 <= data["GDP_USD_bn"] <= 20000.0
        assert data["C_USD_bn"] > 0
        assert data["G_USD_bn"] > 0
        assert data["TAX_pct_GDP"] >= 0

    def test_pwt_data_factory(self):
        """Test creating Penn World Table data."""
        data = PWTDataFactory.build()

        expected_fields = ["year", "rgdpo", "rkna", "pl_gdpo", "cgdpo", "hc"]

        for field in expected_fields:
            assert field in data, f"Missing PWT field: {field}"

        # Check PWT-specific constraints
        assert 1950 <= data["year"] <= 2019  # PWT coverage
        assert data["rgdpo"] > 0
        assert data["rkna"] > 0
        assert data["hc"] >= 1.0

    def test_imf_tax_data_factory(self):
        """Test creating IMF tax data."""
        data = IMFTaxDataFactory.build()

        assert "year" in data
        assert "TAX_pct_GDP" in data
        assert 1990 <= data["year"] <= 2030
        assert 8.0 <= data["TAX_pct_GDP"] <= 30.0


class TestDataFrameFactories:
    """Tests demonstrating DataFrame factory usage."""

    def test_create_economic_dataframe_default(self):
        """Test creating economic DataFrame with default parameters."""
        df = DataFrameFactory.create_economic_dataframe()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 10  # Default num_rows
        assert "year" in df.columns
        assert "GDP_USD_bn" in df.columns

        # Years should be unique and sorted
        assert df["year"].is_unique
        assert df["year"].is_monotonic_increasing

    def test_create_economic_dataframe_specific_years(self):
        """Test creating DataFrame for specific years."""
        years = [2020, 2021, 2022]
        df = DataFrameFactory.create_economic_dataframe(years=years)

        assert len(df) == 3
        assert df["year"].tolist() == years

        # Check that all economic variables are present
        economic_cols = ["GDP_USD_bn", "C_USD_bn", "G_USD_bn", "I_USD_bn"]
        for col in economic_cols:
            assert col in df.columns
            assert (df[col] > 0).all()

    def test_create_dataframe_with_missing_values(self):
        """Test creating DataFrame with missing values."""
        df = DataFrameFactory.create_economic_dataframe(
            years=[2020, 2021, 2022], include_missing=True, missing_probability=0.3
        )

        assert len(df) == 3

        # Should have some missing values (but not in year column)
        total_missing = df.drop("year", axis=1).isna().sum().sum()
        assert total_missing > 0, "Should have some missing values"

        # Year column should never be missing
        assert not df["year"].isna().any()

    def test_create_complete_dataset(self):
        """Test creating complete dataset with all sources."""
        dataset = DataFrameFactory.create_complete_dataset(
            start_year=2000, end_year=2005, include_pwt=True, include_imf=True
        )

        assert "economic" in dataset
        assert "pwt" in dataset
        assert "imf" in dataset

        # Check economic data
        econ_df = dataset["economic"]
        assert len(econ_df) == 6  # 2000-2005
        assert econ_df["year"].min() == 2000
        assert econ_df["year"].max() == 2005

        # Check PWT data
        pwt_df = dataset["pwt"]
        assert len(pwt_df) == 6  # All years should be <= 2019
        assert "rgdpo" in pwt_df.columns

        # Check IMF data
        imf_df = dataset["imf"]
        assert len(imf_df) == 6
        assert "TAX_pct_GDP" in imf_df.columns


class TestConvenienceFunctions:
    """Tests for convenience factory functions."""

    def test_create_minimal_economic_data(self):
        """Test minimal economic data creation."""
        df = create_minimal_economic_data()

        assert len(df) == 3  # Default years: 2020, 2021, 2022
        assert df["year"].tolist() == [2020, 2021, 2022]

        # Should have basic economic columns
        basic_cols = ["GDP_USD_bn", "C_USD_bn", "G_USD_bn"]
        for col in basic_cols:
            assert col in df.columns

    def test_create_complete_economic_data(self):
        """Test complete economic data creation."""
        df = create_complete_economic_data()

        assert len(df) == 23  # 2000-2022
        assert df["year"].min() == 2000
        assert df["year"].max() == 2022

        # Should have all economic columns
        all_cols = ["GDP_USD_bn", "C_USD_bn", "G_USD_bn", "I_USD_bn", "X_USD_bn", "M_USD_bn", "K_USD_bn", "LF_mn", "hc"]
        for col in all_cols:
            assert col in df.columns

    def test_create_data_with_missing_values(self):
        """Test data creation with missing values."""
        df = create_data_with_missing_values(years=[2000, 2001, 2002], missing_probability=0.5)

        assert len(df) == 3

        # Should have substantial missing data
        missing_count = df.drop("year", axis=1).isna().sum().sum()
        total_cells = len(df) * (len(df.columns) - 1)  # Exclude year column
        missing_rate = missing_count / total_cells

        # Should have some missing data (allowing for randomness)
        assert missing_rate > 0.1, f"Missing rate too low: {missing_rate}"

    def test_create_china_growth_scenario(self):
        """Test China growth scenario creation."""
        df = create_china_growth_scenario()

        assert len(df) == 43  # 1980-2022
        assert df["year"].min() == 1980
        assert df["year"].max() == 2022

        # GDP should show growth over time
        gdp_correlation = df["year"].corr(df["GDP_USD_bn"])
        assert gdp_correlation > 0.9, "GDP should be strongly correlated with time"

        # Check realistic economic structure
        # Consumption ratio should increase over time
        df["consumption_ratio"] = df["C_USD_bn"] / df["GDP_USD_bn"]
        consumption_trend = df["year"].corr(df["consumption_ratio"])
        assert consumption_trend > 0, "Consumption ratio should increase over time"


class TestTimeSeriesFactory:
    """Tests for time series factory functionality."""

    def test_create_linear_trending_series(self):
        """Test linear trending time series."""
        years = [2000, 2001, 2002, 2003, 2004]
        series = TimeSeriesFactory.create_trending_series(
            start_value=100.0,
            end_value=200.0,
            years=years,
            trend_type="linear",
            volatility=0.01,  # Low volatility
        )

        assert len(series) == 5
        assert series.index.tolist() == years

        # Should be roughly linear
        correlation = np.corrcoef(years, series.values)[0, 1]
        assert correlation > 0.95, f"Linear series should have high correlation: {correlation}"

        # Values should be positive
        assert (series > 0).all()

    def test_create_exponential_trending_series(self):
        """Test exponential trending time series."""
        years = list(range(2000, 2020))
        series = TimeSeriesFactory.create_trending_series(
            start_value=100.0, end_value=1000.0, years=years, trend_type="exponential", volatility=0.02
        )

        assert len(series) == 20

        # Should show exponential growth pattern
        # Later values should be much larger than earlier ones
        early_avg = series[:5].mean()
        late_avg = series[-5:].mean()
        assert late_avg > 5 * early_avg, "Exponential series should show strong growth"

    def test_create_logarithmic_trending_series(self):
        """Test logarithmic trending time series."""
        years = list(range(2000, 2010))
        series = TimeSeriesFactory.create_trending_series(
            start_value=100.0, end_value=200.0, years=years, trend_type="logarithmic", volatility=0.01
        )

        assert len(series) == 10

        # Should show slowing growth (logarithmic pattern)
        # Growth rate should decrease over time
        growth_rates = series.pct_change().dropna()
        # Later growth rates should generally be smaller
        early_growth = growth_rates[:3].mean()
        late_growth = growth_rates[-3:].mean()
        assert late_growth < early_growth, "Logarithmic series should show slowing growth"


class TestFactoryIntegration:
    """Tests showing integration with actual processing functions."""

    def test_factory_data_with_economic_indicators(self):
        """Test using factory data with economic indicators calculation."""
        df = create_complete_economic_data(years=[2020, 2021, 2022])

        # Should work with economic indicators calculation
        result = calculate_economic_indicators(df)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3

        # Should have calculated indicators
        expected_indicators = ["NX_USD_bn", "TFP", "T_USD_bn", "Openness_Ratio"]
        for indicator in expected_indicators:
            assert indicator in result.columns

    def test_factory_data_with_unit_conversion(self):
        """Test using factory data with unit conversion."""
        # Create data with original units (not billions)
        df = create_minimal_economic_data()

        # Convert to original units for testing
        df["GDP_USD"] = df["GDP_USD_bn"] * 1e9  # Convert back to USD
        df["C_USD"] = df["C_USD_bn"] * 1e9
        df = df.drop(["GDP_USD_bn", "C_USD_bn"], axis=1)

        # Should work with unit conversion
        result = convert_units(df)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3

        # Should have converted units
        if "GDP_USD_bn" in result.columns:
            assert (result["GDP_USD_bn"] > 0).all()

    def test_factory_data_stress_test(self):
        """Stress test with large dataset from factories."""
        # Create a large dataset
        years = list(range(1980, 2023))  # 43 years
        df = DataFrameFactory.create_economic_dataframe(years=years, include_missing=True, missing_probability=0.1)

        assert len(df) == 43

        # Should handle large dataset
        result = calculate_economic_indicators(df)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 43

        # Should have reasonable number of calculated values
        # (some may be missing due to missing input data)
        for col in ["NX_USD_bn", "T_USD_bn", "Openness_Ratio"]:
            if col in result.columns:
                non_missing = result[col].notna().sum()
                assert non_missing > 0, f"Should have some calculated values for {col}"


class TestFactoryRealism:
    """Tests verifying that factory data is realistic."""

    def test_economic_ratios_realistic(self):
        """Test that economic ratios are realistic."""
        df = create_complete_economic_data(years=list(range(2000, 2020)))

        # Calculate ratios
        df["consumption_ratio"] = df["C_USD_bn"] / df["GDP_USD_bn"]
        df["investment_ratio"] = df["I_USD_bn"] / df["GDP_USD_bn"]
        df["government_ratio"] = df["G_USD_bn"] / df["GDP_USD_bn"]
        df["export_ratio"] = df["X_USD_bn"] / df["GDP_USD_bn"]

        # Check realistic ranges for China
        assert (df["consumption_ratio"] >= 0.3).all() and (df["consumption_ratio"] <= 0.7).all()
        assert (df["investment_ratio"] >= 0.1).all() and (df["investment_ratio"] <= 0.6).all()
        assert (df["government_ratio"] >= 0.05).all() and (df["government_ratio"] <= 0.3).all()
        assert (df["export_ratio"] >= 0.05).all() and (df["export_ratio"] <= 0.4).all()

    def test_china_scenario_realism(self):
        """Test that China growth scenario is realistic."""
        df = create_china_growth_scenario()

        # Check GDP growth pattern
        df["gdp_growth"] = df["GDP_USD_bn"].pct_change()

        # Should have positive growth most years
        positive_growth_years = (df["gdp_growth"] > 0).sum()
        total_growth_years = df["gdp_growth"].notna().sum()
        positive_ratio = positive_growth_years / total_growth_years

        assert positive_ratio > 0.8, f"Should have mostly positive growth: {positive_ratio}"

        # Growth should be reasonable (not too extreme)
        growth_rates = df["gdp_growth"].dropna()
        assert (growth_rates < 0.5).all(), "Growth rates should be reasonable"
        assert (growth_rates > -0.3).all(), "Negative growth should not be too extreme"

    def test_factory_data_consistency(self):
        """Test that factory data is internally consistent."""
        df = create_complete_economic_data(years=[2020])
        row = df.iloc[0]

        # Basic accounting identity (allowing for statistical discrepancy)
        calculated_gdp = row["C_USD_bn"] + row["I_USD_bn"] + row["G_USD_bn"] + row["X_USD_bn"] - row["M_USD_bn"]

        discrepancy = abs(calculated_gdp - row["GDP_USD_bn"]) / row["GDP_USD_bn"]
        assert discrepancy <= 0.3, f"GDP accounting identity violated: {discrepancy:.3f}"

        # Capital stock should be reasonable multiple of GDP
        capital_ratio = row["K_USD_bn"] / row["GDP_USD_bn"]
        assert 2.0 <= capital_ratio <= 5.0, f"Capital ratio unrealistic: {capital_ratio}"
