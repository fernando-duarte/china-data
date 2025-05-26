.PHONY: help install install-dev install-uv install-dev-uv format lint test test-property test-mutation test-factories test-benchmark test-parallel test-integration test-all clean run-download run-process security-scan

# Default target
help:
	@echo "Available commands:"
	@echo "  make install       - Install production dependencies (UV)"
	@echo "  make install-dev   - Install development dependencies (UV)"
	@echo "  make install-pip   - Install production dependencies (legacy pip)"
	@echo "  make install-dev-pip - Install development dependencies (legacy pip)"
	@echo "  make format        - Format code with black and isort"
	@echo "  make lint          - Run linting checks"
	@echo "  make test          - Run standard tests"
	@echo "  make test-property - Run property-based tests with Hypothesis"
	@echo "  make test-mutation - Run mutation tests with mutmut (enhanced)"
	@echo "  make test-factories - Run factory demonstration tests"
	@echo "  make test-benchmark - Run performance benchmark tests"
	@echo "  make test-parallel - Run tests in parallel with pytest-xdist"
	@echo "  make test-integration - Run integration tests with factory fixtures"
	@echo "  make test-all      - Run all types of tests"
	@echo "  make security-scan - Run dependency vulnerability scan"
	@echo "  make clean         - Clean up generated files"
	@echo "  make run-download  - Download raw data"
	@echo "  make run-process   - Process downloaded data"
	@echo "  make docs-serve    - Start documentation development server"
	@echo "  make docs-build    - Build documentation"
	@echo "  make docs-test     - Test documentation"
	@echo "  make docs-deploy   - Deploy documentation to GitHub Pages"

# Install production dependencies (UV-first)
install:
	@command -v uv >/dev/null 2>&1 || { echo "uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
	uv sync --no-dev

# Install development dependencies (UV-first)
install-dev:
	@command -v uv >/dev/null 2>&1 || { echo "uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
	uv sync

# Legacy pip install (deprecated)
install-pip:
	@echo "⚠️  Warning: pip install is deprecated. Use 'make install' for UV-based installation."
	uv pip install -e .

# Legacy pip dev install (deprecated)
install-dev-pip:
	@echo "⚠️  Warning: pip install is deprecated. Use 'make install-dev' for UV-based installation."
	uv pip install -e ".[dev]"

# Format code
format:
	black . --exclude=venv
	isort . --skip venv

# Run linting
lint:
	flake8 . --exclude=venv
	pylint china_data_processor.py china_data_downloader.py utils/ --ignore=venv

# Run standard tests
test:
	pytest tests/ -v --ignore=tests/test_property_based.py --ignore=tests/test_factories_demo.py

# Run property-based tests with Hypothesis
test-property:
	@echo "Running property-based tests with Hypothesis..."
	pytest tests/test_property_based.py -v --hypothesis-show-statistics

# Run mutation tests with mutmut (enhanced with 2025 best practices)
test-mutation:
	@echo "Running mutation tests with mutmut (enhanced)..."
	@echo "Using parallel execution and incremental mode for faster testing..."
	mutmut run --use-patch-file --processes 4

# Run quick mutation test on specific module
test-mutation-quick:
	@echo "Running quick mutation test on economic indicators..."
	mutmut run --paths-to-mutate utils/economic_indicators/ --runner "python -m pytest tests/test_economic_indicators.py -x --tb=short"

# Run factory demonstration tests
test-factories:
	@echo "Running factory demonstration tests..."
	pytest tests/test_factories_demo.py -v

# Run benchmark tests
test-benchmark:
	@echo "Running performance benchmark tests..."
	pytest tests/test_performance_regression.py -v --benchmark-only

# Run tests in parallel with pytest-xdist
test-parallel:
	@echo "Running tests in parallel with pytest-xdist..."
	pytest -n auto -m "not benchmark"

# Run integration tests with factory fixtures
test-integration:
	@echo "Running integration tests with factory fixtures..."
	pytest tests/test_factoryboy_integration.py -v

# Run all types of tests
test-all: test test-property test-factories test-benchmark test-parallel test-integration
	@echo "All tests completed!"

# Run dependency vulnerability scan
security-scan:
	@echo "Running dependency vulnerability scan..."
	pip-audit --format=json --output=pip-audit-vulnerabilities.json || true
	safety check --json --output=safety-vulnerabilities.json || true
	@echo "Vulnerability scan complete. Check pip-audit-vulnerabilities.json and safety-vulnerabilities.json"

# Clean up generated files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".uv-cache" -exec rm -rf {} + 2>/dev/null || true
	rm -f pip-audit-*.json safety-*.json vulnerability-*.json vulnerability-*.md 2>/dev/null || true

# Run data download
run-download:
	python china_data_downloader.py

# Run data processing
run-process:
	python china_data_processor.py

# Documentation
docs-serve:
	@echo "Starting documentation server..."
	mkdocs serve

docs-build:
	@echo "Building documentation..."
	mkdocs build

docs-deploy:
	@echo "Deploying documentation to GitHub Pages..."
	mkdocs gh-deploy --force

docs-test:
	@echo "Testing documentation..."
	pytest --doctest-modules --doctest-glob='*.md' docs/
	mkdocs build --strict

docs-clean:
	@echo "Cleaning documentation build..."
	rm -rf site/

# Sphinx documentation (alternative)
sphinx-build:
	@echo "Building Sphinx documentation..."
	sphinx-build -b html docs/ docs/_build/html

sphinx-clean:
	@echo "Cleaning Sphinx build..."
	rm -rf docs/_build/
