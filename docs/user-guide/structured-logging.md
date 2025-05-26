# Structured Logging Guide

The China Data Processing project uses [structlog](https://www.structlog.org/) for structured logging, providing
better observability, debugging capabilities, and monitoring support.

## Overview

Structured logging captures log events as structured data rather than plain text, making logs more searchable,
analyzable, and suitable for modern log aggregation systems.

### Key Features

- **Structured Data**: Log events include contextual information as key-value pairs
- **Automatic Context**: Module, function, and line number information added automatically
- **Multiple Formats**: Support for both human-readable console output and JSON format
- **Operation Tracking**: Built-in support for tracking operations with timing
- **Data Quality Monitoring**: Specialized logging for data quality issues
- **Performance Metrics**: Structured performance metric logging
- **Backward Compatibility**: Works alongside existing standard logging

## Quick Start

### Basic Usage

```python
from utils.logging_config import setup_structured_logging, get_logger

# Set up structured logging
setup_structured_logging(
    log_level="INFO",
    enable_console=True,
    enable_json=False  # Human-readable format
)

# Get a logger
logger = get_logger("my_module")

# Log with structured data
logger.info(
    "Processing data file",
    filename="data.csv",
    file_size_mb=2.5,
    record_count=1000
)
```

### Configuration Options

The structured logging system can be configured through `config.py`:

```python
# Structured logging configuration
STRUCTURED_LOGGING_ENABLED = True
STRUCTURED_LOGGING_LEVEL = "INFO"
STRUCTURED_LOGGING_JSON_FORMAT = False  # Set to True for production
STRUCTURED_LOGGING_INCLUDE_PROCESS_INFO = True
STRUCTURED_LOGGING_FILE = "china_data.log"
```

## Advanced Features

### Operation Logging

Track operations with automatic timing using the `LoggedOperation` context manager:

```python
from utils.logging_config import LoggedOperation, get_logger

logger = get_logger("data_processor")

with LoggedOperation(logger, "data_download", source="World Bank", indicator="GDP"):
    # Your operation code here
    download_data()
    logger.info("Downloaded successfully", records=500)
# Automatically logs start, duration, and completion/failure
```

### Data Quality Issue Logging

Log data quality issues with structured context:

```python
from utils.logging_config import log_data_quality_issue, get_logger

logger = get_logger("validator")

log_data_quality_issue(
    logger,
    issue_type="missing_data",
    description="Missing GDP data for 3 years",
    data_source="World Bank",
    affected_records=3,
    column="GDP_USD_bn",
    total_records=50
)
```

### Performance Metric Logging

Log performance metrics with structured data:

```python
from utils.logging_config import log_performance_metric, get_logger

logger = get_logger("processor")

log_performance_metric(
    logger,
    "data_processing_time",
    45.2,
    "seconds",
    operation="data_transformation",
    records_processed=1000
)
```

## Output Formats

### Human-Readable Format (Development)

```text
2025-05-26 06:40:59 [INFO] Processing data file filename=data.csv file_size_mb=2.5 record_count=1000
```

### JSON Format (Production)

```json
{
  "event": "Processing data file",
  "filename": "data.csv",
  "file_size_mb": 2.5,
  "record_count": 1000,
  "timestamp": "2025-05-26 06:40:59",
  "level": "INFO",
  "module": "data_processor",
  "function": "process_file",
  "line": 42,
  "pid": 12345
}
```

## Configuration Examples

### Development Setup

```python
from utils.logging_config import setup_structured_logging

setup_structured_logging(
    log_level="DEBUG",
    enable_console=True,
    enable_json=False,
    include_process_info=False  # Cleaner output for development
)
```

### Production Setup

```python
from utils.logging_config import setup_structured_logging

setup_structured_logging(
    log_level="INFO",
    log_file="/var/log/china_data.log",
    enable_console=False,
    enable_json=True,  # JSON format for log aggregation
    include_process_info=True
)
```

### Hybrid Setup (Console + File)

```python
from utils.logging_config import setup_structured_logging

setup_structured_logging(
    log_level="INFO",
    log_file="china_data.log",
    enable_console=True,
    enable_json=False,  # Human-readable console, structured file
    include_process_info=True
)
```

## Integration with Existing Code

The structured logging system is designed to work alongside existing standard logging:

```python
import logging
from utils.logging_config import get_logger

# Standard logging still works
standard_logger = logging.getLogger("legacy_module")
standard_logger.info("Legacy log message")

# Structured logging provides enhanced features
struct_logger = get_logger("new_module")
struct_logger.info("Enhanced log message", context="additional_data")
```

## Error Handling Integration

The error handling decorators automatically use structured logging when available:

```python
from utils.error_handling.decorators import handle_data_operation

@handle_data_operation("data_processing")
def process_data(data):
    # Function implementation
    pass
```

When structured logging is enabled, errors are logged with rich context:

```json
{
  "event": "Error in data_processing",
  "operation": "data_processing",
  "function": "process_data",
  "error_type": "ValueError",
  "error_message": "Invalid data format",
  "level": "ERROR",
  "timestamp": "2025-05-26 06:40:59"
}
```

## Best Practices

### 1. Use Meaningful Event Messages

```python
# Good
logger.info("Data validation completed", errors=0, warnings=2, records=1000)

# Avoid
logger.info("Done", result="ok")
```

### 2. Include Relevant Context

```python
# Good
logger.error(
    "Failed to download data",
    source="World Bank",
    indicator="GDP",
    error_code=404,
    retry_count=3
)

# Avoid
logger.error("Download failed")
```

### 3. Use Appropriate Log Levels

- `DEBUG`: Detailed diagnostic information
- `INFO`: General operational information
- `WARNING`: Something unexpected happened but processing continues
- `ERROR`: A serious problem occurred
- `CRITICAL`: A very serious error occurred

### 4. Structure Your Context Data

```python
# Good - structured context
logger.info(
    "Processing completed",
    input_file="data.csv",
    output_file="processed.csv",
    duration_seconds=45.2,
    records_processed=1000,
    success=True
)

# Avoid - unstructured context
logger.info("Processing completed: data.csv -> processed.csv in 45.2s (1000 records)")
```

## Monitoring and Alerting

The structured logging format makes it easy to set up monitoring and alerting:

### Log Aggregation

JSON format logs can be easily ingested by log aggregation systems like:

- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Splunk**
- **Fluentd**
- **Grafana Loki**

### Example Queries

With structured logs, you can easily query for:

```bash
# Find all data quality issues
level:WARNING AND issue_type:*

# Find slow operations
duration_seconds:>30

# Find errors by module
level:ERROR AND module:data_processor

# Monitor performance metrics
metric_name:data_processing_time
```

## Troubleshooting

### Common Issues

1. **Logs not appearing in file**: Ensure handlers are flushed and file permissions are correct
2. **JSON format not working**: Check that `enable_json=True` is set
3. **Missing context information**: Verify that structured logging is properly initialized

### Debug Mode

Enable debug logging to see detailed information:

```python
setup_structured_logging(log_level="DEBUG")
```

### Testing Structured Logging

Run the demonstration script to see structured logging in action:

```bash
python examples/structured_logging_demo.py
```

## Migration from Standard Logging

Existing code using standard logging will continue to work. To migrate:

1. Replace `logging.getLogger()` with `get_logger()` from `utils.logging_config`
2. Add structured context to log calls
3. Use specialized logging functions for operations, data quality, and performance
4. Update log analysis tools to handle structured format

The migration can be done gradually, with both logging styles coexisting during the transition.
