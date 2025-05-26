import sys
from unittest.mock import patch

import pytest

from utils.processor_cli import parse_and_validate_args


class TestProcessorCLIValidation:
    def test_multiple_validation_errors(self):
        """Test that multiple validation errors are reported together."""
        with patch.object(
            sys,
            "argv",
            [
                "prog",
                "--alpha",
                "-0.5",
                "--capital-output-ratio",
                "-1",
                "--end-year",
                "1999",
            ],
        ):
            with pytest.raises(ValueError) as exc_info:
                parse_and_validate_args(
                    ["--alpha", "-0.5", "--capital-output-ratio", "-1", "--end-year", "1999"]
                )
            assert "Alpha parameter" in str(exc_info.value)

    def test_validation_error_messages(self, caplog):
        """Test that validation error messages are logged."""
        with patch.object(sys, "argv", ["prog", "--alpha", "1.5"]):
            with pytest.raises(ValueError):
                parse_and_validate_args(["--alpha", "1.5"])

        messages = "".join(record.message for record in caplog.records)
        assert "Input validation errors:" in messages
        assert "Alpha parameter must be between 0 and 1" in messages
