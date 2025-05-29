# Installation

## Requirements

- Python 3.10 or higher
- pip or uv package manager

## Installation Methods

### Using UV (Recommended)

UV is a fast Python package manager that provides better dependency resolution and faster installs.

```bash
# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install the package
uv pip install china-data

# For development
uv pip install china-data[dev]
```

### Using pip

```bash
# Install the package
pip install china-data

# For development
pip install china-data[dev]
```

### From Source

```bash
# Clone the repository
git clone https://github.com/fernandoduarte/china_data.git
cd china_data

# Install with UV (recommended)
uv sync

# Or with pip
pip install -e .
```

## Development Setup

For development work, use the provided Makefile:

```bash
# One-command setup (installs UV if needed)
make setup

# Start development mode
make dev
```

## Verification

Verify your installation:

```python
import china_data_downloader
import china_data_processor
print("Installation successful!")
```

## Troubleshooting

### Common Issues

1. **Python Version**: Ensure you're using Python 3.10+
2. **Dependencies**: Some packages require system libraries (e.g., for Excel support)
3. **Permissions**: Use virtual environments to avoid permission issues

### Getting Help

- Check the [GitHub Issues](https://github.com/fernandoduarte/china_data/issues)
- Contact: <fernando_duarte@brown.edu>
