# Quick Start

This guide will get you up and running with the China Economic Data Analysis package in minutes.

## Basic Usage

### 1. Download Data

```bash
python china_data_downloader.py
```

This will download economic data from various sources including:

- World Bank World Development Indicators (WDI)
- International Monetary Fund (IMF)
- Penn World Table (PWT)

### 2. Process Data

```bash
python china_data_processor.py
```

This will:

- Clean and standardize the downloaded data
- Calculate economic indicators
- Generate output files in multiple formats

### 3. View Results

Check the `output/` directory for:

- CSV files with processed data
- Excel workbooks with formatted tables
- Markdown reports with analysis

## Configuration

Create a `.env` file to customize behavior:

```bash
# Data sources to include
INCLUDE_WDI=true
INCLUDE_IMF=true
INCLUDE_PWT=true

# Output formats
GENERATE_CSV=true
GENERATE_EXCEL=true
GENERATE_MARKDOWN=true

# Processing options
VALIDATE_DATA=true
CALCULATE_INDICATORS=true
```

## Python API

You can also use the package programmatically:

```python
from china_data_downloader import download_all_data
from china_data_processor import process_all_data

# Download data
download_all_data()

# Process data
results = process_all_data()

# Access processed data
print(f"Processed {len(results)} datasets")
```

## Next Steps

- [Learn about data sources](../user-guide/data-sources.md)
- [Understand the processing pipeline](../user-guide/processing-pipeline.md)
- [Explore output formats](../user-guide/output-formats.md)
- [Customize for your needs](../user-guide/customization.md)
