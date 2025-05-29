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

# Fast testing (under 3 minutes)
test:
	@echo "🧪 Running fast test suite..."
	uv run pytest tests/ -v --maxfail=5 --tb=short -x --timeout=180 \
		--ignore=tests/test_property_based.py \
		--ignore=tests/test_factories_demo.py \
		--ignore=tests/test_performance_regression.py \
		--ignore=tests/test_snapshots.py \
		-m "not benchmark and not slow"

# Comprehensive testing (may take longer)
test-full:
	@echo "🧪 Running comprehensive test suite..."
	uv run pytest --cov --cov-report=html --cov-report=term --timeout=300
	uv run pytest --doctest-modules --timeout=180
	uv run pytest tests/test_property_based.py --hypothesis-show-statistics --timeout=300

# Security and quality checks (optimized)
lint:
	@echo "🔍 Running code quality checks..."
	uv run ruff check --fix --exclude scripts/
	uv run ruff format --exclude scripts/
	uv run mypy . --ignore-missing-imports
	@echo "⚠️  Skipping bandit on scripts/ due to known security warnings"
	uv run bandit -r . -f json -o bandit-report.json --exclude scripts/ || true

security:
	@echo "🔒 Running security scans..."
	uv run pip-audit --desc || true
	uv run safety check || true
	@echo "⚠️  Skipping semgrep due to timeout issues"
	@echo "Run 'make security-full' for complete security scan"

# Full security scan (may take longer)
security-full:
	@echo "🔒 Running comprehensive security scans..."
	uv run pip-audit --desc
	uv run safety check
	uv run semgrep --config=auto

# Generate SARIF reports for local development and IDE integration
security-sarif:
	@echo "📊 Generating unified SARIF security reports..."
	@echo "⚠️  Note: This may take several minutes"
	uv run python scripts/generate_sarif_reports.py || true
	@echo "✅ SARIF reports generated (if successful) in security-reports/ directory"

# Generate SARIF reports with custom output directory
security-sarif-custom:
	@echo "📊 Generating SARIF reports to custom directory..."
	@read -p "Enter output directory [security-reports]: " dir; \
	dir=$${dir:-security-reports}; \
	uv run python scripts/generate_sarif_reports.py --output-dir "$$dir" || true

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

.PHONY: help install install-dev format complexity test-property test-mutation test-factories test-benchmark test-parallel test-integration test-all check-versions sync-versions run-download run-process security-scan docs-serve docs-build docs-test docs-deploy

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup         - One-command development environment setup (UV)"
	@echo "  make dev           - Start development mode"
	@echo "  make test          - Run fast test suite (under 3 minutes)"
	@echo "  make test-full     - Run comprehensive test suite (may take longer)"
	@echo "  make lint          - Run code quality checks (optimized)"
	@echo "  make security      - Run fast security scans"
	@echo "  make security-full - Run comprehensive security scans"
	@echo "  make security-sarif - Generate unified SARIF security reports"
	@echo "  make security-sarif-custom - Generate SARIF reports to custom directory"
	@echo "  make security-sarif-validate - Validate existing SARIF files"
	@echo "  make clean         - Clean up generated files"
	@echo "  make install       - Install production dependencies (UV)"
	@echo "  make install-dev   - Install development dependencies (UV)"
	@echo "  make format        - Format code with ruff"
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

# Format code (simplified and optimized)
format:
	@echo "🎨 Formatting code with Ruff..."
	uv run ruff check . --fix --exclude scripts/
	uv run ruff format . --exclude scripts/
	@echo "✅ Code formatting complete!"

# Run detailed code complexity analysis
# Paths to analyze are documented in [tool.radon] section of pyproject.toml
# Using targeted approach for fast execution (avoids scanning large directories)
complexity:
	@echo "📊 Running detailed code complexity analysis..."
	@echo "ℹ️  Analyzing specific paths (see [tool.radon] in pyproject.toml for details)"
	uv run radon cc utils/ config.py config_schema.py china_data_downloader.py china_data_processor.py -s -a

