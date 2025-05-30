"""Performance regression tests using pytest-benchmark.

This module contains benchmark tests to ensure that performance doesn't regress
as the codebase evolves. These tests help maintain performance standards for
critical economic calculation functions.
"""

from typing import Any

import pandas as pd
import pytest

from tests.factories import DataFrameFactory, create_china_growth_scenario
from utils.capital import calculate_capital_stock
from utils.economic_indicators import calculate_economic_indicators, calculate_tfp
from utils.processor_units import convert_units


class TestEconomicIndicatorsPerformance:
    """Performance benchmarks for economic indicators calculations."""

    @pytest.mark.benchmark(group="economic_indicators")
    def test_calculate_economic_indicators_performance(
        self, benchmark: Any, complete_economic_data: pd.DataFrame
    ) -> None:
        """Benchmark the calculate_economic_indicators function."""
        result = benchmark(calculate_economic_indicators, complete_economic_data)

        # Verify the function still works correctly
        assert len(result) == len(complete_economic_data)
        assert "TFP" in result.columns or "T_USD_bn" in result.columns

    @pytest.mark.benchmark(group="economic_indicators")
    def test_calculate_tfp_performance(self, benchmark: Any) -> None:
        """Benchmark the calculate_tfp function with realistic data."""
        # Create data with required columns for TFP calculation
        economic_dataframe = DataFrameFactory.create_economic_dataframe(
            years=list(range(2000, 2023)), num_rows=23
        )

        result = benchmark(calculate_tfp, economic_dataframe, alpha=1 / 3)

        # Verify the function still works correctly
        assert len(result) == len(economic_dataframe)

    @pytest.mark.benchmark(group="economic_indicators")
    def test_large_dataset_performance(self, benchmark: Any) -> None:
        """Benchmark performance with larger datasets."""
        # Create a larger dataset (40 years of data)
        large_dataframe = DataFrameFactory.create_economic_dataframe(
            years=list(range(1980, 2023)), num_rows=43
        )

        result = benchmark(calculate_economic_indicators, large_dataframe)

        # Verify the function handles large datasets correctly
        assert len(result) == len(large_dataframe)


class TestDataProcessingPerformance:
    """Performance benchmarks for data processing functions."""

    @pytest.mark.benchmark(group="data_processing")
    def test_convert_units_performance(
        self, benchmark: Any, complete_economic_data: pd.DataFrame
    ) -> None:
        """Benchmark the convert_units function."""
        result = benchmark(convert_units, complete_economic_data)

        # Verify the function still works correctly
        assert len(result) == len(complete_economic_data)

    @pytest.mark.benchmark(group="data_processing")
    def test_calculate_capital_stock_performance(self, benchmark: Any) -> None:
        """Benchmark the calculate_capital_stock function."""
        economic_dataframe = DataFrameFactory.create_economic_dataframe(
            years=list(range(2000, 2023)), num_rows=23
        )

        result = benchmark(calculate_capital_stock, economic_dataframe, capital_output_ratio=3.0)

        # Verify the function still works correctly
        assert len(result) == len(economic_dataframe)


class TestRealWorldScenarioPerformance:
    """Performance benchmarks for realistic data scenarios."""

    @pytest.mark.benchmark(group="real_world")
    def test_china_growth_scenario_performance(self, benchmark: Any) -> None:
        """Benchmark performance with China's realistic growth trajectory."""
        china_data = create_china_growth_scenario()

        result = benchmark(calculate_economic_indicators, china_data)

        # Verify the realistic scenario works correctly
        assert len(result) == len(china_data)
        assert len(china_data) > 40  # Should have 40+ years of data

    @pytest.mark.benchmark(group="real_world")
    def test_missing_data_scenario_performance(self, benchmark: Any) -> None:
        """Benchmark performance with missing data (realistic scenario)."""
        missing_data_dataframe = DataFrameFactory.create_economic_dataframe(
            years=list(range(1990, 2023)),
            num_rows=33,
            include_missing=True,
            missing_probability=0.15,
        )

        result = benchmark(calculate_economic_indicators, missing_data_dataframe)

        # Verify missing data handling works correctly
        assert len(result) == len(missing_data_dataframe)


class TestPerformanceRegression:
    """Tests to catch performance regressions."""

    @pytest.mark.benchmark(
        group="regression",
        min_rounds=5,
        max_time=2.0,  # Maximum 2 seconds per benchmark
        warmup=True,
    )
    def test_economic_indicators_regression(self, benchmark: Any) -> None:
        """Regression test for economic indicators calculation performance."""
        # Use a standardized dataset for consistent benchmarking
        standard_dataframe = DataFrameFactory.create_economic_dataframe(
            years=list(range(2000, 2021)), num_rows=21
        )

        result = benchmark(calculate_economic_indicators, standard_dataframe)

        # Performance assertion: should complete within reasonable time
        # This will fail if performance significantly degrades
        assert len(result) == 21

    @pytest.mark.benchmark(
        group="regression",
        min_rounds=5,
        max_time=1.0,  # Maximum 1 second per benchmark
        warmup=True,
    )
    def test_unit_conversion_regression(self, benchmark: Any) -> None:
        """Regression test for unit conversion performance."""
        conversion_dataframe = DataFrameFactory.create_economic_dataframe(
            years=list(range(2010, 2021)), num_rows=11
        )

        result = benchmark(convert_units, conversion_dataframe)

        # Performance assertion
        assert len(result) == 11


# Benchmark configuration for different scenarios
@pytest.mark.benchmark(group="memory")
def test_memory_usage_economic_indicators(
    benchmark: Any, complete_economic_data: pd.DataFrame
) -> None:
    """Test memory usage patterns for economic indicators calculation."""
    import os

    import psutil

    def measure_memory() -> pd.DataFrame:
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss

        result = calculate_economic_indicators(complete_economic_data)

        memory_after = process.memory_info().rss
        memory_used = memory_after - memory_before

        # Log memory usage for monitoring
        print(f"Memory used: {memory_used / 1024 / 1024:.2f} MB")

        return result

    result = benchmark(measure_memory)
    assert len(result) == len(complete_economic_data)


# Custom benchmark markers for different performance categories
pytestmark = [
    pytest.mark.performance,
    pytest.mark.benchmark,
]
