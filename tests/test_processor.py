"""Test suite for the china_data_processor.py functionality.

This module tests the data processing pipeline including:
- Loading raw data from markdown files
- Unit conversion functions
- Capital stock calculations
- Human capital projections
- Economic indicator calculations (TFP, savings, etc.)
- Time series extrapolation methods
- Output file generation
"""

import os
import pandas as pd
import numpy as np
import pytest
from unittest import mock

from utils.processor_load import load_raw_data
from utils.processor_units import convert_units
from utils.capital import calculate_capital_stock, project_capital_stock
from utils.processor_hc import project_human_capital
from utils.economic_indicators import calculate_tfp, calculate_economic_indicators
from utils.processor_extrapolation import extrapolate_series_to_end_year
from utils.processor_output import create_markdown_table
from statsmodels.tsa.arima.model import ARIMA
from sklearn.linear_model import LinearRegression

# Use a temporary file for testing
def test_load_raw_data_success(monkeypatch, tmp_path):
    # Create a temporary directory for the test
    output_dir = tmp_path / 'china_data' / 'output'
    os.makedirs(output_dir, exist_ok=True)
    dummy_raw_md_path = output_dir / 'china_data_raw.md'

    # Create a dummy markdown file
    with open(dummy_raw_md_path, 'w') as f:
        f.write("# China Economic Data\n\n")
        f.write("## Economic Data (1960-present)\n\n")
        f.write("| Year | GDP (USD) |\n")
        f.write("|------|-----------|\n")
        f.write("| 2020 | 100       |\n")

    # Mock the find_file function to return our temporary file
    def mock_find_file(filename, possible_locations_relative_to_root=None):
        if filename == 'china_data_raw.md':
            return str(dummy_raw_md_path)
        return None

    # Apply the mock
    from utils import processor_load
    monkeypatch.setattr(processor_load, 'find_file', mock_find_file)

    # Test the function
    df = load_raw_data(input_file='china_data_raw.md')
    assert not df.empty
    assert 'GDP_USD' in df.columns


def test_load_raw_data_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        # load_raw_data will search standard locations. 'missing.md' should not be there.
        load_raw_data(input_file='missing.md')


def test_convert_units():
    raw = pd.DataFrame({
        'year': [2017],
        'GDP_USD': [1e12],
        'rgdpo': [1000],
        'POP': [1000000],
        'LF': [500000],
    })
    out = convert_units(raw)
    assert out['GDP_USD_bn'].iloc[0] == 1000
    assert out['rgdpo_bn'].iloc[0] == 1
    assert out['POP_mn'].iloc[0] == 1
    assert out['LF_mn'].iloc[0] == 0.5


def test_calculate_capital_stock_missing():
    raw = pd.DataFrame({'year':[2017]})
    result = calculate_capital_stock(raw)
    assert 'K_USD_bn' in result.columns
    assert np.isnan(result['K_USD_bn']).all()


def test_calculate_capital_stock_basic():
    raw = pd.DataFrame({
        'year': [2017,2018],
        'rkna': [2.0, 2.1],
        'pl_gdpo': [3.0, 3.1],
        'cgdpo': [4.0, 4.4],
    })
    df = calculate_capital_stock(raw, capital_output_ratio=3)
    assert not df['K_USD_bn'].isna().all()

def test_project_human_capital_fallback(monkeypatch):
    data = pd.DataFrame({'year':[2017,2018],'hc':[1.0,np.nan]})
    # This test doesn't need to mock ExponentialSmoothing since we're using LinearRegression now
    df = project_human_capital(data, end_year=2019)
    # Should return a DataFrame even if no projection is performed
    assert isinstance(df, pd.DataFrame)


def test_calculate_tfp_with_missing_hc():
    data = pd.DataFrame({'year':[2017,2018],'GDP_USD_bn':[2.0,2.1],'K_USD_bn':[1.0,1.1],'LF_mn':[1,1.1],'hc':[1.0,np.nan]})
    out = calculate_tfp(data)
    assert 'TFP' in out.columns


