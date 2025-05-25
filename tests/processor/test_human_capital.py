"""Tests for human capital projection."""


import numpy as np
import pandas as pd

from utils.processor_hc import project_human_capital


def test_project_human_capital_fallback(monkeypatch):
    data = pd.DataFrame({"year": [2017, 2018], "hc": [1.0, np.nan]})
    # This test doesn't need to mock ExponentialSmoothing since we're using LinearRegression now
    df = project_human_capital(data, end_year=2019)
    # Should return a DataFrame even if no projection is performed
    assert isinstance(df, pd.DataFrame)
