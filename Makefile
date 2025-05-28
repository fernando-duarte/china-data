# Makefile (enhanced for 2025)
.PHONY: setup dev test lint security clean

# One-command setup
setup:
	@echo "🚀 Setting up development environment..."
	@command -v uv >/dev/null 2>&1 || { echo "Installing UV..."; curl -LsSf https://astral.sh/uv/install.sh | sh; }
	uv sync --all-extras
	uv run pre-commit install
	@echo "✅ Development environment ready!"

# Development workflow
dev: setup
	@echo "🔧 Starting development mode..."
	uv run python china_data_processor.py

# Comprehensive testing
test:
	@echo "🧪 Running comprehensive test suite..."
	uv run pytest --cov --cov-report=html --cov-report=term
	uv run pytest --doctest-modules
	uv run pytest tests/test_property_based.py --hypothesis-show-statistics

# Security and quality checks
lint:
	@echo "🔍 Running code quality checks..."
	uv run ruff check --fix
	uv run ruff format
	uv run mypy .
	uv run bandit -r . -f json -o bandit-report.json

security:
	@echo "🔒 Running security scans..."
	uv run pip-audit --desc
	uv run safety check
	uv run semgrep --config=auto

# Generate SARIF reports for local development and IDE integration
security-sarif:
	@echo "📊 Generating unified SARIF security reports..."
	uv run python scripts/generate_sarif_reports.py
	@echo "✅ SARIF reports generated in security-reports/ directory"
	@echo "💡 Import security-reports/unified-security-report.sarif into your IDE for integrated security analysis"

# Generate SARIF reports with custom output directory
security-sarif-custom:
	@echo "📊 Generating SARIF reports to custom directory..."
	@read -p "Enter output directory [security-reports]: " dir; \
	dir=$${dir:-security-reports}; \
	uv run python scripts/generate_sarif_reports.py --output-dir "$$dir"

# Validate existing SARIF files
security-sarif-validate:
	@echo "🔍 Validating existing SARIF files..."
	@if [ -d "security-reports" ]; then \
		for file in security-reports/*.sarif; do \
			if [ -f "$$file" ]; then \
				echo "Validating $$file..."; \
				uv run python -c "import json; json.load(open('$$file')); print('✅ Valid JSON')" || echo "❌ Invalid JSON"; \
			fi; \
		done; \
	else \
		echo "No security-reports directory found. Run 'make security-sarif' first."; \
	fi

# Clean environment
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -rf security-reports/
	uv cache clean

# Additional targets from original Makefile

.PHONY: help install install-dev install-uv install-dev-uv format complexity test-property test-mutation test-factories test-benchmark test-parallel test-integration test-all check-versions sync-versions run-download run-process security-scan security-sarif security-sarif-custom security-sarif-validate docs-serve docs-build docs-test docs-deploy

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup         - One-command development environment setup (UV)"
	@echo "  make dev           - Start development mode"
	@echo "  make test          - Run comprehensive test suite"
	@echo "  make lint          - Run code quality checks"
	@echo "  make security      - Run security scans"
	@echo "  make security-sarif - Generate unified SARIF security reports"
	@echo "  make security-sarif-custom - Generate SARIF reports to custom directory"
	@echo "  make security-sarif-validate - Validate existing SARIF files"
	@echo "  make clean         - Clean up generated files"
	@echo "  make install       - Install production dependencies (UV)"
	@echo "  make install-dev   - Install development dependencies (UV)"
	@echo "  make install-pip   - Install production dependencies (legacy pip)"
	@echo "  make install-dev-pip - Install development dependencies (legacy pip)"
	@echo "  make format        - Format code with black and isort"
	@echo "  make complexity    - Run detailed code complexity analysis"
	@echo "  make test-property - Run property-based tests with Hypothesis"
	@echo "  make test-mutation - Run mutation tests with mutmut (enhanced)"
	@echo "  make test-factories - Run factory demonstration tests"
	@echo "  make test-benchmark - Run performance benchmark tests"
	@echo "  make test-parallel - Run tests in parallel with pytest-xdist"
	@echo "  make test-integration - Run integration tests with factory fixtures"
	@echo "  make test-all      - Run all types of tests"
	@echo "  make security-scan - Run dependency vulnerability scan"
	@echo "  make sync-versions - Synchronize tool versions between pre-commit and CI"
	@echo "  make check-versions - Check tool version alignment"
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
	@echo "Formatting code with Ruff, Black, and isort..."
	ruff check . --fix
	ruff format .
	black . --exclude=venv
	isort . --skip venv

# Run detailed code complexity analysis
complexity:
	@echo "Running detailed code complexity analysis..."
	radon cc . --show --average

# Run standard tests
test-standard:
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

# Download raw data
run-download:
	python china_data_downloader.py

# Process downloaded data
run-process:
	python china_data_processor.py

# Documentation commands
docs-serve:
	mkdocs serve --dev-addr localhost:8000

docs-build:
	mkdocs build --clean

docs-test:
	mkdocs build --strict

docs-deploy:
	mkdocs gh-deploy --force

# Check tool version alignment
check-versions:
	@echo "🔍 Checking tool version alignment across all configuration files..."
	python scripts/sync_tool_versions.py --check-only

# Synchronize tool versions
sync-versions:
	@echo "🔄 Synchronizing tool versions across pre-commit, CI, and pyproject.toml..."
	python scripts/sync_tool_versions.py
	@echo "📦 Updating lock file..."
	uv lock
	@echo "✅ Version synchronization complete!"
	@echo ""
	@echo "📋 Next steps:"
	@echo "1. Run 'make check-versions' to verify synchronization"
	@echo "2. Run 'pre-commit run --all-files' to test locally"
	@echo "3. Commit and push changes to test CI"
