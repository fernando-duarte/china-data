#!/usr/bin/env python3
"""Demonstration of structured logging features in China Data Processing.

This script shows how to use the structured logging capabilities for better
observability and monitoring of data processing operations.
"""

import sys
import time
from pathlib import Path

import pandas as pd

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# ruff: noqa: E402
from utils.logging_config import (
    LoggedOperation,
    get_logger,
    log_data_quality_issue,
    log_performance_metric,
    setup_structured_logging,
)


def demo_basic_structured_logging() -> None:
    """Demonstrate basic structured logging features."""
    logger = get_logger("demo")

    # Basic structured logging with context
    logger.info("Starting demonstration", demo_type="basic_logging")

    # Log with additional context
    logger.info("Processing data file", filename="demo_data.csv", file_size_mb=2.5, record_count=1000)

    # Log warnings with structured data
    logger.warning(
        "Data quality issue detected",
        issue_type="missing_values",
        column="GDP_USD_bn",
        missing_count=5,
        total_records=100,
    )

    # Log errors with context
    def _raise_validation_error() -> None:
        """Raise a validation error for demonstration."""
        error_msg = "Invalid data format"
        raise ValueError(error_msg)

    try:
        # Simulate an error
        _raise_validation_error()
    except ValueError as e:
        logger.exception(
            "Data processing failed",
            error_type=type(e).__name__,
            error_message=str(e),
            operation="data_validation",
        )


def demo_operation_logging() -> None:
    """Demonstrate operation logging with context managers."""
    logger = get_logger("demo")

    # Using LoggedOperation context manager for automatic timing
    with LoggedOperation(logger, "data_download", source="World Bank", indicator="GDP"):
        # Simulate some work
        time.sleep(0.1)
        logger.info("Downloaded data successfully", records_downloaded=500)

    # Nested operations
    with LoggedOperation(logger, "data_processing", input_file="raw_data.csv") as op_logger:
        with LoggedOperation(op_logger, "data_validation"):
            time.sleep(0.05)
            op_logger.info("Validation completed", validation_errors=0)

        with LoggedOperation(op_logger, "data_transformation"):
            time.sleep(0.05)
            op_logger.info("Transformation completed", output_columns=15)


def demo_data_quality_logging() -> None:
    """Demonstrate data quality issue logging."""
    logger = get_logger("demo")

    # Create sample data with issues
    sample_data = pd.DataFrame(
        {
            "year": [2020, 2021, 2022, 2023],
            "GDP_USD_bn": [14.7, None, 16.2, 17.1],  # Missing value
            "population": [1.4e9, 1.41e9, 1.42e9, 1.43e9],
        }
    )

    # Log data quality issues
    missing_gdp = sample_data["GDP_USD_bn"].isna().sum()
    if missing_gdp > 0:
        log_data_quality_issue(
            logger,
            issue_type="missing_data",
            description=f"Missing GDP data for {missing_gdp} years",
            data_source="World Bank",
            affected_records=missing_gdp,
            column="GDP_USD_bn",
            total_records=len(sample_data),
        )

    # Check for outliers
    gdp_values = sample_data["GDP_USD_bn"].dropna()
    mean_gdp = gdp_values.mean()
    std_gdp = gdp_values.std()
    outliers = gdp_values[(gdp_values > mean_gdp + 3 * std_gdp) | (gdp_values < mean_gdp - 3 * std_gdp)]

    if len(outliers) > 0:
        log_data_quality_issue(
            logger,
            issue_type="outlier_detected",
            description=f"Found {len(outliers)} GDP outliers",
            data_source="World Bank",
            affected_records=len(outliers),
            column="GDP_USD_bn",
            outlier_values=outliers.tolist(),
        )


def demo_performance_logging() -> None:
    """Demonstrate performance metric logging."""
    logger = get_logger("demo")

    # Simulate data processing with performance metrics
    start_time = time.time()

    # Simulate data loading
    time.sleep(0.1)
    load_time = time.time() - start_time
    log_performance_metric(logger, "data_load_time", load_time, "seconds", operation="data_loading", file_size_mb=10.5)

    # Simulate data processing
    process_start = time.time()
    time.sleep(0.2)
    process_time = time.time() - process_start
    log_performance_metric(
        logger, "data_process_time", process_time, "seconds", operation="data_processing", records_processed=1000
    )

    # Log memory usage (simulated)
    log_performance_metric(logger, "memory_usage", 125.7, "MB", operation="data_processing", peak_memory=True)


def demo_json_logging() -> None:
    """Demonstrate JSON format logging for production environments."""
    print("\n" + "=" * 60)
    print("JSON FORMAT LOGGING DEMO")
    print("=" * 60)

    # Set up JSON logging
    setup_structured_logging(log_level="INFO", enable_json=True, enable_console=True, include_process_info=True)

    logger = get_logger("json_demo")

    # Log some events in JSON format
    logger.info(
        "Data processing started",
        operation="china_data_processing",
        input_file="china_raw_data.csv",
        config_version="1.0",
        processing_mode="production",
    )

    logger.warning(
        "Data quality issue",
        issue_type="missing_data",
        column="FDI_pct_GDP",
        missing_years=[2020, 2021],
        impact="medium",
    )

    logger.info(
        "Processing completed",
        operation="china_data_processing",
        duration_seconds=45.2,
        output_file="china_processed_data.csv",
        records_processed=50,
        success=True,
    )


def main() -> None:
    """Run all structured logging demonstrations."""
    print("China Data Processing - Structured Logging Demonstration")
    print("=" * 60)

    # Set up structured logging with console output
    setup_structured_logging(
        log_level="INFO",
        enable_console=True,
        enable_json=False,  # Human-readable format for demo
        include_process_info=False,  # Cleaner output for demo
    )

    print("\n1. Basic Structured Logging")
    print("-" * 30)
    demo_basic_structured_logging()

    print("\n2. Operation Logging with Context Managers")
    print("-" * 45)
    demo_operation_logging()

    print("\n3. Data Quality Issue Logging")
    print("-" * 35)
    demo_data_quality_logging()

    print("\n4. Performance Metric Logging")
    print("-" * 35)
    demo_performance_logging()

    # Demonstrate JSON logging
    demo_json_logging()

    print("\n" + "=" * 60)
    print("Demonstration completed!")
    print("Check 'china_data.log' for file output.")
    print("=" * 60)


if __name__ == "__main__":
    main()
