#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Process command line arguments
DEV=false
TEST_ONLY=false
USE_UV=true  # Default to UV now
PROCESSOR_ARGS=""
END_YEAR=2025
for arg in "$@"; do
    case $arg in
        --dev) DEV=true;;
        --test) TEST_ONLY=true;;
        --no-uv) USE_UV=false;;  # Changed: UV is now default, use --no-uv to disable
        -a=*|--alpha=*) PROCESSOR_ARGS+=" -a ${arg#*=}";;
        -k=*|--capital-output-ratio=*) PROCESSOR_ARGS+=" -k ${arg#*=}";;
        -o=*|--output-file=*) PROCESSOR_ARGS+=" -o ${arg#*=}";;
        --end-year=*) END_YEAR="${arg#*=}";;
        --help) echo "Usage: ./setup.sh [--dev|--test|--no-uv] [-a=VAL] [-k=VAL] [-o=NAME] [--end-year=YYYY]"; exit 0;;
    esac
done

# Check for Python 3
if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
elif command -v python &>/dev/null; then
    PYTHON_CMD=python
else
    echo "Python 3 is required but not found"
    exit 1
fi

# Check Python version (require 3.10+ for our project)
python_version=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.10 or higher is required. Found: $python_version"
    exit 1
fi

# Create output directory
mkdir -p output

# Check if uv is available
if $USE_UV && command -v uv &>/dev/null; then
    echo "Using UV for dependency management..."

    # Install dependencies with uv sync
    if $DEV || $TEST_ONLY; then
        echo "Installing all dependencies (including dev)..."
        uv sync
    else
        echo "Installing production dependencies only..."
        uv sync --no-dev
    fi

    # Use uv run for all commands
    PYTHON_CMD="uv run python"

elif $USE_UV; then
    echo "UV not found. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"

    # Retry with newly installed UV
    if $DEV || $TEST_ONLY; then
        uv sync
    else
        uv sync --no-dev
    fi
    PYTHON_CMD="uv run python"

else
    echo "Using traditional pip installation (not recommended)..."

    # Create and activate virtual environment
    ALREADY_IN_VENV=false
    if [ -z "$VIRTUAL_ENV" ]; then
        $PYTHON_CMD -m venv .venv
        source .venv/bin/activate
        ALREADY_IN_VENV=false
    else
        ALREADY_IN_VENV=true
    fi

    # Install dependencies with pip
    $PYTHON_CMD -m pip install --upgrade pip >/dev/null

    if $DEV || $TEST_ONLY; then
        $PYTHON_CMD -m pip install -e ".[dev]"
    else
        $PYTHON_CMD -m pip install -e .
    fi
fi

run_tests(){
    if $USE_UV; then
        echo "Running tests with UV..."
        uv run pytest tests
    else
        (export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"; $PYTHON_CMD -m pytest tests)
    fi
}

if $TEST_ONLY; then
    run_tests
    exit 0
fi

# Set up Python path to include the current directory (for non-UV runs)
if ! $USE_UV; then
    export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"
fi

# Run the scripts
echo "Downloading data..."
$PYTHON_CMD china_data_downloader.py --end-year=$END_YEAR

echo "Processing data..."
$PYTHON_CMD china_data_processor.py $PROCESSOR_ARGS --end-year=$END_YEAR

if $DEV; then run_tests; fi

if ! $USE_UV && ! $ALREADY_IN_VENV; then deactivate; fi

echo "Setup complete!"
