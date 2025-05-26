# China Economic Data Analysis

[![CI](https://github.com/fernandoduarte/china_data/workflows/CI/badge.svg)](https://github.com/fernandoduarte/china_data/actions/workflows/ci.yml)
[![Performance Tests](https://github.com/fernandoduarte/china_data/workflows/Performance%20Testing/badge.svg)](https://github.com/fernandoduarte/china_data/actions/workflows/performance.yml)
[![Dependency Check](https://github.com/fernandoduarte/china_data/workflows/Dependency%20Management/badge.svg)](https://github.com/fernandoduarte/china_data/actions/workflows/dependency-check.yml)
[![codecov](https://codecov.io/gh/fernandoduarte/china_data/branch/main/graph/badge.svg)](https://codecov.io/gh/fernandoduarte/china_data)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Python package for downloading, processing, and analyzing economic data for China from the World Bank,
Penn World Table, and IMF Fiscal Monitor. Includes automated data retrieval, processing pipelines,
statistical extrapolation, and CI/CD workflows.

## Quick Start

### Prerequisites

- Python 3.9+ (Python 3.13+ recommended)
- Internet connection (for downloading data)
- pip package manager

### Installation

1. **Clone and navigate to the repository:**

   ```bash
   git clone https://github.com/fernandoduarte/china_data.git
   cd china_data
   ```

2. **Run the setup script:**

   ```bash
   ./setup.sh
   ```

The setup script will:

- Create a Python virtual environment
- Install all required dependencies
- Download and process the latest economic data
- Generate output files in the `output` directory
- Run data integrity tests

### Data Releases (Public Access)

For the just the processed data without running the pipeline:

**Latest Data-Only Release:** [Download china-data-only-v1.0.0.zip](https://github.com/fernandoduarte/china_data/releases/latest)

---

## Setup and Installation

### Automated Setup (Recommended)

```bash
# Clone repository
git clone https://github.com/fernandoduarte/china_data.git
cd china_data

# Basic setup - data processing only
./setup.sh

# Development setup - includes testing tools
./setup.sh --dev

# Testing only - skip data processing
./setup.sh --test

# Use uv for faster dependency resolution (requires: pip install uv)
./setup.sh --uv --dev
```

### Dependency Management Options

This project supports both traditional pip and modern uv for dependency management:

**Using pip (traditional):**

```bash
make install      # Production dependencies
make install-dev  # Development dependencies
```

**Using uv (faster, recommended):**

```bash
make install-uv      # Production dependencies with uv
make install-dev-uv  # Development dependencies with uv
```

**Security scanning:**

```bash
make security-scan   # Run vulnerability scan on dependencies
```

### Setup Options

```bash
./setup.sh --help
```

**Available options:**

- `--dev`: Install development dependencies and run tests
- `--test`: Install development dependencies and run tests only (skip data processing)
- `-a=VALUE, --alpha=VALUE`: Capital share parameter (default: 0.33)
- `-k=VALUE, --capital-output-ratio=VALUE`: Capital-to-output ratio (default: 3.0)
- `-o=NAME, --output-file=NAME`: Base name for output files (default: china_data_processed)
- `--end-year=YYYY`: Last year to process/download data (default: 2025)

**Example with custom parameters:**

```bash
./setup.sh -a=0.4 -k=2.5 -o=custom_output --end-year=2030 --dev
```

### Development with VS Code Dev Containers (Recommended)

For the best development experience, use the VS Code Dev Container:

1. **Prerequisites:**

   - [VS Code](https://code.visualstudio.com/) with [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
   - [Docker Desktop](https://www.docker.com/products/docker-desktop/)

2. **Open in container:**

   ```bash
   code .
   # VS Code will prompt to "Reopen in Container"
   # Or use Command Palette: "Dev Containers: Reopen in Container"
   ```

3. **Automatic setup:** The container includes:
   - Python 3.11 with all dependencies
   - Pre-configured VS Code extensions for Python, Jupyter, and data science
   - Jupyter Lab server (port 8888)
   - MkDocs documentation server (port 8000)
   - All development tools (Black, Ruff, MyPy, pytest)

See [`.devcontainer/README.md`](.devcontainer/README.md) for detailed setup instructions.

### Development with Docker Compose

```bash
docker compose build
docker compose run --rm dev
```

This opens a shell inside a container with all dependencies installed. The repository is mounted at `/app`,
so you can run `make test` or `./setup.sh` as usual.

### Manual Setup

<details>
<summary>Click to expand manual setup instructions</summary>

1. **Create virtual environment:**

   ```bash
   python -m venv venv
   # or: python3 -m venv venv
   ```

2. **Activate virtual environment:**

   ```bash
   # macOS/Linux:
   source venv/bin/activate

   # Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install --upgrade pip
   pip install setuptools>=67.0.0  # Required for Python 3.13+

   # Production dependencies:
   pip install -r requirements.txt

   # Development dependencies:
   pip install -r dev-requirements.txt
   ```

4. **Run the pipeline:**

   ```bash
   python china_data_downloader.py --end-year=2025
   python china_data_processor.py --end-year=2025
   ```

   </details>

### Configuration System

All project settings are centralized in `config.py`:

```python
from config import Config

# Access configuration values
alpha = Config.DEFAULT_ALPHA
output_dir = Config.get_output_directory()
column_map = Config.OUTPUT_COLUMN_MAP
```

---

### Citation Guidelines

If you use the provided data, please cite original data sources:

1. World Bank WDI: Available under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
2. Penn World Table: [Feenstra, Inklaar & Timmer (2015)](https://www.rug.nl/ggdc/productivity/pwt/)
3. IMF Fiscal Monitor: Per [IMF Terms](https://www.imf.org/external/terms.htm)

---

## Output Files

All processed data is stored in the `output/` directory:

### Generated Files

- `china_data_raw.md` - Raw data with source attribution and download dates
- `china_data_processed.md` - Processed data with calculation methodology and extrapolation details
- `china_data_processed.csv` - Machine-readable CSV format for analysis tools

### Data Content

---

## License

MIT License - See LICENSE file for details.

Academic Use: This project is for educational and research purposes. Use, modify, and distribute with attribution.

Data Licensing: Users must comply with original data source terms:

- World Bank WDI: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- Penn World Table: Academic use with proper citation
- IMF Fiscal Monitor: Per [IMF Terms](https://www.imf.org/external/terms.htm)
