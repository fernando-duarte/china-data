"""Tests for economic indicator and TFP calculations."""

from unittest import mock

import numpy as np
import pandas as pd
import pytest

from config import Config
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
    assert "K_Y_ratio" not in result.columns
    assert "TFP" in result.columns
    assert "T_USD_bn" in result.columns
    assert "Openness_Ratio" in result.columns
    assert "S_USD_bn" in result.columns
    assert "S_priv_USD_bn" in result.columns
    assert "S_pub_USD_bn" in result.columns
    assert "Saving_Rate" in result.columns

    # Check some calculations
    assert np.allclose(result["NX_USD_bn"], result["X_USD_bn"] - result["M_USD_bn"])
    # Compare T_USD_bn with expected calculation, considering rounding
    expected_T_USD_bn = (data["TAX_pct_GDP"] / 100) * data["GDP_USD_bn"]
    assert np.allclose(result["T_USD_bn"], expected_T_USD_bn.round(Config.DECIMAL_PLACES_CURRENCY))

    # Corrected saving calculation assertion based on S = Y - C - G
    expected_S_USD_bn = data["GDP_USD_bn"] - data["C_USD_bn"] - data["G_USD_bn"]
    assert np.allclose(result["S_USD_bn"], expected_S_USD_bn.round(Config.DECIMAL_PLACES_CURRENCY))

    # New tests for economic indicators
    # private saving + public saving = saving
    assert np.allclose(result["S_USD_bn"], result["S_priv_USD_bn"].fillna(0) + result["S_pub_USD_bn"].fillna(0))

    # openness = (exports+imports)/Y
    expected_processor_openness = (result["X_USD_bn"] + result["M_USD_bn"]) / result["GDP_USD_bn"]
    assert result["Openness_Ratio"].tolist() == pytest.approx(expected_processor_openness.tolist(), rel=1e-4)

    # saving rate = S/Y
    expected_processor_saving_rate = result["S_USD_bn"] / result["GDP_USD_bn"]
    assert result["Saving_Rate"].tolist() == pytest.approx(expected_processor_saving_rate.tolist(), rel=1e-4)

    # saving rate = 1 - (C_t + G_t)/Y_t (GDP Identity based saving)
    expected_identity_saving_rate = 1 - (result["C_USD_bn"] + result["G_USD_bn"]) / result["GDP_USD_bn"]
    assert result["Saving_Rate"].tolist() == pytest.approx(expected_identity_saving_rate.tolist(), rel=1e-4)

    # taxes > 0 (for years where tax data is available)
    assert (result.loc[result["TAX_pct_GDP"].notna(), "T_USD_bn"].dropna() > 0).all()

    # A > 0 (TFP > 0)
    assert (result["TFP"].dropna() > 0).all()

    processed_data = calculate_economic_indicators(data)

    expected_columns = [
        "TFP",
        "T_USD_bn",
        "Openness_Ratio",
        "NX_USD_bn",
        "S_USD_bn",
        "S_priv_USD_bn",
        "S_pub_USD_bn",
        "Saving_Rate",
        # "K_Y_ratio" # This indicator is not calculated by calculate_economic_indicators
    ]
    for col in expected_columns:
        assert col in processed_data.columns, f"Missing expected column: {col}"

    # Example check for TFP (can add more specific value checks if needed)
