.PHONY: help install install-dev install-uv install-dev-uv format lint test clean run-download run-process security-scan

# Default target
help:
	@echo "Available commands:"
	@echo "  make install       - Install production dependencies (pip)"
	@echo "  make install-dev   - Install development dependencies (pip)"
	@echo "  make install-uv    - Install production dependencies (uv)"
	@echo "  make install-dev-uv - Install development dependencies (uv)"
	@echo "  make format        - Format code with black and isort"
	@echo "  make lint          - Run linting checks"
	@echo "  make test          - Run tests"
	@echo "  make security-scan - Run dependency vulnerability scan"
	@echo "  make clean         - Clean up generated files"
	@echo "  make run-download  - Download raw data"
	@echo "  make run-process   - Process downloaded data"

# Install production dependencies
install:
	pip install -r requirements.txt

# Install development dependencies
install-dev:
	pip install -r dev-requirements.txt

# Install production dependencies with uv
install-uv:
	@command -v uv >/dev/null 2>&1 || { echo "uv not found. Install with: pip install uv"; exit 1; }
	uv venv --python 3.9
	uv pip install -e .

# Install development dependencies with uv
install-dev-uv:
	@command -v uv >/dev/null 2>&1 || { echo "uv not found. Install with: pip install uv"; exit 1; }
	uv venv --python 3.9
	uv pip install -e ".[dev]"

# Format code
format:
	black . --exclude=venv
	isort . --skip venv

# Run linting
lint:
	flake8 . --exclude=venv
	pylint china_data_processor.py china_data_downloader.py utils/ --ignore=venv

# Run tests
test:
	pytest tests/ -v

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
