from pathlib import Path

from utils import ensure_directory, find_file, get_output_directory, get_project_root
from utils.path_constants import OUTPUT_DIR_NAME


def test_get_project_root_returns_existing_directory():
    root = get_project_root()
    root_path = Path(root)
    assert root_path.is_dir()
    # Check that the directory exists and contains expected project files
    assert (root_path / "README.md").is_file()
    assert (root_path / "utils").is_dir()


def test_find_file_locates_known_file():
    path = find_file("README.md", [""])  # Look in project root
    assert path is not None
    assert path.endswith("README.md")


def test_ensure_directory_creates_path(tmp_path):
    new_dir = tmp_path / "sub"
    path = ensure_directory(str(new_dir))
    assert Path(path).is_dir()


def test_get_output_directory_exists():
    out_dir = get_output_directory()
    expected = Path(get_project_root()) / OUTPUT_DIR_NAME
    assert out_dir == str(expected)
    assert Path(out_dir).is_dir()
