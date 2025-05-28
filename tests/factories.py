"""Test data factories for generating realistic economic data.

This module provides factory_boy factories for creating test data that matches
the structure and constraints of real economic data used in the China data pipeline.
"""

import random
from typing import Any

import factory
import numpy as np
import pandas as pd
from factory import fuzzy


class EconomicDataFactory(factory.Factory):  # type: ignore[misc]
    """Factory for generating economic data rows."""

    class Meta:
        model = dict

    # Year should be realistic (1960-2030)
    year = fuzzy.FuzzyInteger(1960, 2030)

    # GDP in USD billions (realistic range for China: 50-20000)
    GDP_USD_bn = fuzzy.FuzzyFloat(50.0, 20000.0)

    # Consumption as percentage of GDP (typically 35-65% for China)
    @factory.LazyAttribute  # type: ignore[misc]
    def C_USD_bn(obj: Any) -> Any:
        consumption_ratio = random.uniform(0.35, 0.65)
        return round(obj.GDP_USD_bn * consumption_ratio, 2)

    # Government spending as percentage of GDP (typically 10-25%)
    @factory.LazyAttribute  # type: ignore[misc]
    def G_USD_bn(obj: Any) -> Any:
        gov_ratio = random.uniform(0.10, 0.25)
        return round(obj.GDP_USD_bn * gov_ratio, 2)

    # Investment as percentage of GDP (typically 20-50% for China)
    @factory.LazyAttribute  # type: ignore[misc]
    def I_USD_bn(obj: Any) -> Any:
        investment_ratio = random.uniform(0.20, 0.50)
        return round(obj.GDP_USD_bn * investment_ratio, 2)

    # Exports as percentage of GDP (typically 10-35% for China)
    @factory.LazyAttribute  # type: ignore[misc]
    def X_USD_bn(obj: Any) -> Any:
        export_ratio = random.uniform(0.10, 0.35)
        return round(obj.GDP_USD_bn * export_ratio, 2)

    # Imports as percentage of GDP (typically 8-30% for China)
    @factory.LazyAttribute  # type: ignore[misc]
    def M_USD_bn(obj: Any) -> Any:
        import_ratio = random.uniform(0.08, 0.30)
        return round(obj.GDP_USD_bn * import_ratio, 2)

    # Capital stock (typically 2-4 times GDP)
    @factory.LazyAttribute  # type: ignore[misc]
    def K_USD_bn(obj: Any) -> Any:
        capital_ratio = random.uniform(2.0, 4.0)
        return round(obj.GDP_USD_bn * capital_ratio, 2)

    # Labor force in millions (realistic range for China: 400-800)
    LF_mn = fuzzy.FuzzyFloat(400.0, 800.0)

    # Human capital index (typically 1.5-3.5)
    hc = fuzzy.FuzzyFloat(1.5, 3.5)

    # Tax revenue as percentage of GDP (typically 10-25%)
    TAX_pct_GDP = fuzzy.FuzzyFloat(10.0, 25.0)

    # Population in millions (realistic range for China: 600-1500)
    Population_mn = fuzzy.FuzzyFloat(600.0, 1500.0)

    # FDI as percentage of GDP (typically 0-6%)
    FDI_pct_GDP = fuzzy.FuzzyFloat(0.0, 6.0)


class PWTDataFactory(factory.Factory):  # type: ignore[misc]
    """Factory for Penn World Table data."""

    class Meta:
        model = dict

    year = fuzzy.FuzzyInteger(1950, 2019)  # PWT coverage

    # Real GDP at constant 2017 national prices (millions 2017 USD)
    rgdpo = fuzzy.FuzzyFloat(100000.0, 25000000.0)

    # Capital stock at constant 2017 national prices (millions 2017 USD)
    rkna = fuzzy.FuzzyFloat(200000.0, 100000000.0)

    # Price level of GDP (USA=1)
    pl_gdpo = fuzzy.FuzzyFloat(0.1, 2.0)

    # Real GDP at current PPPs (millions 2017 USD)
    cgdpo = fuzzy.FuzzyFloat(100000.0, 30000000.0)

    # Human capital index
    hc = fuzzy.FuzzyFloat(1.0, 4.0)


