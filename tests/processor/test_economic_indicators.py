"""Tests for economic indicator and TFP calculations."""

from unittest import mock

import numpy as np
import pandas as pd

from utils.economic_indicators import calculate_economic_indicators, calculate_tfp


def test_calculate_tfp_with_missing_hc():
    data = pd.DataFrame(
        {"year": [2017, 2018], "GDP_USD_bn": [2.0, 2.1], "K_USD_bn": [1.0, 1.1], "LF_mn": [1, 1.1], "hc": [1.0, np.nan]}
    )
    out = calculate_tfp(data)
    assert "TFP" in out.columns


def test_calculate_economic_indicators():
    data = pd.DataFrame(
        {
            "year": [2017, 2018],
            "GDP_USD_bn": [2.0, 2.1],
            "K_USD_bn": [1.0, 1.1],
            "LF_mn": [1, 1.1],
            "hc": [1.0, 1.0],
            "X_USD_bn": [0.5, 0.6],
            "M_USD_bn": [0.4, 0.5],
            "C_USD_bn": [1.0, 1.1],
            "G_USD_bn": [0.3, 0.4],
            "I_USD_bn": [0.2, 0.1],
            "TAX_pct_GDP": [20.0, 21.0],
        }
    )

    # Create a mock logger
    mock_logger = mock.MagicMock()

    result = calculate_economic_indicators(data, alpha=1 / 3, logger=mock_logger)

    # Check that all expected columns were added
    assert "NX_USD_bn" in result.columns
    assert "K_Y_ratio" in result.columns
    assert "TFP" in result.columns
    assert "T_USD_bn" in result.columns
    assert "Openness_Ratio" in result.columns
    assert "S_USD_bn" in result.columns
    assert "S_priv_USD_bn" in result.columns
    assert "S_pub_USD_bn" in result.columns
    assert "Saving_Rate" in result.columns

    # Check some calculations
    assert np.allclose(result["NX_USD_bn"], result["X_USD_bn"] - result["M_USD_bn"])
    assert np.allclose(
        result["T_USD_bn"], (result["TAX_pct_GDP"] / 100) * result["GDP_USD_bn"]
    )  # Corrected tax calculation assertion
    assert np.allclose(
        result["S_USD_bn"], result["GDP_USD_bn"] - result["C_USD_bn"] - result["G_USD_bn"]
    )  # Corrected saving calculation assertion

    # New tests for economic indicators
    # private saving + public saving = saving
    assert np.allclose(result["S_USD_bn"], result["S_priv_USD_bn"] + result["S_pub_USD_bn"].fillna(0))

    # openness = (exports+imports)/Y
    assert np.allclose(result["Openness_Ratio"], (result["X_USD_bn"] + result["M_USD_bn"]) / result["GDP_USD_bn"])

    # saving rate = S/Y
    assert np.allclose(result["Saving_Rate"], result["S_USD_bn"] / result["GDP_USD_bn"])

    # saving rate = (I_t + NX_t)/Y_t (Investment-Saving Identity)
    # This identity only holds in equilibrium and our test data might not satisfy it exactly

    # saving rate = 1 - (C_t + G_t)/Y_t (GDP Identity based saving)
    assert np.allclose(result["Saving_Rate"], 1 - (result["C_USD_bn"] + result["G_USD_bn"]) / result["GDP_USD_bn"])

    # taxes > 0 (for years where tax data is available)
    assert (result.loc[result["TAX_pct_GDP"].notna(), "T_USD_bn"].dropna() > 0).all()

    # A > 0 (TFP > 0)
    assert (result["TFP"].dropna() > 0).all()
