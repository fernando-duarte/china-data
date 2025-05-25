import os
import shutil
import tempfile

import pytest

from utils.processor_load import load_raw_data


def pytest_configure(config):
    os.environ.setdefault("PYTHONPATH", os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture(scope="session")
def raw_df():
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
    original_cwd = os.getcwd()

    # Change to temp directory
    os.chdir(str(tmp_path))

    yield tmp_path

    # Restore original directory
    os.chdir(original_cwd)
