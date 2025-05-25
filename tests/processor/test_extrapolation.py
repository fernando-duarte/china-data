"""Tests for time series extrapolation functionality."""


import pandas as pd

from utils.processor_extrapolation import extrapolate_series_to_end_year


def test_extrapolate_series_to_end_year(monkeypatch):
    df = pd.DataFrame(
        {
            "year": [2023],
            "GDP_USD_bn": [1.0],
            "C_USD_bn": [1.0],
            "G_USD_bn": [1.0],
            "I_USD_bn": [1.0],
            "X_USD_bn": [1.0],
            "M_USD_bn": [1.0],
            "POP_mn": [1.0],
            "LF_mn": [1.0],
        }
    )

    class Dummy:
        def fit(self):
            return self

        def forecast(self, steps):
            return [1.0] * steps


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

    monkeypatch.setattr(extrapolation_module, "extrapolate_with_arima", mock_extrapolate_with_arima)
    monkeypatch.setattr(
        extrapolation_module, "extrapolate_with_linear_regression", mock_extrapolate_with_linear_regression
    )
    out, info = extrapolate_series_to_end_year(df, end_year=2024, raw_data=df)
    assert 2024 in out["year"].values
    assert isinstance(info, dict)
