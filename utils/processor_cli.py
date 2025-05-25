"""Command-line interface for China data processor with input validation.

This module provides argument parsing and validation for the China economic data processor.
All input parameters are validated to ensure they are within reasonable ranges:
- Alpha (capital share): 0 ≤ α ≤ 1
- Capital-output ratio: > 0
- End year: 2000 ≤ year ≤ current_year + 100
"""

import argparse
import sys
from datetime import datetime
from typing import Any


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
    current_year = datetime.now().year
    min_year = 2000  # Reasonable minimum for economic data
    max_year = current_year + 100  # Reasonable maximum for projections
    
    if args.end_year < min_year or args.end_year > max_year:
        errors.append(f"End year must be between {min_year} and {max_year}, got {args.end_year}")
    
    # If there are validation errors, print them and exit
    if errors:
        print("Input validation errors:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)


def parse_arguments() -> Any:
    parser = argparse.ArgumentParser(description="Process China economic data")
    parser.add_argument("-i", "--input-file", default="china_data_raw.md", help="Input file name")
    parser.add_argument("-a", "--alpha", type=float, default=1 / 3, help="Capital share parameter (0-1)")
    parser.add_argument("-o", "--output-file", default="china_data_processed", help="Base name for output files")
    parser.add_argument(
        "-k", "--capital-output-ratio", type=float, default=3.0, help="Capital-to-output ratio for base year (2017) (must be positive)"
    )
    parser.add_argument("--end-year", type=int, default=2025, help="Last year to extrapolate/process (default: 2025)")
    
    args = parser.parse_args()
    validate_arguments(args)
    return args
