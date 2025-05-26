# Installation Guide

This guide will help you install and set up the China Economic Data Analysis package on your system.

## System Requirements

### Minimum Requirements

- **Python**: 3.9 or higher (Python 3.13+ recommended)
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Memory**: 2GB RAM minimum, 4GB recommended
- **Storage**: 500MB free space for package and data
- **Internet**: Required for downloading economic data

### Recommended Setup

- **Python**: 3.13 (latest stable version)
- **Memory**: 8GB RAM for large dataset processing
- **Storage**: 2GB free space for extended data history
- **Internet**: Stable broadband connection

## Installation Methods

### Method 1: Automated Setup (Recommended)

The easiest way to get started is using the automated setup script:

```bash
# Clone the repository
git clone https://github.com/fernandoduarte/china_data.git
cd china_data

# Run automated setup
./setup.sh
```

This will:

- Create a Python virtual environment
- Install all required dependencies
- Download and process the latest economic data
- Run data integrity tests
- Generate output files

!!! tip "Setup Options"

    The setup script supports several options:

    ```bash
    ./setup.sh --dev          # Include development tools
    ./setup.sh --test         # Run tests only (skip data processing)
    ./setup.sh --uv           # Use uv for faster dependency resolution
    ./setup.sh --help         # Show all available options
    ```

### Method 2: Manual Installation

For more control over the installation process:

=== "Using pip"

    ```bash
    # Clone repository
    git clone https://github.com/fernandoduarte/china_data.git
    cd china_data

    # Create virtual environment
    python -m venv venv

    # Activate virtual environment
    source venv/bin/activate  # On Windows: venv\Scripts\activate

    # Upgrade pip
    python -m pip install --upgrade pip

    # Install dependencies
    pip install -r requirements.txt

    # For development
    pip install -r dev-requirements.txt
    ```

=== "Using uv (Faster)"

    ```bash
    # Install uv if not already installed
    pip install uv

    # Clone repository
    git clone https://github.com/fernandoduarte/china_data.git
    cd china_data

    # Create virtual environment and install dependencies
    uv venv --python 3.9
    uv pip install -e .

    # For development
    uv pip install -e ".[dev]"
    ```

=== "Using Makefile"

    ```bash
    # Clone repository
    git clone https://github.com/fernandoduarte/china_data.git
    cd china_data

    # Create virtual environment manually
    python -m venv venv
    source venv/bin/activate

    # Install using Makefile
    make install          # Production dependencies
    make install-dev      # Development dependencies

    # Or with uv
    make install-uv       # Production with uv
    make install-dev-uv   # Development with uv
    ```

### Method 3: Docker Setup

For a containerized environment:

```bash
# Clone repository
git clone https://github.com/fernandoduarte/china_data.git
cd china_data

# Build and run with Docker Compose
docker compose build
docker compose run --rm dev

# Inside the container, run setup
./setup.sh
```

## Verification

After installation, verify everything is working:

### 1. Check Python Environment

```bash
# Verify Python version
python --version  # Should be 3.9+

# Check installed packages
pip list | grep -E "(pandas|numpy|requests)"
```

### 2. Test Data Download

```bash
# Test data download (quick test)
python china_data_downloader.py --end-year=2023
```

Expected output:

```
Starting China economic data download...
✓ World Bank data downloaded successfully
✓ Penn World Table data downloaded successfully
✓ IMF Fiscal Monitor data downloaded successfully
Download completed in X.X seconds
```

### 3. Test Data Processing

```bash
# Test data processing
python china_data_processor.py --end-year=2023
```

Expected output:

```
Starting China economic data processing...
✓ Data loaded and validated
✓ Economic indicators calculated
✓ Time series extrapolated
✓ Output files generated
Processing completed in X.X seconds
```

### 4. Run Tests

```bash
# Run the test suite
pytest tests/ -v
```

All tests should pass with output similar to:

```
tests/test_data_integrity.py::test_data_completeness PASSED
tests/test_processor.py::test_basic_processing PASSED
...
======================== X passed in X.X seconds ========================
```

## Troubleshooting

### Common Issues

#### Python Version Error

```
Error: Python 3.9+ required, found 3.8.x
```

**Solution**: Upgrade Python or use a different Python installation:

```bash
# Check available Python versions
python3.9 --version
python3.10 --version
python3.11 --version

# Use specific version
python3.9 -m venv venv
```

#### Permission Errors

```
Permission denied: './setup.sh'
```

**Solution**: Make the script executable:

```bash
chmod +x setup.sh
./setup.sh
```

#### Network/Download Errors

```
ConnectionError: Failed to download data from World Bank
```

**Solutions**:

1. **Check internet connection**
2. **Use cached data** (if available):

   ```bash
   python china_data_processor.py --use-cache
   ```

3. **Configure proxy** (if behind corporate firewall):

   ```bash
   export HTTP_PROXY=http://proxy.company.com:8080
   export HTTPS_PROXY=http://proxy.company.com:8080
   ```

#### Memory Errors

```
MemoryError: Unable to allocate array
```

**Solutions**:

1. **Reduce data range**:

   ```bash
   python china_data_downloader.py --start-year=2000 --end-year=2023
   ```

2. **Use data chunking**:

   ```bash
   python china_data_processor.py --chunk-size=1000
   ```

#### Dependency Conflicts

```
ERROR: pip's dependency resolver does not currently have a solution
```

**Solutions**:

1. **Use fresh virtual environment**:

   ```bash
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   ```

2. **Use uv for better dependency resolution**:

   ```bash
   pip install uv
   uv pip install -r requirements.txt
   ```

### Getting Help

If you encounter issues not covered here:

1. **Check the logs**: Look for detailed error messages in the console output
2. **Search existing issues**: Visit the [GitHub Issues](https://github.com/fernandoduarte/china_data/issues) page
3. **Create a new issue**: Include:
   - Your operating system and Python version
   - Complete error message
   - Steps to reproduce the problem
   - Output of `pip list` or `uv pip list`

## Next Steps

Once installation is complete:

1. **[Quick Start Guide](../getting-started/quickstart.md)** - Learn basic usage
2. **[Configuration](../getting-started/configuration.md)** - Customize settings
3. **[User Guide](../user-guide/data-sources.md)** - Detailed documentation
4. **[API Reference](../api/core.md)** - Technical documentation

## Development Installation

For contributors and developers:

```bash
# Clone with development setup
git clone https://github.com/fernandoduarte/china_data.git
cd china_data

# Install with development dependencies
./setup.sh --dev

# Install pre-commit hooks
pre-commit install

# Run full test suite
make test
make lint
make security-scan
```

See the [Development Guide](../development/contributing.md) for more details.
