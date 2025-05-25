import os

from utils import ensure_directory, find_file, get_output_directory, get_project_root
from utils.path_constants import OUTPUT_DIR_NAME


def test_get_project_root_returns_existing_directory():
    root = get_project_root()
    assert os.path.isdir(root)
    # Check that the directory exists and contains expected project files
    assert os.path.isfile(os.path.join(root, "README.md"))
    assert os.path.isdir(os.path.join(root, "utils"))


def test_find_file_locates_known_file():
    path = find_file("README.md", [""])  # Look in project root
    assert path and path.endswith("README.md")


def test_ensure_directory_creates_path(tmp_path):
    new_dir = tmp_path / "sub"
    path = ensure_directory(str(new_dir))
    assert os.path.isdir(path)


def test_get_output_directory_exists():
    out_dir = get_output_directory()
    expected = os.path.join(get_project_root(), OUTPUT_DIR_NAME)
    assert out_dir == expected
    assert os.path.isdir(out_dir)