def test_calculate_economic_indicators():
    data = pd.DataFrame({
        'year': [2017, 2018],
        'GDP_USD_bn': [2.0, 2.1],
        'K_USD_bn': [1.0, 1.1],
        'LF_mn': [1, 1.1],
        'hc': [1.0, 1.0],
        'X_USD_bn': [0.5, 0.6],
        'M_USD_bn': [0.4, 0.5],
        'C_USD_bn': [1.0, 1.1],
        'G_USD_bn': [0.3, 0.4],
        'TAX_pct_GDP': [20.0, 21.0]
    })

    # Create a mock logger
    mock_logger = mock.MagicMock()

    result = calculate_economic_indicators(data, alpha=1/3, logger=mock_logger)

    # Check that all expected columns were added
    assert 'NX_USD_bn' in result.columns
    assert 'K_Y_ratio' in result.columns
    assert 'TFP' in result.columns
    assert 'T_USD_bn' in result.columns
    assert 'Openness_Ratio' in result.columns
    assert 'S_USD_bn' in result.columns
    assert 'S_priv_USD_bn' in result.columns
    assert 'S_pub_USD_bn' in result.columns
    assert 'Saving_Rate' in result.columns

    # Check some calculations
    assert round(result['NX_USD_bn'].iloc[0], 4) == 0.1  # 0.5 - 0.4
    assert round(result['T_USD_bn'].iloc[0], 4) == 0.4  # (20.0 / 100) * 2.0
    assert round(result['S_USD_bn'].iloc[0], 4) == 0.7  # 2.0 - 1.0 - 0.3


def test_extrapolate_series_to_end_year(monkeypatch):
    df = pd.DataFrame({
        'year':[2023],
        'GDP_USD_bn':[1.0],
        'C_USD_bn':[1.0],
        'G_USD_bn':[1.0],
        'I_USD_bn':[1.0],
        'X_USD_bn':[1.0],
        'M_USD_bn':[1.0],
        'POP_mn':[1.0],
        'LF_mn':[1.0],
    })
    class Dummy:
        def fit(self):
            return self
        def forecast(self, steps):
            return [1.0]*steps
    # Import the modules where ARIMA and LinearRegression are used
    import utils.extrapolation_methods.arima as arima_module
    import utils.extrapolation_methods.linear_regression as linear_regression_module

    # Mock the extrapolation functions to return successful results
    def mock_extrapolate_with_arima(df, col, years, **kwargs):
        for year in years:
            df.loc[df.year == year, col] = 1.0
        return df, True, "ARIMA"

    def mock_extrapolate_with_linear_regression(df, col, years, **kwargs):
        for year in years:
            df.loc[df.year == year, col] = 1.0
        return df, True, "Linear regression"

    # Apply the mocks
    import utils.processor_extrapolation as extrapolation_module
    monkeypatch.setattr(extrapolation_module, 'extrapolate_with_arima', mock_extrapolate_with_arima)
    monkeypatch.setattr(extrapolation_module, 'extrapolate_with_linear_regression', mock_extrapolate_with_linear_regression)
    out, info = extrapolate_series_to_end_year(df, end_year=2024, raw_data=df)
    assert 2024 in out['year'].values
    assert isinstance(info, dict)


def test_create_markdown_table(tmp_path):
    data = pd.DataFrame({
        'Year':[2024],
        'GDP_USD_bn':[1.0],
        'C_USD_bn':[1.0],
        'G_USD_bn':[1.0],
        'I_USD_bn':[1.0],
        'X_USD_bn':[1.0],
        'M_USD_bn':[1.0],
        'NX_USD_bn':[0.0],
        'POP_mn':[1.0],
        'LF_mn':[1.0],
        'K_USD_bn':[2.0],
        'TFP':[1.0],
        'FDI_pct_GDP':[0.1],
        'TAX_pct_GDP':[0.2],
        'hc':[1.0]
    })
    out = tmp_path/'out.md'
    create_markdown_table(data, str(out), {'GDP_USD_bn': {'method':'test','years':[2024]}}, end_year=2024)
    assert out.exists()