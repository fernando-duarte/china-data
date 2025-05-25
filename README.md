# China Economic Data Analysis

This package contains scripts to download, process, and analyze economic data for China from multiple sources including the World Bank, Penn World Table, and IMF Fiscal Monitor. It provides tools for data retrieval, processing, analysis, and projection of economic indicators.

## Setup and Installation

### Prerequisites

- Python 3.7 or higher (Python 3.13+ recommended)
  - The script will work with either the `python3` or `python` command, as long as it's Python 3
- Internet connection (for downloading data)
- pip package manager

### Installation

1. Open Terminal
2. Navigate to the `china_data` directory
3. Run the setup script:
   ```bash
   ./setup.sh
   ```

The setup script will:
- Create a Python virtual environment (if not already in one)
- Install all required dependencies
- Run the data downloader and processor scripts
- Store output files in the `output` directory

> **Note:** The setup script can be run from inside an existing virtual environment or from outside. If run from inside an existing virtual environment, it will use that environment instead of creating a new one.

### Dependencies

The package relies on several Python libraries:
- pandas: Data manipulation and analysis
- pandas-datareader: Interface for extracting data from various web sources
- numpy: Numerical computing
- scikit-learn: Machine learning for linear regression in extrapolation methods
- statsmodels: Statistical models for ARIMA forecasting
- tabulate: Creating formatted tables
- jinja2: Template engine for markdown generation
- openpyxl: Excel file support
- requests: HTTP library for downloading data

Development dependencies include:
- pytest: Testing framework
- black: Code formatter
- isort: Import sorter
- flake8: Linting tool
- pylint: Advanced linting
- mypy: Type checking

### Setup Script Options

The setup script supports several command-line options:

```bash
./setup.sh --help
```

Options include:
- `--dev`: Install development dependencies and run tests after data scripts.
  
- `--test`: Install development dependencies and run tests only (skips data scripts).
  
- `-a=VALUE, --alpha=VALUE`: Capital share parameter for TFP calculation (default: 0.33).
  - This corresponds to the α parameter in the Cobb-Douglas production function.
  
- `-k=VALUE, --capital-output-ratio=VALUE`: Capital-to-output ratio for base year 2017 (default: 3.0).
  - For China, values between 2.5 and 3.5 are common in the literature.
  
- `-o=NAME, --output-file=NAME`: Base name for output files (default: china_data_processed).
  - Generated files will use this base name with extensions .md, .csv.
  
- `--end-year=YYYY`: Last year to process/download data for (default: 2025).
  - Code uses extrapolation methods to project data to the specified end year if actual data is not available.

Example:
```bash
./setup.sh -a=0.4 -k=2.5 -o=custom_output --end-year=2030
```

## Development Tools

### Using the Makefile

The project includes a Makefile for common development tasks:

```bash
make help          # Show available commands
make install       # Install production dependencies
make install-dev   # Install development dependencies
make format        # Format code with black and isort
make lint          # Run linting checks
make test          # Run tests
make clean         # Clean up generated files
make run-download  # Download raw data
make run-process   # Process downloaded data
```

### Code Quality

The project maintains high code quality standards:

- **Formatting**: Code is automatically formatted using `black` with a 120-character line limit
- **Import Organization**: Imports are sorted using `isort` with black-compatible settings
- **Linting**: Code is checked with `flake8` and `pylint` for style and potential issues
- **Type Checking**: Optional type checking with `mypy` for better code reliability
- **Testing**: Comprehensive test suite with pytest

Configuration files:
- `.flake8`: Linting rules and exclusions
- `pyproject.toml`: Configuration for black, isort, pytest, and mypy
- `config.py`: Centralized configuration for all project settings

### Configuration System

All project settings are centralized in `config.py`:

```python
from config import Config

# Access configuration values
alpha = Config.DEFAULT_ALPHA
output_dir = Config.get_output_directory()
column_map = Config.OUTPUT_COLUMN_MAP
```

This ensures:
- Single source of truth for all settings
- Easy modification of parameters
- Consistent behavior across modules
- No hardcoded values scattered throughout the codebase

## Manual Setup

If you prefer to set up manually:

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

   or

   ```bash
   python3 -m venv venv
   ```

2. Activate the virtual environment:
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```
     venv\Scripts\activate
     ```

3. Upgrade pip:
   ```bash
   pip install --upgrade pip
   ```

4. Install setuptools with distutils support:
   ```bash
   pip install setuptools>=67.0.0  # Required for pandas-datareader compatibility with Python 3.13+
   ```

5. Install dependencies (choose one option):

   For basic usage:
   ```bash
   pip install -r requirements.txt
   ```

   For development (includes testing tools):
   ```bash
   pip install -r dev-requirements.txt
   ```

6. Run the scripts:
   ```bash
   python china_data_downloader.py --end-year=2025
   python china_data_processor.py --end-year=2025
   ```

## Running Tests

There are several ways to run the automated tests:

