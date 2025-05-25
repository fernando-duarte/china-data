"""Tests for output file generation."""

import os

import pandas as pd

from utils.output import create_markdown_table


def test_create_markdown_table(tmp_path):
    data = pd.DataFrame(
        {
            "Year": [2024],
            "GDP_USD_bn": [1.0],
            "C_USD_bn": [1.0],
            "G_USD_bn": [1.0],
            "I_USD_bn": [1.0],
            "X_USD_bn": [1.0],
            "M_USD_bn": [1.0],
            "NX_USD_bn": [0.0],
            "POP_mn": [1.0],
            "LF_mn": [1.0],
            "K_USD_bn": [2.0],
            "TFP": [1.0],
            "FDI_pct_GDP": [0.1],
            "TAX_pct_GDP": [0.2],
            "hc": [1.0],
        }
    )
    out = tmp_path / "out.md"
    create_markdown_table(data, str(out), {"GDP_USD_bn": {"method": "test", "years": [2024]}}, end_year=2024)
    assert out.exists()
