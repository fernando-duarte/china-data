"""Demonstration tests for pytest-factoryboy integration.

This module shows how the pytest-factoryboy integration provides automatic
fixtures from registered factories, following 2025 best practices.
"""

from typing import Any

import pytest

from utils.economic_indicators import calculate_economic_indicators


class TestFactoryBoyIntegration:
    """Tests demonstrating pytest-factoryboy automatic fixture generation."""

    def test_automatic_economic_data_fixture(self, economic_data: dict[str, Any]) -> None:
        """Test using the automatically generated economic_data fixture."""
        # The 'economic_data' fixture is automatically created from EconomicDataFactory
        assert isinstance(economic_data, dict)
        assert "year" in economic_data
        assert "GDP_USD_bn" in economic_data
        assert economic_data["GDP_USD_bn"] > 0

    def test_automatic_factory_fixture(self, economic_data_factory: Any) -> None:
        """Test using the automatically generated factory fixture."""
        # The 'economic_data_factory' fixture is automatically created
        data1 = economic_data_factory()
        data2 = economic_data_factory(GDP_USD_bn=1000.0)

        assert data1["GDP_USD_bn"] != data2["GDP_USD_bn"]
        assert data2["GDP_USD_bn"] == 1000.0

    def test_named_factory_fixtures(
        self, baseline_economic_data: dict[str, Any], alternative_economic_data: dict[str, Any]
    ) -> None:
        """Test using named factory fixtures for comparison scenarios."""
        # These fixtures are created from the registered named factories
        assert (
            baseline_economic_data["year"] != alternative_economic_data["year"]
            or baseline_economic_data["GDP_USD_bn"] != alternative_economic_data["GDP_USD_bn"]
        )

    def test_pwt_data_fixture(self, pwt_data: dict[str, Any]) -> None:
        """Test using the PWT data fixture."""
        assert isinstance(pwt_data, dict)
        assert "year" in pwt_data
        assert "rgdpo" in pwt_data
        assert pwt_data["rgdpo"] > 0

    def test_imf_tax_data_fixture(self, imf_tax_data: dict[str, Any]) -> None:
        """Test using the IMF tax data fixture."""
        assert isinstance(imf_tax_data, dict)
        assert "year" in imf_tax_data
        assert "TAX_pct_GDP" in imf_tax_data
        assert 0 <= imf_tax_data["TAX_pct_GDP"] <= 100

    def test_economic_indicators_fixture(self, economic_indicators: dict[str, Any]) -> None:
        """Test using the economic indicators fixture."""
        assert isinstance(economic_indicators, dict)
        assert "TFP" in economic_indicators
        assert economic_indicators["TFP"] > 0

    @pytest.mark.parametrize("economic_data__GDP_USD_bn", [1000.0, 5000.0, 10000.0])
    def test_parametrized_factory_attributes(
        self, economic_data: dict[str, Any], economic_data__gdp_usd_bn: float
    ) -> None:
        """Test parametrizing factory attributes using pytest-factoryboy syntax."""
        # The economic_data fixture will have the parametrized GDP values
        assert economic_data["GDP_USD_bn"] in [1000.0, 5000.0, 10000.0]
        assert economic_data["GDP_USD_bn"] == economic_data__gdp_usd_bn

    @pytest.mark.parametrize("economic_data__year", [2020, 2021, 2022])
    def test_parametrized_years(self, economic_data: dict[str, Any], economic_data__year: int) -> None:
        """Test parametrizing year values."""
        assert economic_data["year"] in [2020, 2021, 2022]
        assert economic_data["year"] == economic_data__year

    def test_factory_subfactory_relationships(self, economic_data_factory: Any) -> None:
        """Test creating related data using factories."""
        # Create base economic data
        base_data = economic_data_factory(year=2020, GDP_USD_bn=5000.0)

        # Create related data for the next year
        next_year_data = economic_data_factory(
            year=2021,
            GDP_USD_bn=base_data["GDP_USD_bn"] * 1.05,  # 5% growth
        )

        assert next_year_data["year"] == base_data["year"] + 1
        assert next_year_data["GDP_USD_bn"] > base_data["GDP_USD_bn"]


class TestFactoryBoyWithRealFunctions:
    """Tests showing factory integration with actual economic functions."""

    def test_economic_indicators_with_factory_data(self, economic_data_factory: Any) -> None:
        """Test economic indicators calculation with factory-generated data."""
        import pandas as pd

        # Create a small dataset using the factory
        data = [
            economic_data_factory(year=2020, GDP_USD_bn=5000.0),
            economic_data_factory(year=2021, GDP_USD_bn=5250.0),
            economic_data_factory(year=2022, GDP_USD_bn=5500.0),
        ]

        economic_dataframe = pd.DataFrame(data)
        result = calculate_economic_indicators(economic_dataframe)

        assert len(result) == 3
        assert "year" in result.columns

    @pytest.mark.parametrize("baseline_economic_data__GDP_USD_bn", [1000.0, 5000.0])
    @pytest.mark.parametrize("alternative_economic_data__GDP_USD_bn", [2000.0, 6000.0])
    def test_comparative_analysis(
        self, baseline_economic_data: dict[str, Any], alternative_economic_data: dict[str, Any]
    ) -> None:
        """Test comparative analysis using different factory configurations."""
        import pandas as pd

        # Create DataFrames from the factory data
        baseline_dataframe = pd.DataFrame([baseline_economic_data])
        alternative_dataframe = pd.DataFrame([alternative_economic_data])

        baseline_result = calculate_economic_indicators(baseline_dataframe)
        alternative_result = calculate_economic_indicators(alternative_dataframe)

        # Compare results
        if "T_USD_bn" in baseline_result.columns and "T_USD_bn" in alternative_result.columns:
            baseline_tax = baseline_result["T_USD_bn"].iloc[0]
            alternative_tax = alternative_result["T_USD_bn"].iloc[0]

            # Higher GDP should generally lead to higher tax revenue
            if alternative_economic_data["GDP_USD_bn"] > baseline_economic_data["GDP_USD_bn"]:
                assert alternative_tax >= baseline_tax


# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration
