"""
Snapshot testing for data pipelines using syrupy.

This module demonstrates snapshot testing to ensure data processing
output remains consistent across changes.
"""

from typing import Any, cast

import pandas as pd
import pytest

try:
    from syrupy import SnapshotAssertion
except ImportError:
    # Fallback for when syrupy is not available
    SnapshotAssertion = Any  # type: ignore[misc,assignment]


# Mock data processing functions for testing
def process_china_data_sample() -> dict[str, Any]:
    """Process a sample of China data for testing."""
    return {
        "gdp_growth": [6.1, 2.3, 8.1],
        "inflation": [2.9, 2.5, 0.9],
        "unemployment": [5.2, 5.9, 5.5],
        "years": [2019, 2020, 2021],
        "metadata": {
            "source": "test_data",
            "processed_at": "2025-01-01T00:00:00Z",
            "version": "1.0.0",
        },
    }


def process_economic_indicators() -> pd.DataFrame:
    """Process economic indicators for testing."""
    return pd.DataFrame(
        {
            "year": [2020, 2021, 2022],
            "gdp_usd": [14.34e12, 17.73e12, 17.95e12],
            "gdp_growth_rate": [2.3, 8.1, 3.0],
            "cpi_inflation": [2.5, 0.9, 2.0],
            "unemployment_rate": [5.9, 5.5, 5.4],
        }
    )


class TestDataProcessingSnapshots:
    """Test data processing output consistency using snapshots."""

    def test_china_data_processing_output(self, snapshot: SnapshotAssertion):
        """Ensure China data processing output remains consistent."""
        result = process_china_data_sample()
        assert result == snapshot

    def test_economic_indicators_dataframe(self, snapshot: SnapshotAssertion):
        """Ensure economic indicators DataFrame structure is consistent."""
        df = process_economic_indicators()

        # Convert DataFrame to dict for snapshot comparison
        result = {
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "shape": df.shape,
            "data": df.to_dict("records"),
        }

        assert result == snapshot

    def test_data_transformation_pipeline(self, snapshot: SnapshotAssertion):
        """Test complete data transformation pipeline output."""
        # Simulate a data transformation pipeline
        raw_data = {
            "gdp_nominal": [14.34e12, 17.73e12, 17.95e12],
            "population": [1.411e9, 1.412e9, 1.413e9],
            "years": [2020, 2021, 2022],
        }

        # Transform data (calculate GDP per capita)
        gdp_nominal = cast("list[float]", raw_data["gdp_nominal"])
        population = cast("list[float]", raw_data["population"])
        transformed = {
            "year": raw_data["years"],
            "gdp_per_capita": [
                gdp / pop for gdp, pop in zip(gdp_nominal, population, strict=False)
            ],
            "gdp_nominal_trillions": [gdp / 1e12 for gdp in gdp_nominal],
            "transformation_metadata": {
                "method": "gdp_per_capita_calculation",
                "currency": "USD",
                "base_year": 2020,
            },
        }

        assert transformed == snapshot

    @pytest.mark.parametrize(("year", "expected_records"), [(2020, 1), (2021, 2), (2022, 3)])
    def test_yearly_data_filtering(
        self, snapshot: SnapshotAssertion, year: int, expected_records: int
    ):
        """Test yearly data filtering with snapshots."""
        df = process_economic_indicators()

        # Filter data up to the specified year
        filtered_df = df[df["year"] <= year]

        result = {
            "filter_year": year,
            "record_count": len(filtered_df),
            "data": filtered_df.to_dict("records"),
        }

        assert result == snapshot
        assert len(filtered_df) == expected_records


class TestDataValidationSnapshots:
    """Test data validation output using snapshots."""

    def test_data_quality_report(self, snapshot: SnapshotAssertion):
        """Test data quality validation report structure."""
        df = process_economic_indicators()

        # Generate data quality report
        quality_report = {
            "total_records": len(df),
            "missing_values": df.isna().sum().to_dict(),
            "data_types": df.dtypes.astype(str).to_dict(),
            "numeric_summaries": {
                col: {
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "mean": float(df[col].mean()),
                }
                for col in df.select_dtypes(include=["number"]).columns
            },
            "validation_timestamp": "2025-01-01T00:00:00Z",  # Fixed for testing
        }

        assert quality_report == snapshot

    def test_outlier_detection_results(self, snapshot: SnapshotAssertion):
        """Test outlier detection algorithm results."""
        df = process_economic_indicators()

        # Simple outlier detection using IQR method
        outliers = {}
        for col in df.select_dtypes(include=["number"]).columns:
            if col != "year":  # Skip year column
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr

                outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
                outlier_indices = df[outlier_mask].index.tolist()
                outliers[col] = {
                    "outlier_count": int(outlier_mask.sum()),
                    "outlier_indices": outlier_indices,
                    "bounds": {"lower": float(lower_bound), "upper": float(upper_bound)},
                }

        result = {
            "outlier_analysis": outliers,
            "total_outliers": sum(info["outlier_count"] for info in outliers.values()),
        }

        assert result == snapshot


# Configuration for snapshot testing
@pytest.fixture
def snapshot_config():
    """Configure snapshot testing behavior."""
    return {
        "update_snapshots": False,  # Set to True to update snapshots
        "include_metadata": True,
    }
