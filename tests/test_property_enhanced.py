"""
Enhanced property-based testing for data processing pipeline.

This module demonstrates advanced property-based testing using Hypothesis,
including stateful testing for complex data processing scenarios.
"""

import numpy as np
import pandas as pd
from hypothesis import assume, given, settings
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, initialize, invariant, rule


# Strategies for generating test data
@st.composite
def economic_data_strategy(draw):
    """Generate realistic economic data for testing."""
    years = draw(st.lists(st.integers(min_value=1990, max_value=2030), min_size=3, max_size=10, unique=True))
    years.sort()

    return {
        "years": years,
        "gdp_values": draw(
            st.lists(
                st.floats(min_value=1e10, max_value=1e15, allow_nan=False, allow_infinity=False),
                min_size=len(years),
                max_size=len(years),
            )
        ),
        "population": draw(
            st.lists(st.integers(min_value=1e6, max_value=2e9), min_size=len(years), max_size=len(years))
        ),
        "inflation_rates": draw(
            st.lists(
                st.floats(min_value=-5.0, max_value=20.0, allow_nan=False, allow_infinity=False),
                min_size=len(years),
                max_size=len(years),
            )
        ),
    }


@st.composite
def dataframe_strategy(draw):
    """Generate pandas DataFrames with economic data."""
    data = draw(economic_data_strategy())

    return pd.DataFrame(
        {
            "year": data["years"],
            "gdp_usd": data["gdp_values"],
            "population": data["population"],
            "inflation_rate": data["inflation_rates"],
        }
    )


class TestDataProcessingProperties:
    """Property-based tests for data processing functions."""

    @given(economic_data_strategy())
    @settings(max_examples=50, deadline=1000)
    def test_gdp_per_capita_calculation_properties(self, data):
        """Test properties of GDP per capita calculation."""
        assume(all(pop > 0 for pop in data["population"]))
        assume(all(gdp > 0 for gdp in data["gdp_values"]))

        # Calculate GDP per capita
        gdp_per_capita = [gdp / pop for gdp, pop in zip(data["gdp_values"], data["population"], strict=False)]

        # Properties that should always hold
        assert all(gpc > 0 for gpc in gdp_per_capita), "GDP per capita should be positive"
        assert len(gdp_per_capita) == len(data["years"]), "Output length should match input"

        # GDP per capita should be proportional to GDP
        for i in range(len(gdp_per_capita)):
            expected = data["gdp_values"][i] / data["population"][i]
            assert abs(gdp_per_capita[i] - expected) < 1e-6, "Calculation should be accurate"

    @given(dataframe_strategy())
    @settings(max_examples=30, deadline=1000)
    def test_dataframe_processing_properties(self, df):
        """Test properties of DataFrame processing operations."""
        assume(len(df) > 0)
        assume(df["population"].min() > 0)
        assume(df["gdp_usd"].min() > 0)

        # Add calculated columns
        df_processed = df.copy()
        df_processed["gdp_per_capita"] = df_processed["gdp_usd"] / df_processed["population"]
        df_processed["gdp_growth"] = df_processed["gdp_usd"].pct_change() * 100

        # Properties
        assert len(df_processed) == len(df), "Processing should preserve row count"
        assert "gdp_per_capita" in df_processed.columns, "Should add GDP per capita column"
        assert "gdp_growth" in df_processed.columns, "Should add GDP growth column"

        # GDP per capita should be positive
        assert (df_processed["gdp_per_capita"] > 0).all(), "GDP per capita should be positive"

        # First GDP growth value should be NaN (no previous year)
        assert pd.isna(df_processed["gdp_growth"].iloc[0]), "First growth value should be NaN"

    @given(st.lists(st.floats(min_value=0, max_value=1e15, allow_nan=False), min_size=1, max_size=100))
    @settings(max_examples=50)
    def test_data_normalization_properties(self, values):
        """Test properties of data normalization."""
        assume(len(values) > 1)
        assume(max(values) > min(values))  # Avoid division by zero

        # Min-max normalization
        min_val, max_val = min(values), max(values)
        normalized = [(v - min_val) / (max_val - min_val) for v in values]

        # Properties
        assert all(0 <= n <= 1 for n in normalized), "Normalized values should be in [0, 1]"
        assert min(normalized) == 0, "Minimum should be 0"
        assert max(normalized) == 1, "Maximum should be 1"
        assert len(normalized) == len(values), "Length should be preserved"

    @given(st.lists(st.floats(min_value=-100, max_value=100, allow_nan=False), min_size=3, max_size=50))
    @settings(max_examples=30)
    def test_moving_average_properties(self, values):
        """Test properties of moving average calculation."""
        window_size = 3
        assume(len(values) >= window_size)

        # Calculate moving average
        moving_avg = []
        for i in range(len(values) - window_size + 1):
            window = values[i : i + window_size]
            moving_avg.append(sum(window) / len(window))

        # Properties
        assert len(moving_avg) == len(values) - window_size + 1, "Correct output length"

        # Each moving average should be within the range of its window
        for i, avg in enumerate(moving_avg):
            window = values[i : i + window_size]
            assert min(window) <= avg <= max(window), "Average should be within window range"


