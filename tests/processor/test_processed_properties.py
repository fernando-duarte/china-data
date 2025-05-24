"""Tests for properties and initial values of processed data."""

import pandas as pd
import numpy as np

def test_processed_data_properties():
    # Load the processed data CSV
    processed_df = pd.read_csv('output/china_data_processed.csv')

    # K increasing over time
    assert (processed_df['Physical Capital'].diff().dropna() >= 0).all()

    # L increasing over time (Labor Force)
    # Note: Labor Force data is sparse before 1990, so we check from 1990 onwards
    lf_data = processed_df.set_index('Year')['Labor Force'].dropna()
    assert (lf_data.diff().dropna() >= 0).all()

    # K/Y ratio in 2017 between 1 and 5
    k_y_2017 = processed_df[processed_df['Year'] == 2017]['Physical Capital'].iloc[0] / processed_df[processed_df['Year'] == 2017]['GDP'].iloc[0]
    assert 1 <= k_y_2017 <= 5

    # Check 1980 initial values for K, X, M against china_data_processed.csv
    data_1980 = processed_df[processed_df['Year'] == 1980]
    assert data_1980['Physical Capital'].iloc[0] > 0 and np.isclose(data_1980['Physical Capital'].iloc[0], 337.49)
    assert data_1980['Exports'].iloc[0] > 0 and np.isclose(data_1980['Exports'].iloc[0], 19.4057)
    assert data_1980['Imports'].iloc[0] > 0 and np.isclose(data_1980['Imports'].iloc[0], 21.8427) 