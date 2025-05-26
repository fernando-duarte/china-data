# Core Modules

This section documents the core modules of the China Economic Data Analysis package.

## Main Scripts

### Data Downloader

::: china_data_downloader
options:
show_root_heading: true
show_source: true
heading_level: 3

### Data Processor

::: china_data_processor
options:
show_root_heading: true
show_source: true
heading_level: 3

## Configuration

### Config Module

::: config
options:
show_root_heading: true
show_source: true
heading_level: 3
members: - Config - DataSourceConfig - ProcessingConfig - OutputConfig

## Usage Examples

### Basic Configuration

```python
from config import Config

# Initialize configuration
config = Config()

# Set economic parameters
config.set_alpha(0.33)  # Capital share in production function
config.set_capital_output_ratio(3.0)  # Steady-state capital-to-output ratio

# Get configuration values
alpha = config.get_alpha()
output_dir = config.get_output_directory()
```

### Running the Pipeline

```python
import subprocess
import sys

# Download latest data
result = subprocess.run([
    sys.executable, 'china_data_downloader.py',
    '--end-year', '2025'
], capture_output=True, text=True)

if result.returncode == 0:
    print("Data download completed successfully")
else:
    print(f"Download failed: {result.stderr}")

# Process the data
result = subprocess.run([
    sys.executable, 'china_data_processor.py',
    '--alpha', '0.33',
    '--capital-output-ratio', '3.0'
], capture_output=True, text=True)

if result.returncode == 0:
    print("Data processing completed successfully")
else:
    print(f"Processing failed: {result.stderr}")
```

### Custom Output Configuration

```python
from config import Config, OutputConfig

# Create custom output configuration
output_config = OutputConfig(
    base_filename="custom_china_data",
    output_directory="./custom_output",
    formats=["csv", "json", "markdown"]
)

# Apply configuration
config = Config()
config.set_output_config(output_config)
```

## Error Handling

The core modules implement comprehensive error handling:

```python
from utils.error_handling.exceptions import (
    DataDownloadError,
    DataProcessingError,
    ConfigurationError
)

try:
    # Your data processing code here
    pass
except DataDownloadError as e:
    print(f"Failed to download data: {e}")
except DataProcessingError as e:
    print(f"Failed to process data: {e}")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

## Performance Considerations

### Memory Usage

The package is designed to handle large datasets efficiently:

- **Streaming Processing**: Data is processed in chunks to minimize memory usage
- **Caching**: Intermediate results are cached to avoid redundant computations
- **Lazy Loading**: Data is loaded only when needed

### Execution Time

Typical execution times on a modern system:

| Operation         | Time          | Memory |
| ----------------- | ------------- | ------ |
| Data Download     | 30-60 seconds | ~50MB  |
| Data Processing   | 10-30 seconds | ~100MB |
| Output Generation | 5-10 seconds  | ~25MB  |

### Optimization Tips

```python
# Use caching for repeated runs
from utils.caching_utils import enable_caching
enable_caching(cache_dir=".cache")

# Process only required years
config.set_year_range(start_year=2000, end_year=2025)

# Use parallel processing for large datasets
config.set_parallel_processing(enabled=True, workers=4)
```