### Using the Setup Script

1.  **Run tests as part of development setup**:
    This command will install development dependencies, run the data downloader and processor, and then execute the tests.
    ```bash
    ./setup.sh --dev
    ```

2.  **Run tests only**:
    This command will install development dependencies and then execute the tests, skipping the data downloader and processor scripts.
    ```bash
    ./setup.sh --test
    ```

### Using the Makefile

```bash
make test
```

### Manual Test Execution

If you prefer to run tests manually:

1.  Ensure you have activated the virtual environment:
    ```bash
    source venv/bin/activate
    ```
2.  Ensure development dependencies are installed:
    ```bash
    pip install -r dev-requirements.txt
    ```
3.  Navigate to the `china_data` directory (if not already there).
4.  Run pytest:
    ```bash
    python -m pytest
    ```
    Or simply:
    ```bash
    pytest
    ```
    Pytest will automatically discover and run tests in the `tests/` subdirectory.

### Test Coverage

The test suite includes:
- Unit tests for data downloading and processing functions
- Data integrity tests to verify:
  - Proper data structure and column presence
  - Consistency of calculated values
  - Valid value ranges for economic indicators
- Integration tests for the complete data pipeline

## Output Files

All output files are stored in the `output` directory after running the scripts:

- `china_data_raw.md`: Raw data in markdown format (generated by downloader)
  - Contains original data from World Bank WDI, IMF Fiscal Monitor, and Penn World Table
  - Includes source attribution and data descriptions
  - Records download dates for each data source

- `china_data_processed.md`: Processed data in markdown format (generated by processor)
  - Contains transformed and calculated economic variables
  - Includes detailed documentation on calculation methods
  - Specifies which years are extrapolated for each variable, and methods used

- `china_data_processed.csv`: Processed data in CSV format (generated by processor)
  - Contains the same data as the data table in the markdown file
  - Useful for importing into other analysis tools

## Data Sources

The package retrieves and processes data from the following sources:

### International Monetary Fund (IMF) Fiscal Monitor
  - Tax revenue data (replaces World Bank tax revenue data)
    - G1_S13_POGDP_PT: Tax revenue as percentage of GDP
  - Includes both historical data and official IMF projections through 2030
  - The IMF data is pre-downloaded and stored in the input directory

### World Bank World Development Indicators (WDI)
  - GDP and its components (consumption, government, investment, exports, imports)
    - NY.GDP.MKTP.CD: GDP (current US$)
    - NE.CON.PRVT.CD: Household consumption (current US$)
    - NE.CON.GOVT.CD: Government consumption (current US$)
    - NE.GDI.TOTL.CD: Gross capital formation (current US$)
    - NE.EXP.GNFS.CD: Exports (current US$)
    - NE.IMP.GNFS.CD: Imports (current US$)
  - Foreign Direct Investment (FDI)
    - BX.KLT.DINV.WD.GD.ZS: Foreign direct investment as percentage of GDP
  - Population and labor force data
    - SP.POP.TOTL: Population, total
    - SL.TLF.TOTL.IN: Labor force, total
  - Downloaded dynamically using pandas-datareader

### Penn World Table (PWT) version 10.01
  - Real GDP (rgdpo)
  - Capital stock (rkna) 
  - Price level (pl_gdpo)
  - Nominal GDP (cgdpo)
  - Human capital index (hc)
  - Downloaded programmatically during execution

## Data Processing Pipeline

The data processing pipeline consists of several stages:

1. **Data Download**: Retrieves data from multiple sources and merges them into a single dataset
2. **Unit Conversion**: Converts various units to standardized formats (billions USD, millions people)
3. **Capital Stock Calculation**: Calculates capital stock using investment data and capital-output ratio
4. **Human Capital Projection**: Projects human capital to future years using linear regression
5. **Data Extrapolation**: Extends base time series to end year using appropriate statistical methods:
   - ARIMA models for complex time series (TFP)
   - Linear regression for variables with clear trends
   - Average growth rate for stable growth variables
6. **Capital Stock Projection**: Projects capital stock using extrapolated investment data
7. **Economic Indicators**: Calculates derived indicators like:
   - Total Factor Productivity (TFP)
   - Net exports
   - Capital-output ratio
   - Tax revenue
   - Openness ratio (trade as % of GDP)
   - Total, private, and public savings
   - Saving rate
8. **Output Generation**: Formats results and generates output files

> **Note:** Extrapolation is performed before calculating economic indicators so that derived indicators can be calculated from already-extrapolated base variables. This approach ensures consistency in the projected data and eliminates the need to separately extrapolate derived economic indicators.

## Project Structure