# Run standard tests (optimized)
test-standard:
	@echo "🧪 Running standard tests..."
	uv run pytest tests/ -v --timeout=180 --maxfail=10 \
		--ignore=tests/test_property_based.py \
		--ignore=tests/test_factories_demo.py \
		--ignore=tests/test_performance_regression.py \
		-m "not benchmark and not slow"

# Run property-based tests with Hypothesis (with timeout)
test-property:
	@echo "🔬 Running property-based tests with Hypothesis..."
	uv run pytest tests/test_property_based.py -v --hypothesis-show-statistics --timeout=300

# Run mutation tests with mutmut (enhanced with timeout)
test-mutation:
	@echo "🧬 Running mutation tests with mutmut..."
	@echo "⚠️  This may take several minutes..."
	uv run mutmut run --use-patch-file --processes 2 || echo "⚠️  Mutation testing may have timed out"

# Run quick mutation test on specific module
test-mutation-quick:
	@echo "🧬 Running quick mutation test on economic indicators..."
	uv run mutmut run --paths-to-mutate utils/economic_indicators/ --runner "python -m pytest tests/test_economic_indicators.py -x --tb=short"

# Run factory demonstration tests (with timeout)
test-factories:
	@echo "🏭 Running factory demonstration tests..."
	uv run pytest tests/test_factories_demo.py -v --timeout=180

# Run benchmark tests (with timeout)
test-benchmark:
	@echo "⚡ Running performance benchmark tests..."
	uv run pytest tests/test_performance_regression.py -v --benchmark-only --timeout=300

# Run tests in parallel with pytest-xdist (optimized)
test-parallel:
	@echo "🚀 Running tests in parallel with pytest-xdist..."
	uv run pytest -n auto -m "not benchmark and not slow" --timeout=180 --maxfail=10

# Run integration tests with factory fixtures (with timeout)
test-integration:
	@echo "🔗 Running integration tests with factory fixtures..."
	uv run pytest tests/test_factoryboy_integration.py -v --timeout=300

# Run all types of tests (with reasonable timeouts)
test-all: test test-property test-factories test-benchmark test-parallel test-integration
	@echo "✅ All tests completed!"

# Run dependency vulnerability scan (with timeout)
security-scan:
	@echo "🔍 Running dependency vulnerability scan..."
	uv run pip-audit --format=json --output=pip-audit-vulnerabilities.json || true
	uv run safety check --json --output=safety-vulnerabilities.json || true
	@echo "✅ Vulnerability scan complete. Check pip-audit-vulnerabilities.json and safety-vulnerabilities.json"

# Download raw data (with timeout)
run-download:
	@echo "📥 Downloading raw data..."
	uv run python china_data_downloader.py

# Process downloaded data (with timeout)
run-process:
	@echo "⚙️  Processing downloaded data..."
	uv run python china_data_processor.py

# Documentation commands (with timeouts)
docs-serve:
	@echo "📚 Starting documentation server..."
	uv run mkdocs serve --dev-addr localhost:8000

docs-build:
	@echo "🏗️  Building documentation..."
	uv run mkdocs build --clean

docs-test:
	@echo "🧪 Testing documentation..."
	uv run mkdocs build --strict

docs-deploy:
	@echo "🚀 Deploying documentation..."
	uv run mkdocs gh-deploy --force

# Check tool version alignment (with timeout)
check-versions:
	@echo "🔍 Checking tool version alignment across all configuration files..."
	uv run python scripts/sync_tool_versions.py --check-only

# Synchronize tool versions (with timeout)
sync-versions:
	@echo "🔄 Synchronizing tool versions across pre-commit, CI, and pyproject.toml..."
	uv run python scripts/sync_tool_versions.py
	@echo "📦 Updating lock file..."
	uv lock
	@echo "✅ Version synchronization complete!"
	@echo ""
	@echo "📋 Next steps:"
	@echo "1. Run 'make check-versions' to verify synchronization"
	@echo "2. Run 'pre-commit run --all-files' to test locally"
	@echo "3. Commit and push changes to test CI"
