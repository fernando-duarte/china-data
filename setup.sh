#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Process command line arguments
DEV=false
TEST_ONLY=false
PROCESSOR_ARGS=""
END_YEAR=2025
for arg in "$@"; do
    case $arg in
        --dev) DEV=true;;
        --test) TEST_ONLY=true;;
        -a=*|--alpha=*) PROCESSOR_ARGS+=" -a ${arg#*=}";;
        -k=*|--capital-output-ratio=*) PROCESSOR_ARGS+=" -k ${arg#*=}";;
        -o=*|--output-file=*) PROCESSOR_ARGS+=" -o ${arg#*=}";;
        --end-year=*) END_YEAR="${arg#*=}";;
        --help) echo "Usage: ./setup.sh [--dev|--test] [-a=VAL] [-k=VAL] [-o=NAME] [--end-year=YYYY]"; exit 0;;
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

# Create output directory
mkdir -p output

# Create and activate virtual environment
ALREADY_IN_VENV=false
if [ -z "$VIRTUAL_ENV" ]; then
    $PYTHON_CMD -m venv venv
    source venv/bin/activate
    ALREADY_IN_VENV=false
else
    ALREADY_IN_VENV=true
fi

# Install dependencies
$PYTHON_CMD -m pip install --upgrade pip >/dev/null
$PYTHON_CMD -m pip install 'setuptools>=67.0.0' >/dev/null
if $DEV || $TEST_ONLY; then
    $PYTHON_CMD -m pip install -r dev-requirements.txt
else
    $PYTHON_CMD -m pip install -r requirements.txt
fi

run_tests(){
    (export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"; $PYTHON_CMD -m pytest tests)
}

if $TEST_ONLY; then
    run_tests
    exit 0
fi

# Set up Python path to include the current directory
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Run the scripts
$PYTHON_CMD china_data_downloader.py --end-year=$END_YEAR
$PYTHON_CMD china_data_processor.py $PROCESSOR_ARGS --end-year=$END_YEAR

if $DEV; then run_tests; fi

if ! $ALREADY_IN_VENV; then deactivate; fi
