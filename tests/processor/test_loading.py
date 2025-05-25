"""Tests for data loading functionality."""

import os
from unittest import mock

import pandas as pd
import pytest

from utils.processor_load import load_raw_data


def test_load_raw_data_success(monkeypatch, tmp_path):
    # Create a temporary directory for the test
    output_dir = tmp_path / "china_data" / "output"
    os.makedirs(output_dir, exist_ok=True)
    dummy_raw_md_path = output_dir / "china_data_raw.md"

    # Create a dummy markdown file
    with open(dummy_raw_md_path, "w") as f:
        f.write("# China Economic Data\n\n")
        f.write("## Economic Data (1960-present)\n\n")
        f.write("| Year | GDP (USD) |\n")
        f.write("|------|-----------|\n")
        f.write("| 2020 | 100       |\n")

    # Mock the find_file function to return our temporary file
    def mock_find_file(filename, possible_locations_relative_to_root=None):
        if filename == "china_data_raw.md":
            return str(dummy_raw_md_path)
        return None

    # Apply the mock
    from utils import processor_load

    monkeypatch.setattr(processor_load, "find_file", mock_find_file)

    # Test the function
    df = load_raw_data(input_file="china_data_raw.md")
    assert not df.empty
    assert "GDP_USD" in df.columns


def test_load_raw_data_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        # load_raw_data will search standard locations. 'missing.md' should not be there.
        load_raw_data(input_file="missing.md")