class IMFTaxDataFactory(factory.Factory):  # type: ignore[misc]
    """Factory for IMF tax revenue data."""

    class Meta:
        model = dict

    year = fuzzy.FuzzyInteger(1990, 2030)
    TAX_pct_GDP = fuzzy.FuzzyFloat(8.0, 30.0)


class EconomicIndicatorsFactory(factory.Factory):  # type: ignore[misc]
    """Factory for calculated economic indicators."""

    class Meta:
        model = dict

    year = fuzzy.FuzzyInteger(1960, 2030)

    # Total Factor Productivity (positive values)
    TFP = fuzzy.FuzzyFloat(0.5, 3.0)

    # Tax revenue in USD billions
    T_USD_bn = fuzzy.FuzzyFloat(50.0, 3000.0)

    # Trade openness ratio
    Openness_Ratio = fuzzy.FuzzyFloat(0.1, 0.8)

    # Net exports in USD billions (can be negative)
    NX_USD_bn = fuzzy.FuzzyFloat(-500.0, 1000.0)

    # Total saving in USD billions
    S_USD_bn = fuzzy.FuzzyFloat(100.0, 8000.0)

    # Private saving in USD billions
    S_priv_USD_bn = fuzzy.FuzzyFloat(50.0, 6000.0)

    # Public saving in USD billions (can be negative)
    S_pub_USD_bn = fuzzy.FuzzyFloat(-1000.0, 2000.0)

    # Saving rate (0-1)
    Saving_Rate = fuzzy.FuzzyFloat(0.1, 0.6)


class DataFrameFactory:
    """Factory for creating pandas DataFrames with economic data."""

    @staticmethod
    def create_economic_dataframe(
        years: list[int] | None = None,
        num_rows: int = 10,
        include_missing: bool = False,
        missing_probability: float = 0.1,
    ) -> pd.DataFrame:
        """Create a DataFrame with economic data.

        Args:
            years: Specific years to include. If None, generates random years.
            num_rows: Number of rows to generate if years not specified.
            include_missing: Whether to include missing values.
            missing_probability: Probability of missing values (if include_missing=True).

        Returns:
            pandas.DataFrame with economic data.
        """
        if years is None:
            years = sorted(random.sample(range(1960, 2031), num_rows))

        data = []
        for year in years:
            row_data = EconomicDataFactory.build()
            row_data["year"] = year
            data.append(row_data)

        df = pd.DataFrame(data)

        if include_missing:
            # Randomly set some values to NaN
            for col in df.columns:
                if col != "year":  # Don't make year missing
                    mask = np.random.random(len(df)) < missing_probability
                    df.loc[mask, col] = np.nan

        return df

    @staticmethod
    def create_pwt_dataframe(years: list[int] | None = None, num_rows: int = 10) -> pd.DataFrame:
        """Create a DataFrame with Penn World Table data."""
        if years is None:
            years = sorted(random.sample(range(1950, 2020), num_rows))

        data = []
        for year in years:
            row_data = PWTDataFactory.build()
            row_data["year"] = year
            data.append(row_data)

        return pd.DataFrame(data)

    @staticmethod
    def create_imf_tax_dataframe(years: list[int] | None = None, num_rows: int = 10) -> pd.DataFrame:
        """Create a DataFrame with IMF tax data."""
        if years is None:
            years = sorted(random.sample(range(1990, 2031), num_rows))

        data = []
        for year in years:
            row_data = IMFTaxDataFactory.build()
            row_data["year"] = year
            data.append(row_data)

        return pd.DataFrame(data)

    @staticmethod
    def create_complete_dataset(
        start_year: int = 2000, end_year: int = 2022, include_pwt: bool = True, include_imf: bool = True
    ) -> dict[str, pd.DataFrame]:
        """Create a complete dataset with all data sources.

        Args:
            start_year: Starting year for the dataset.
            end_year: Ending year for the dataset.
            include_pwt: Whether to include PWT data.
            include_imf: Whether to include IMF data.

        Returns:
            Dictionary with 'economic', 'pwt', and 'imf' DataFrames.
        """
        years = list(range(start_year, end_year + 1))

        result = {"economic": DataFrameFactory.create_economic_dataframe(years=years)}

        if include_pwt:
            # PWT data typically ends around 2019
            pwt_years = [y for y in years if y <= 2019]
            if pwt_years:
                result["pwt"] = DataFrameFactory.create_pwt_dataframe(years=pwt_years)

        if include_imf:
            result["imf"] = DataFrameFactory.create_imf_tax_dataframe(years=years)

        return result


