# Core API Reference

This section documents the core modules and functions of the China Economic Data Analysis package.

## Main Modules

### china_data_downloader

::: china_data_downloader
options:
show_source: true
show_root_heading: true
show_root_toc_entry: true

### china_data_processor

::: china_data_processor
options:
show_source: true
show_root_heading: true
show_root_toc_entry: true

## Configuration

### config

::: config
options:
show_source: true
show_root_heading: true
show_root_toc_entry: true

### config_schema

::: config_schema
options:
show_source: true
show_root_heading: true
show_root_toc_entry: true

## Core Functions

### Data Download

```python
from china_data_downloader import download_all_data, download_wdi_data

# Download all data sources
download_all_data()

# Download specific source
download_wdi_data()
```

### Data Processing

```python
from china_data_processor import process_all_data, generate_reports

# Process downloaded data
results = process_all_data()

# Generate reports
generate_reports(results)
```

### Configuration Management

```python
from config import get_config, update_config

# Get current configuration
config = get_config()

# Update configuration
update_config({"INCLUDE_WDI": True})
```

## Error Handling

The package uses structured error handling:

```python
from utils.error_handling import DataSourceError, ProcessingError

try:
    download_all_data()
except DataSourceError as e:
    print(f"Data source error: {e}")
except ProcessingError as e:
    print(f"Processing error: {e}")
```

## Logging

Structured logging is available throughout:

```python
import structlog

logger = structlog.get_logger()
logger.info("Starting data download", source="WDI")
```
