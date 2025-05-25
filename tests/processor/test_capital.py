"""Tests for capital stock calculations."""

import numpy as np
import pandas as pd

from utils.capital import calculate_capital_stock, project_capital_stock


def test_calculate_capital_stock_missing():
    raw = pd.DataFrame({"year": [2017]})
    result = calculate_capital_stock(raw)
    assert "K_USD_bn" in result.columns
    assert np.isnan(result["K_USD_bn"]).all()


def test_calculate_capital_stock_basic():
    raw = pd.DataFrame(
        {
            "year": [2017, 2018],
            "rkna": [2.0, 2.1],
            "pl_gdpo": [3.0, 3.1],
            "cgdpo_bn": [4.0, 4.4],
        }
    )
    df = calculate_capital_stock(raw, capital_output_ratio=3)
    assert not df["K_USD_bn"].isna().all()