class TimeSeriesFactory:
    """Factory for creating realistic time series data."""

    @staticmethod
    def create_trending_series(
        start_value: float, end_value: float, years: list[int], volatility: float = 0.05, trend_type: str = "linear"
    ) -> pd.Series:
        """Create a trending time series with realistic volatility.

        Args:
            start_value: Starting value of the series.
            end_value: Ending value of the series.
            years: List of years for the series.
            volatility: Standard deviation of random noise (as fraction of value).
            trend_type: Type of trend ('linear', 'exponential', 'logarithmic').

        Returns:
            pandas.Series with trending data.
        """
        n = len(years)

        if trend_type == "linear":
            trend = np.linspace(start_value, end_value, n)
        elif trend_type == "exponential":
            growth_rate = (end_value / start_value) ** (1 / (n - 1)) - 1
            trend = start_value * (1 + growth_rate) ** np.arange(n)
        elif trend_type == "logarithmic":
            # Logarithmic growth slows down over time
            x = np.linspace(0, 1, n)
            trend = start_value + (end_value - start_value) * np.log(1 + x) / np.log(2)
        else:
            raise ValueError(f"Unknown trend_type: {trend_type}")

        # Add realistic volatility
        noise = np.random.normal(0, volatility, n)
        values = trend * (1 + noise)

        # Ensure positive values for economic data
        values = np.maximum(values, 0.01)

        return pd.Series(values, index=years, name="value")


# Convenience functions for common test scenarios
def create_minimal_economic_data(years: list[int] | None = None) -> pd.DataFrame:
    """Create minimal economic data for basic tests."""
    if years is None:
        years = [2020, 2021, 2022]

    return DataFrameFactory.create_economic_dataframe(years=years)


def create_complete_economic_data(years: list[int] | None = None) -> pd.DataFrame:
    """Create complete economic data with all required columns."""
    if years is None:
        years = list(range(2000, 2023))

    return DataFrameFactory.create_economic_dataframe(years=years)


def create_data_with_missing_values(years: list[int] | None = None, missing_probability: float = 0.2) -> pd.DataFrame:
    """Create economic data with realistic missing values."""
    if years is None:
        years = list(range(1980, 2023))

    return DataFrameFactory.create_economic_dataframe(
        years=years, include_missing=True, missing_probability=missing_probability
    )


def create_china_growth_scenario() -> pd.DataFrame:
    """Create data representing China's economic growth trajectory."""
    years = list(range(1980, 2023))

    # Create realistic growth trajectory
    gdp_series = TimeSeriesFactory.create_trending_series(
        start_value=200.0,  # 1980 GDP
        end_value=17000.0,  # 2022 GDP
        years=years,
        trend_type="exponential",
        volatility=0.03,
    )

    data = []
    for i, year in enumerate(years):
        gdp = gdp_series.iloc[i]

        # Create realistic ratios based on China's development
        consumption_ratio = 0.35 + 0.15 * (year - 1980) / (2022 - 1980)  # Rising consumption
        investment_ratio = 0.45 - 0.10 * (year - 1980) / (2022 - 1980)  # Declining investment

        row = {
            "year": year,
            "GDP_USD_bn": gdp,
            "C_USD_bn": gdp * consumption_ratio,
            "I_USD_bn": gdp * investment_ratio,
            "G_USD_bn": gdp * 0.15,  # Stable government spending
            "X_USD_bn": gdp * (0.05 + 0.25 * (year - 1980) / (2022 - 1980)),  # Rising exports
            "M_USD_bn": gdp * (0.04 + 0.20 * (year - 1980) / (2022 - 1980)),  # Rising imports
            "K_USD_bn": gdp * (2.5 + 1.0 * (year - 1980) / (2022 - 1980)),  # Rising capital intensity
            "LF_mn": 400 + 350 * (year - 1980) / (2022 - 1980),  # Growing labor force
            "hc": 1.5 + 1.5 * (year - 1980) / (2022 - 1980),  # Improving human capital
            "TAX_pct_GDP": 12 + 8 * (year - 1980) / (2022 - 1980),  # Rising tax capacity
        }
        data.append(row)

    return pd.DataFrame(data)
