import os

from utils.path_constants import INPUT_DIR_NAME, OUTPUT_DIR_NAME, get_search_locations_relative_to_root


class TestPathConstants:
    """Test suite for path_constants module."""

    def test_directory_constants(self):
        """Test that directory name constants are defined correctly."""
        assert INPUT_DIR_NAME == "input"
        assert OUTPUT_DIR_NAME == "output"

    def test_get_search_locations_relative_to_root(self):
        """Test that search locations are returned correctly."""
        locations = get_search_locations_relative_to_root()

        # Check that it returns a dictionary
        assert isinstance(locations, dict)

        # Check for expected keys
        assert "input_files" in locations
        assert "output_files" in locations
        assert "config_files" in locations
        # assert "general" in locations # 'general' key is not currently defined or used

        # Check that input_files contains expected directories
        input_files = locations["input_files"]
        assert isinstance(input_files, list)
        assert "input" in input_files

        # Check that output_files contains expected directories
        output_files = locations["output_files"]
        assert isinstance(output_files, list)
        assert "output" in output_files

    def test_path_construction(self):
        """Test that paths are constructed correctly for different scenarios."""
        locations = get_search_locations_relative_to_root()

        # Check that paths are properly formatted
        for path_list in locations.values():
            for path in path_list:
                # Paths should not have trailing slashes
                assert not path.endswith("/")
                # Paths should use forward slashes
                assert "\\" not in path or os.name == "nt"
