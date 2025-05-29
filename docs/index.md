# China Economic Data Analysis

A comprehensive Python package for downloading, processing, and analyzing economic data for China.

## Overview

This package provides a robust pipeline for:

- **Data Collection**: Automated downloading from multiple economic data sources
- **Data Processing**: Standardized cleaning, transformation, and validation
- **Analysis Tools**: Built-in economic indicators and analytical functions
- **Output Generation**: Multiple output formats including CSV, Excel, and Markdown reports

## Key Features

- 🔄 **Automated Data Pipeline**: End-to-end data processing workflow
- 📊 **Multiple Data Sources**: Support for World Bank, IMF, PWT, and other sources
- 🧹 **Data Validation**: Comprehensive data integrity checks
- 📈 **Economic Indicators**: Built-in calculation of key economic metrics
- 🔧 **Extensible Architecture**: Easy to add new data sources and processors
- 📝 **Rich Documentation**: Comprehensive guides and API reference

## Quick Start

```bash
# Install the package
pip install china-data

# Download and process data
python china_data_downloader.py
python china_data_processor.py
```

## Project Structure

```text
china_data/
├── utils/                    # Core utilities and modules
│   ├── data_sources/        # Data source connectors
│   ├── economic_indicators/ # Economic calculation modules
│   └── processor_dataframe/ # Data processing utilities
├── input/                   # Raw data storage
├── output/                  # Processed data and reports
├── tests/                   # Comprehensive test suite
└── docs/                    # Documentation
```

## Getting Started

- [Installation Guide](getting-started/installation.md)
- [Quick Start Tutorial](getting-started/quickstart.md)
- [Configuration Options](getting-started/configuration.md)

## Documentation Sections

- **[User Guide](user-guide/data-sources.md)**: Comprehensive usage instructions
- **[API Reference](api/core.md)**: Detailed API documentation
- **[Development](development/contributing.md)**: Contributing and development guides
- **[ADRs](adrs/index.md)**: Architectural Decision Records

## Support

- **GitHub**: [fernandoduarte/china_data](https://github.com/fernandoduarte/china_data)
- **Email**: <fernando_duarte@brown.edu>
- **Issues**: [GitHub Issues](https://github.com/fernandoduarte/china_data/issues)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