class DataProcessingStateMachine(RuleBasedStateMachine):
    """Stateful testing for data processing pipeline."""

    def __init__(self):
        super().__init__()
        self.data_store: dict[str, pd.DataFrame] = {}
        self.processing_history: list[str] = []

    @initialize()
    def setup_initial_data(self):
        """Initialize with some basic data."""
        initial_data = pd.DataFrame(
            {
                "year": [2020, 2021, 2022],
                "gdp_usd": [14.34e12, 17.73e12, 17.95e12],
                "population": [1.411e9, 1.412e9, 1.413e9],
            }
        )
        self.data_store["base"] = initial_data
        self.processing_history.append("initialize")

    @rule(
        dataset_name=st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=("Lu", "Ll"))),
        data=dataframe_strategy(),
    )
    def add_dataset(self, dataset_name, data):
        """Add a new dataset to the data store."""
        assume(dataset_name not in self.data_store)
        assume(len(data) > 0)

        self.data_store[dataset_name] = data
        self.processing_history.append(f"add_{dataset_name}")

    @rule(dataset_name=st.sampled_from(["base"]), target=st.sampled_from(["base"]))
    def calculate_gdp_per_capita(self, dataset_name, target):
        """Calculate GDP per capita for a dataset."""
        assume(dataset_name in self.data_store)

        df = self.data_store[dataset_name].copy()
        assume("gdp_usd" in df.columns and "population" in df.columns)
        assume((df["population"] > 0).all())

        df["gdp_per_capita"] = df["gdp_usd"] / df["population"]
        self.data_store[target] = df
        self.processing_history.append(f"gdp_per_capita_{dataset_name}_to_{target}")

    @rule(dataset_name=st.sampled_from(["base"]), target=st.sampled_from(["base"]))
    def calculate_growth_rates(self, dataset_name, target):
        """Calculate growth rates for a dataset."""
        assume(dataset_name in self.data_store)

        df = self.data_store[dataset_name].copy()
        assume("gdp_usd" in df.columns)
        assume(len(df) > 1)

        df = df.sort_values("year")
        df["gdp_growth"] = df["gdp_usd"].pct_change() * 100
        self.data_store[target] = df
        self.processing_history.append(f"growth_rates_{dataset_name}_to_{target}")

    @invariant()
    def data_store_consistency(self):
        """Invariant: Data store should maintain consistency."""
        # All datasets should have valid data
        for name, df in self.data_store.items():
            assert isinstance(df, pd.DataFrame), f"Dataset {name} should be a DataFrame"
            assert len(df) > 0, f"Dataset {name} should not be empty"
            assert "year" in df.columns, f"Dataset {name} should have year column"

    @invariant()
    def gdp_per_capita_validity(self):
        """Invariant: GDP per capita should be positive when present."""
        for name, df in self.data_store.items():
            if "gdp_per_capita" in df.columns:
                assert (df["gdp_per_capita"] > 0).all(), f"GDP per capita in {name} should be positive"

    @invariant()
    def year_ordering(self):
        """Invariant: Years should be in ascending order when sorted."""
        for name, df in self.data_store.items():
            if len(df) > 1:
                sorted_df = df.sort_values("year")
                years = sorted_df["year"].tolist()
                assert years == sorted(years), f"Years in {name} should be sortable"


# Test the state machine
TestDataProcessingStateMachine = DataProcessingStateMachine.TestCase


class TestAdvancedProperties:
    """Advanced property-based tests with complex scenarios."""

    @given(
        st.lists(
            st.tuples(
                st.integers(min_value=1990, max_value=2030),  # year
                st.floats(min_value=1e10, max_value=1e15, allow_nan=False),  # gdp
                st.floats(min_value=-10, max_value=20, allow_nan=False),  # inflation
            ),
            min_size=2,
            max_size=20,
            unique_by=lambda x: x[0],  # unique years
        )
    )
    @settings(max_examples=20, deadline=2000)
    def test_time_series_properties(self, time_series_data):
        """Test properties of time series data processing."""
        # Sort by year
        time_series_data.sort(key=lambda x: x[0])

        years, gdp_values, inflation_rates = zip(*time_series_data, strict=False)

        # Create DataFrame
        df = pd.DataFrame({"year": years, "gdp_usd": gdp_values, "inflation_rate": inflation_rates})

        # Calculate year-over-year changes
        df["gdp_change"] = df["gdp_usd"].diff()
        df["inflation_change"] = df["inflation_rate"].diff()

        # Properties
        assert len(df) == len(time_series_data), "DataFrame should have correct length"
        assert df["year"].is_monotonic_increasing, "Years should be in ascending order"

        # First values should be NaN for difference calculations
        assert pd.isna(df["gdp_change"].iloc[0]), "First GDP change should be NaN"
        assert pd.isna(df["inflation_change"].iloc[0]), "First inflation change should be NaN"

        # Changes should be calculable for subsequent years
        for i in range(1, len(df)):
            expected_gdp_change = df["gdp_usd"].iloc[i] - df["gdp_usd"].iloc[i - 1]
            assert abs(df["gdp_change"].iloc[i] - expected_gdp_change) < 1e-6


# Performance property tests
class TestPerformanceProperties:
    """Property-based tests for performance characteristics."""

    @given(st.integers(min_value=100, max_value=10000))
    @settings(max_examples=10, deadline=5000)
    def test_processing_time_scales_linearly(self, data_size):
        """Test that processing time scales reasonably with data size."""
        import time

        # Generate test data
        df = pd.DataFrame(
            {"year": range(2000, 2000 + data_size), "value": np.random.default_rng().random(data_size) * 1e12}
        )

        # Measure processing time
        start_time = time.time()

        # Simple processing operation
        df["normalized"] = (df["value"] - df["value"].min()) / (df["value"].max() - df["value"].min())
        df["moving_avg"] = df["value"].rolling(window=min(5, len(df))).mean()

        processing_time = time.time() - start_time

        # Performance property: should complete within reasonable time
        # Allowing 1ms per 1000 records as a reasonable baseline
        max_expected_time = data_size / 1000 * 0.001
        assert processing_time < max_expected_time * 10, (
            f"Processing took too long: {processing_time}s for {data_size} records"
        )