```
china_data/
├── china_data_downloader.py    # Main script for downloading raw data
├── china_data_processor.py      # Main script for processing data
├── config.py                    # Centralized configuration
├── setup.sh                     # Setup and run script
├── Makefile                     # Development tasks automation
├── requirements.txt             # Python dependencies
├── dev-requirements.txt         # Development dependencies
├── .flake8                      # Linting configuration
├── pyproject.toml               # Tool configurations
├── input/                       # Pre-downloaded data files (IMF)
├── output/                      # Generated output files
├── tests/                       # Test suite
│   ├── test_downloader.py       # Tests for data downloading
│   ├── test_processor_*.py      # Tests for data processing modules
│   ├── test_dataframe_ops.py    # Tests for dataframe operations
│   ├── test_utils.py            # Tests for utility functions
│   └── data_integrity/          # Data integrity tests
│       ├── test_structure.py    # Tests for data structure
│       ├── test_consistency.py  # Tests for data consistency
│       └── test_value_ranges.py # Tests for value ranges
└── utils/                       # Utility modules
    ├── capital/                 # Capital stock calculations
    ├── data_sources/            # Data source handlers
    │   ├── wdi_downloader.py    # World Bank data downloader
    │   ├── pwt_downloader.py    # Penn World Table downloader
    │   └── imf_loader.py        # IMF data loader
    ├── extrapolation_methods/   # Extrapolation methods
    │   ├── arima.py             # ARIMA forecasting
    │   ├── linear_regression.py # Linear regression extrapolation
    │   └── average_growth_rate.py # Growth rate extrapolation
    ├── processor_dataframe/     # Dataframe operations
    │   ├── merge_operations.py  # Merging functions
    │   ├── metadata_operations.py # Metadata handling
    │   └── output_operations.py # Output formatting
    └── [various processor modules] # Processing utilities
```

## Code Quality Standards

The project follows strict code quality standards:

### File Organization
- No file exceeds 200 lines of code for maintainability
- Related functionality is grouped into modules
- Clear separation of concerns between modules

### Code Style
- Consistent formatting enforced by black
- Import organization managed by isort
- Comprehensive docstrings for all functions and classes
- Type hints where appropriate

### Best Practices
- Single source of truth for configuration
- No hardcoded values
- Comprehensive error handling
- Extensive logging for debugging
- Modular design for easy testing and maintenance

## Usage Examples

### Basic Data Processing

To download the latest data and process it with default parameters:

```bash
./setup.sh
```

This will create a complete dataset with projections using default parameters (α=0.33, capital-output ratio=3.0).

### Custom Parameter Analysis

To analyze the data with different economic assumptions:

```bash
./setup.sh -a=0.4 -k=3.5 --end-year=2030
```

This allows testing different theoretical assumptions about China's economy:
- Higher capital share (α=0.4) suggests capital contributes more to output growth
- Different capital-output ratio affects capital stock calculations
- Extended projection to 2030 provides longer-term forecasts

### Generating Data for Further Analysis

To produce data files for use in other analytical tools:

```bash
python china_data_downloader.py --end-year=2025
python china_data_processor.py -o china_data_for_analysis --end-year=2025
```

The resulting CSV file can be imported into statistical software, spreadsheets, or visualization tools for:
- Time series analysis
- Growth accounting
- Cross-country comparisons
- Custom visualizations

### Updating with New Data

When new data becomes available:

```bash
./setup.sh --dev
```

This will:
1. Download the latest available data from all sources
2. Process the updated dataset
3. Run tests to ensure calculations remain valid
4. Output updated files with the most recent projections

## Common Issues and Solutions

### Missing Data

If certain years have missing data:
- The processor attempts to fill gaps using appropriate statistical methods
- Check the extrapolation section in the processed markdown file for details on which methods were used
- For systematic gaps in specific variables, consider modifying the interpolation method in `utils/processor_extrapolation.py`

### API Limitations

If you encounter API rate limits:
- The downloader includes automatic retry mechanisms with exponential backoff
- Built-in delays between requests help prevent rate limiting
- You can manually re-run the downloader script if needed

### Python Version Compatibility

For Python 3.13+:
- The setup script ensures setuptools>=67.0.0 is installed first
- This provides distutils support required by pandas-datareader
- If you encounter import errors, ensure setuptools is properly installed

## License

This project is for educational purposes only. The code and documentation are provided "as is" without warranty of any kind, express or implied. Users are free to:

- Use the code for academic and research purposes
- Modify and distribute the code, provided proper attribution is given
- Contribute improvements via pull requests

When using this software for academic work, please cite:

```
Duarte, Fernando. China Economic Data Analysis Package (2025).
Brown University, Department of Economics.
```

### Data Source Licensing

This package retrieves and processes data from various sources, each with their own terms of use:

- **World Bank WDI**: Data is available under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/)
- **Penn World Table**: Academic use permitted with proper citation of [Feenstra, Robert C., Robert Inklaar and Marcel P. Timmer (2015)](https://www.rug.nl/ggdc/productivity/pwt/)
- **IMF Fiscal Monitor**: Data used according to the [IMF Terms and Conditions](https://www.imf.org/external/terms.htm)

Users should ensure they comply with the terms of use for each data source.
