import sys
from unittest.mock import patch

import pytest

from utils.processor_cli import parse_arguments


class TestProcessorCLIValidation:
    def test_multiple_validation_errors(self):
        """Test that multiple validation errors are reported together."""
        with patch.object(
            sys, "argv", ["prog", "--alpha", "-0.5", "--capital-output-ratio", "-1", "--end-year", "1999"]
        ):
            with pytest.raises(SystemExit) as exc_info:
                parse_arguments()
            assert exc_info.value.code == 1

    def test_validation_error_messages(self, capsys):
        """Test that validation error messages are informative."""
        with patch.object(sys, "argv", ["prog", "--alpha", "1.5"]):
            with pytest.raises(SystemExit):
                parse_arguments()

            captured = capsys.readouterr()
            assert "Input validation errors:" in captured.err
            assert "Alpha parameter must be between 0 and 1" in captured.err
