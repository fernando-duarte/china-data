# Configuration

The China Economic Data Analysis package can be configured through environment variables and configuration files.

## Environment Variables

Create a `.env` file in the project root:

```bash
# Data Source Configuration
INCLUDE_WDI=true
INCLUDE_IMF=true
INCLUDE_PWT=true

# Output Configuration
GENERATE_CSV=true
GENERATE_EXCEL=true
GENERATE_MARKDOWN=true

# Processing Options
VALIDATE_DATA=true
CALCULATE_INDICATORS=true
USE_CACHE=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=china_data.log

# Performance
PARALLEL_PROCESSING=true
MAX_WORKERS=4
```

## Configuration Schema

The package uses Pydantic for configuration validation. See `config_schema.py` for the complete schema.

## Advanced Configuration

For more complex configurations, you can modify `config.py` directly or create custom configuration classes.

## Data Source Settings

### World Bank WDI

- Automatic retry on failures
- Configurable date ranges
- Custom indicator selection

### IMF Data

- API key configuration (if required)
- Regional data filtering
- Currency conversion options

### Penn World Table

- Version selection
- Variable subset configuration
- Data quality filters

## Output Customization

Configure output formats and destinations:

```python
OUTPUT_CONFIG = {
    "csv": {
        "enabled": True,
        "directory": "output/csv",
        "encoding": "utf-8"
    },
    "excel": {
        "enabled": True,
        "directory": "output/excel",
        "format": "xlsx"
    },
    "markdown": {
        "enabled": True,
        "directory": "output/reports",
        "template": "default"
    }
}
```
