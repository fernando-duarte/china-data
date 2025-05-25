import sys
from unittest.mock import patch

import pytest

from utils.processor_cli import parse_arguments


class TestProcessorCLI:
    """Test suite for processor CLI argument parsing."""

    def test_default_arguments(self):
        """Test parsing with default arguments."""
        with patch.object(sys, "argv", ["prog"]):
            args = parse_arguments()

            # Check default values
            assert args.input_file == "china_data_raw.md"
            assert args.output_file == "china_data_processed"
            assert args.alpha == 1 / 3
            assert args.capital_output_ratio == 3.0
            assert args.end_year == 2025

    def test_custom_input_file(self):
        """Test parsing with custom input file."""
        with patch.object(sys, "argv", ["prog", "--input-file", "custom_data.md"]):
            args = parse_arguments()
            assert args.input_file == "custom_data.md"

    def test_custom_output_file(self):
        """Test parsing with custom output file."""
        with patch.object(sys, "argv", ["prog", "--output-file", "custom_output"]):
            args = parse_arguments()
            assert args.output_file == "custom_output"

    def test_custom_alpha(self):
        """Test parsing with custom alpha value."""
        with patch.object(sys, "argv", ["prog", "--alpha", "0.4"]):
            args = parse_arguments()
            assert args.alpha == 0.4

    def test_custom_capital_output_ratio(self):
        """Test parsing with custom capital-output ratio."""
        with patch.object(sys, "argv", ["prog", "--capital-output-ratio", "2.5"]):
            args = parse_arguments()
            assert args.capital_output_ratio == 2.5

    def test_custom_end_year(self):
        """Test parsing with custom end year."""
        with patch.object(sys, "argv", ["prog", "--end-year", "2040"]):
            args = parse_arguments()
            assert args.end_year == 2040

    def test_all_custom_arguments(self):
        """Test parsing with all custom arguments."""
        with patch.object(
            sys,
            "argv",
            [
                "prog",
                "--input-file",
                "my_data.md",
                "--output-file",
                "my_output",
                "--alpha",
                "0.35",
                "--capital-output-ratio",
                "2.8",
                "--end-year",
                "2045",
            ],
        ):
            args = parse_arguments()

            assert args.input_file == "my_data.md"
            assert args.output_file == "my_output"
            assert args.alpha == 0.35
            assert args.capital_output_ratio == 2.8
            assert args.end_year == 2045

    def test_invalid_alpha_negative(self):
        """Test that negative alpha values are rejected with validation."""
        with patch.object(sys, "argv", ["prog", "--alpha", "-0.5"]):
            with pytest.raises(SystemExit) as exc_info:
                parse_arguments()
            assert exc_info.value.code == 1

    def test_invalid_alpha_too_large(self):
        """Test that alpha values greater than 1 are rejected with validation."""
        with patch.object(sys, "argv", ["prog", "--alpha", "1.5"]):
            with pytest.raises(SystemExit) as exc_info:
                parse_arguments()
            assert exc_info.value.code == 1

    def test_invalid_capital_output_ratio_negative(self):
        """Test that negative capital-output ratio is rejected with validation."""
        with patch.object(sys, "argv", ["prog", "--capital-output-ratio", "-1"]):
            with pytest.raises(SystemExit) as exc_info:
                parse_arguments()
            assert exc_info.value.code == 1

    def test_invalid_capital_output_ratio_zero(self):
        """Test that zero capital-output ratio is rejected with validation."""
        with patch.object(sys, "argv", ["prog", "--capital-output-ratio", "0"]):
            with pytest.raises(SystemExit) as exc_info:
                parse_arguments()
            assert exc_info.value.code == 1

    def test_invalid_end_year_too_early(self):
        """Test that end years before 2000 are rejected."""
        with patch.object(sys, "argv", ["prog", "--end-year", "1999"]):
            with pytest.raises(SystemExit) as exc_info:
                parse_arguments()
            assert exc_info.value.code == 1

    def test_invalid_end_year_too_late(self):
        """Test that end years too far in the future are rejected."""
        with patch.object(sys, "argv", ["prog", "--end-year", "3000"]):
            with pytest.raises(SystemExit) as exc_info:
                parse_arguments()
            assert exc_info.value.code == 1

    def test_invalid_end_year_type(self):
        """Test that non-integer end year is rejected."""
        with patch.object(sys, "argv", ["prog", "--end-year", "abc"]):
            with pytest.raises(SystemExit):
                parse_arguments()

    def test_help_option(self):
        """Test that help option exits cleanly."""
        with patch.object(sys, "argv", ["prog", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                parse_arguments()
            # Help should exit with code 0
            assert exc_info.value.code == 0

    def test_alpha_boundary_values(self):
        """Test alpha boundary values (0 and 1)."""
        # Alpha = 0 should be valid
        with patch.object(sys, "argv", ["prog", "--alpha", "0"]):
            args = parse_arguments()
            assert args.alpha == 0

        # Alpha = 1 should be valid
        with patch.object(sys, "argv", ["prog", "--alpha", "1"]):
            args = parse_arguments()
            assert args.alpha == 1

    def test_float_precision(self):
        """Test that float values maintain precision."""
        with patch.object(sys, "argv", ["prog", "--alpha", "0.333333"]):
            args = parse_arguments()
            assert abs(args.alpha - 0.333333) < 1e-6

    @pytest.mark.parametrize("year", [2020, 2030, 2100])
    def test_valid_end_years(self, year):
        """Test various valid end year values."""
        with patch.object(sys, "argv", ["prog", "--end-year", str(year)]):
            args = parse_arguments()
            assert args.end_year == year

    def test_short_option_forms(self):
        """Test if short option forms are supported."""
        # Test that -i short option works
        with patch.object(sys, "argv", ["prog", "-i", "input.md"]):
            args = parse_arguments()
            assert args.input_file == "input.md"

        # Test that -a short option works
        with patch.object(sys, "argv", ["prog", "-a", "0.4"]):
            args = parse_arguments()
            assert args.alpha == 0.4

        # Test that -o short option works
        with patch.object(sys, "argv", ["prog", "-o", "output"]):
            args = parse_arguments()
            assert args.output_file == "output"

        # Test that -k short option works
        with patch.object(sys, "argv", ["prog", "-k", "2.5"]):
            args = parse_arguments()
            assert args.capital_output_ratio == 2.5

