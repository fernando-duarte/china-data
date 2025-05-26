"""Command-line interface for China data processor with input validation.

This module provides argument parsing and validation for the China economic data processor.
All input parameters are validated to ensure they are within reasonable ranges:
- Alpha (capital share): 0 ≤ a ≤ 1
- Capital-output ratio: > 0
- End year: 2000 ≤ year ≤ current_year + 100
"""

import argparse
import logging
import sys
from datetime import datetime, timezone
from typing import Any

from utils.validation_utils import validate_alpha, validate_capital_output_ratio, validate_end_year

logger = logging.getLogger(__name__)


def validate_arguments(args: Any) -> None:
    """Validate CLI arguments and raise SystemExit with error message if invalid.

    Args:
        args: Parsed arguments from argparse

    Raises:
        SystemExit: If any argument is invalid
    """
    errors = []

    # Validate alpha parameter (capital share)
    if args.alpha < 0 or args.alpha > 1:
        errors.append(f"Alpha parameter must be between 0 and 1, got {args.alpha}")

    # Validate capital-output ratio (must be positive)
    if args.capital_output_ratio <= 0:
        errors.append(f"Capital-output ratio must be positive, got {args.capital_output_ratio}")

    # Validate end year (reasonable range)
    current_year = datetime.now(tz=timezone.utc).year
    min_year = 2000  # Reasonable minimum for economic data
    max_year = current_year + 100  # Reasonable maximum for projections

    if args.end_year < min_year or args.end_year > max_year:
        errors.append(f"End year must be between {min_year} and {max_year}, got {args.end_year}")

    # If there are validation errors, log them and exit
    if errors:
        logger.error("Input validation errors:")
        for error in errors:
            logger.error("  - %s", error)
        sys.exit(1)


def parse_and_validate_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse and validate command line arguments."""
    parser = argparse.ArgumentParser(description="Process China economic data")

    parser.add_argument(
        "-i", "--input-file", type=str, default="china_data_raw.md", help="Input markdown file containing raw data"
    )

    parser.add_argument(
        "-o", "--output-file", type=str, default="china_data_processed", help="Base name for output files"
    )

    parser.add_argument("-a", "--alpha", type=float, default=0.33, help="Capital share parameter (0-1)")

    parser.add_argument(
        "-k",
        "--capital-output-ratio",
        type=float,
        default=3.0,
        help="Capital-to-output ratio for base year (must be positive)",
    )

    parser.add_argument("--end-year", type=int, default=2025, help="Last year to extrapolate/process (default: 2025)")

    parsed_args = parser.parse_args(args)

    # Validate arguments
    errors = []

    if not validate_alpha(parsed_args.alpha):
        errors.append(f"Alpha parameter must be between 0 and 1, got {parsed_args.alpha}")

    if not validate_capital_output_ratio(parsed_args.capital_output_ratio):
        errors.append(f"Capital-output ratio must be positive, got {parsed_args.capital_output_ratio}")

    if not validate_end_year(parsed_args.end_year):
        errors.append(f"End year must be between 2020 and 2100, got {parsed_args.end_year}")

    if errors:
        logger.error("Input validation errors:")
        for error in errors:
            logger.error("  - %s", error)
        raise ValueError("\n".join(errors))

    return parsed_args
