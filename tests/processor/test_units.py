"""Tests for unit conversion functionality."""

import pandas as pd

from utils.processor_units import convert_units


def test_convert_units():
    raw = pd.DataFrame(
        {
            "year": [2017],
            "GDP_USD": [1e12],
            "rgdpo": [1000],
            "POP": [1000000],
            "LF": [500000],
        }
    )
    out = convert_units(raw)
    assert out["GDP_USD_bn"].iloc[0] == 1e9
    assert out["rgdpo"].iloc[0] == 1000
    assert out["POP_mn"].iloc[0] == 1000
    assert out["LF_mn"].iloc[0] == 500
