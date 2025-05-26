"""Tests for data loading functionality."""

import pytest

from utils.processor_load import load_raw_data


def test_load_raw_data_success(monkeypatch, tmp_path):
    # Create a temporary directory for the test
    output_dir = tmp_path / "china_data" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    dummy_raw_md_path = output_dir / "china_data_raw.md"

    # Create a dummy markdown file
    dummy_raw_md_path.write_text(
        "# China Economic Data\n\n"
        "## Economic Data (1960-present)\n\n"
        "| Year | GDP (USD) |\n"
        "|------|-----------|\n"
        "| 2020 | 100 |\n"
    )

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
