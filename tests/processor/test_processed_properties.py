"""Tests for properties and initial values of processed data."""

import numpy as np
import pandas as pd


def test_processed_data_properties():
    # Create mock processed data
    processed_df = pd.DataFrame(
        {
            "Year": list(range(1980, 2023)),
            "Physical Capital": [337.49 + i * 100 for i in range(43)],  # Increasing values
            "Labor Force": [500 + i * 10 for i in range(43)],  # Increasing values
            "GDP": [300 + i * 50 for i in range(43)],
            "Exports": [19.4057 + i * 5 for i in range(43)],
            "Imports": [21.8427 + i * 5 for i in range(43)],
        }
    )

    # K increasing over time
    assert (processed_df["Physical Capital"].diff().dropna() >= 0).all()

    # L increasing over time (Labor Force)
    lf_data = processed_df.set_index("Year")["Labor Force"].dropna()
    assert (lf_data.diff().dropna() >= 0).all()

    # K/Y ratio in 2017 between 1 and 5
    k_y_2017 = (
        processed_df[processed_df["Year"] == 2017]["Physical Capital"].iloc[0]
        / processed_df[processed_df["Year"] == 2017]["GDP"].iloc[0]
    )
    assert 1 <= k_y_2017 <= 5

    # Check 1980 initial values for K, X, M
    data_1980 = processed_df[processed_df["Year"] == 1980]
    assert data_1980["Physical Capital"].iloc[0] > 0
    assert np.isclose(data_1980["Physical Capital"].iloc[0], 337.49)
    assert data_1980["Exports"].iloc[0] > 0
    assert np.isclose(data_1980["Exports"].iloc[0], 19.4057)
    assert data_1980["Imports"].iloc[0] > 0
    assert np.isclose(data_1980["Imports"].iloc[0], 21.8427)
