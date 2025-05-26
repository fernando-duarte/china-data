.PHONY: help install install-dev format lint test clean run-download run-process

# Default target
help:
	@echo "Available commands:"
	@echo "  make install       - Install production dependencies"
	@echo "  make install-dev   - Install development dependencies"
	@echo "  make format        - Format code with black and isort"
	@echo "  make lint          - Run linting checks"
	@echo "  make test          - Run tests"
	@echo "  make clean         - Clean up generated files"
	@echo "  make run-download  - Download raw data"
	@echo "  make run-process   - Process downloaded data"

# Install production dependencies
install:
	pip install -r requirements.txt

# Install development dependencies
install-dev:
	pip install -r dev-requirements.txt

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

# Clean up generated files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true

# Run data download
run-download:
	python china_data_downloader.py

# Run data processing
run-process:
	python china_data_processor.py
