import os
from pathlib import Path

import pytest

from tests.factories import DataFrameFactory, create_complete_economic_data, create_minimal_economic_data
from utils.processor_load import load_raw_data


@pytest.fixture(scope="session")
def raw_df():
    """Load raw data for testing."""
    return load_raw_data("china_data_raw.md")


@pytest.fixture
def temp_project_root(tmp_path):
    """Create a temporary project root for testing."""
    # Create project structure
    (tmp_path / "utils").mkdir()
    (tmp_path / "input").mkdir()
    (tmp_path / "output").mkdir()
    (tmp_path / "parameters_info").mkdir()

    # Create a README to identify as project root
    (tmp_path / "README.md").write_text("Test project")

    # Save current directory
    original_cwd = Path.cwd()

    # Change to temp directory
    os.chdir(str(tmp_path))

    yield tmp_path

    # Restore original directory
    os.chdir(str(original_cwd))


@pytest.fixture(autouse=True)
def mock_cached_session_for_tests(monkeypatch):
    """Globally mocks get_cached_session to return a non-cached session for all tests."""
    import requests

    def non_cached_session():
        return requests.Session()

    monkeypatch.setattr("utils.caching_utils.get_cached_session", non_cached_session)


@pytest.fixture
def minimal_economic_data():
    """Fixture providing minimal economic data for testing."""
    return create_minimal_economic_data()


@pytest.fixture
def complete_economic_data():
    """Fixture providing complete economic data for testing."""
    return create_complete_economic_data()


@pytest.fixture
def economic_data_with_missing():
    """Fixture providing economic data with missing values."""
    return DataFrameFactory.create_economic_dataframe(
        years=[2020, 2021, 2022], include_missing=True, missing_probability=0.2
    )


@pytest.fixture
def china_growth_data():
    """Fixture providing China growth scenario data."""
    from tests.factories import create_china_growth_scenario

    return create_china_growth_scenario()
