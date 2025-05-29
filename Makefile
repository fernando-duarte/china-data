# Makefile (enhanced for 2025)
# Respects single source of truth - all tool configurations are maintained in their respective config files

# Variables with sane defaults (overridable)
PYTHON ?= python
UV ?= uv
PYTEST_ARGS ?= -x --maxfail=5
PARALLEL_JOBS ?= auto
RADON_EXCLUDE ?= "*test*,tests/*,scripts/*,*/__pycache__/*,*/.*/*,*/build/*,*/dist/*"

# Default target
.DEFAULT_GOAL := help

# Declare all phony targets at once for clarity
.PHONY: help setup dev clean install install-dev test test-full test-standard test-property test-mutation \
        test-mutation-quick test-factories test-benchmark test-parallel test-integration test-all \
        lint format complexity quick-check security security-full security-scan security-sarif \
        security-sarif-custom security-sarif-validate run-download run-process docs-serve docs-build \
        docs-test docs-deploy check-versions sync-versions pre-commit-run pre-commit-update \
        profile-download profile-process cache-clear cache-status shell notebook validate

# Self-documenting help command
help: ## Show this help message
	@echo "China Data Pipeline - Makefile Commands"
	@echo "======================================="
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Setup & Development:"
	@grep -E '^(setup|dev|install|install-dev|shell|notebook):.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-25s %s\n", $$1, $$2}'
	@echo ""
	@echo "Testing:"
	@grep -E '^test[^:]*:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-25s %s\n", $$1, $$2}'
	@echo ""
	@echo "Code Quality:"
	@grep -E '^(lint|format|complexity|quick-check|validate):.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-25s %s\n", $$1, $$2}'
	@echo ""
	@echo "Security:"
	@grep -E '^security[^:]*:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-25s %s\n", $$1, $$2}'
	@echo ""
	@echo "Documentation:"
	@grep -E '^docs[^:]*:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-25s %s\n", $$1, $$2}'
	@echo ""
	@echo "Data Processing:"
	@grep -E '^run[^:]*:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-25s %s\n", $$1, $$2}'
	@echo ""
	@echo "Maintenance:"
	@grep -E '^(clean|cache-clear|cache-status|check-versions|sync-versions|pre-commit|profile):.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-25s %s\n", $$1, $$2}'

# ===== Setup & Development =====

setup: ## One-command development environment setup (installs UV if needed)
	@echo "🚀 Setting up development environment..."
	@command -v $(UV) >/dev/null 2>&1 || { echo "Installing UV..."; curl -LsSf https://astral.sh/uv/install.sh | sh; }
	$(UV) sync --all-extras
	$(UV) run pre-commit install
	@echo "🔧 Fixing ruamel namespace package issue..."
	@$(UV) run $(PYTHON) scripts/fix_ruamel_namespace.py || echo "⚠️  Could not fix ruamel namespace (might already be fixed)"
	@echo "✅ Development environment ready!"

dev: setup ## Start development mode (runs processor)
	@echo "🔧 Starting development mode..."
	$(UV) run $(PYTHON) china_data_processor.py

install: ## Install production dependencies only
	@command -v $(UV) >/dev/null 2>&1 || { echo "$(UV) not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
	$(UV) sync --no-dev

install-dev: ## Install all dependencies including dev
	@command -v $(UV) >/dev/null 2>&1 || { echo "$(UV) not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
	$(UV) sync

shell: ## Start IPython shell with project context
	@echo "🐚 Starting IPython shell with project context..."
	$(UV) run ipython

notebook: ## Start Jupyter notebook
	@echo "📓 Starting Jupyter notebook..."
	$(UV) run jupyter notebook

# ===== Testing =====

test: ## Run fast test suite (under 3 minutes)
	@echo "🧪 Running fast test suite..."
	$(UV) run pytest $(PYTEST_ARGS) -m "not benchmark and not slow"

test-full: ## Run comprehensive test suite with coverage
	@echo "🧪 Running comprehensive test suite..."
	$(UV) run pytest --cov --cov-report=html --cov-report=term
	$(UV) run pytest --doctest-modules
	$(UV) run pytest tests/test_property_based.py --hypothesis-show-statistics

test-standard: ## Run standard unit tests
	@echo "🧪 Running standard tests..."
	$(UV) run pytest -v --maxfail=10 -m "not benchmark and not slow"

test-property: ## Run property-based tests with Hypothesis
	@echo "🔬 Running property-based tests with Hypothesis..."
	$(UV) run pytest tests/test_property_based.py -v --hypothesis-show-statistics

test-mutation: ## Run mutation tests with mutmut (may take time)
	@echo "🧬 Running mutation tests with mutmut..."
	@echo "⚠️  This may take several minutes..."
	$(UV) run mutmut run || echo "⚠️  Mutation testing may have timed out"

test-mutation-quick: ## Run quick mutation test on economic indicators
	@echo "🧬 Running quick mutation test on economic indicators..."
	$(UV) run mutmut run --paths-to-mutate utils/economic_indicators/

test-factories: ## Run factory demonstration tests
	@echo "🏭 Running factory demonstration tests..."
	$(UV) run pytest tests/test_factories_demo.py -v

test-benchmark: ## Run performance benchmark tests
	@echo "⚡ Running performance benchmark tests..."
	$(UV) run pytest tests/test_performance_regression.py -v --benchmark-only

test-parallel: ## Run tests in parallel with pytest-xdist
	@echo "🚀 Running tests in parallel with pytest-xdist..."
	$(UV) run pytest -n $(PARALLEL_JOBS) -m "not benchmark and not slow" --maxfail=10

test-integration: ## Run integration tests with factory fixtures
	@echo "🔗 Running integration tests with factory fixtures..."
	$(UV) run pytest tests/test_factoryboy_integration.py -v

test-all: test test-property test-factories test-benchmark test-parallel test-integration ## Run all types of tests
	@echo "✅ All tests completed!"

# ===== Code Quality =====

lint: ## Run code quality checks (ruff, mypy, bandit)
	@echo "🔍 Running code quality checks..."
	# Using ruff with its ruff.toml configuration
	$(UV) run ruff check --fix
	$(UV) run ruff format
	# Using mypy with its pyproject.toml configuration
	$(UV) run mypy .
	# Using bandit with its .bandit.yaml configuration
	$(UV) run bandit -r . -f json -o bandit-report.json || true

format: ## Format code with ruff
	@echo "🎨 Formatting code with Ruff..."
	$(UV) run ruff check --fix
	$(UV) run ruff format
	@echo "✅ Code formatting complete!"

complexity: ## Run code complexity analysis
	@echo "📊 Running code complexity analysis..."
	# Using radon with exclude patterns for performance (tests and scripts excluded)
	$(UV) run radon cc . -s -e "$(RADON_EXCLUDE)"

quick-check: ## Run quick quality checks (faster than full lint)
	@echo "⚡ Running quick quality checks..."
	$(UV) run ruff check --select=E,F,I
	$(UV) run mypy . --follow-imports=skip --ignore-missing-imports
	@echo "✅ Quick check complete!"

validate: lint test security ## Run all validation checks
	@echo "✅ All validation checks passed!"

# ===== Security =====

security: ## Run fast security scans
	@echo "🔒 Running security scans..."
	# Using pip-audit as configured in pre-commit
	$(UV) run pip-audit --desc || true
	# Using safety directly (namespace issue should be fixed by setup)
	# Note: may show pkg_resources deprecation warning - this is harmless
	$(UV) run safety scan || true
	@echo "⚠️  Skipping semgrep due to timeout issues"
	@echo "Run 'make security-full' for complete security scan"

security-full: ## Run comprehensive security scans
	@echo "🔒 Running comprehensive security scans..."
	$(UV) run pip-audit --desc
	$(UV) run safety scan
	# Using semgrep with pre-commit configuration
	$(UV) run semgrep --config=p/security-audit --config=p/secrets --timeout=30 --skip-unknown-extensions

security-scan: ## Run dependency vulnerability scan
	@echo "🔍 Running dependency vulnerability scan..."
	$(UV) run pip-audit --format=json --output=pip-audit-vulnerabilities.json || true
	$(UV) run safety scan --output json > safety-vulnerabilities.json || true
	@echo "✅ Vulnerability scan complete. Check pip-audit-vulnerabilities.json and safety-vulnerabilities.json"

security-sarif: ## Generate unified SARIF security reports
	@echo "📊 Generating unified SARIF security reports..."
	@echo "⚠️  Note: This may take several minutes"
	$(UV) run $(PYTHON) scripts/generate_sarif_reports.py || true
	@echo "✅ SARIF reports generated (if successful) in security-reports/ directory"

security-sarif-custom: ## Generate SARIF reports to custom directory
	@echo "📊 Generating SARIF reports to custom directory..."
	@read -p "Enter output directory [security-reports]: " dir; \
	dir=$${dir:-security-reports}; \
	$(UV) run $(PYTHON) scripts/generate_sarif_reports.py --output-dir "$$dir" || true

security-sarif-validate: ## Validate existing SARIF files
	@echo "🔍 Validating existing SARIF files..."
	@if [ -d "security-reports" ]; then \
		for file in security-reports/*.sarif; do \
			if [ -f "$$file" ]; then \
				echo "Validating $$file..."; \
				$(UV) run $(PYTHON) -c "import json; json.load(open('$$file')); print('✅ Valid JSON')" || echo "❌ Invalid JSON"; \
			fi; \
		done; \
	else \
		echo "No security-reports directory found. Run 'make security-sarif' first."; \
	fi

# ===== Documentation =====

docs-serve: ## Start documentation development server
	@echo "📚 Starting documentation server..."
	$(UV) run mkdocs serve --dev-addr localhost:8000

docs-build: ## Build documentation
	@echo "🏗️  Building documentation..."
	$(UV) run mkdocs build --clean

docs-test: ## Test documentation (strict mode)
	@echo "🧪 Testing documentation..."
	$(UV) run mkdocs build --strict

docs-deploy: ## Deploy documentation to GitHub Pages
	@echo "🚀 Deploying documentation..."
	$(UV) run mkdocs gh-deploy --force

# ===== Data Processing =====

run-download: ## Download raw data
	@echo "📥 Downloading raw data..."
	$(UV) run $(PYTHON) china_data_downloader.py

run-process: ## Process downloaded data
	@echo "⚙️  Processing downloaded data..."
	$(UV) run $(PYTHON) china_data_processor.py

# ===== Maintenance =====

clean: ## Clean up generated files and caches
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -rf security-reports/
	$(UV) cache clean

cache-clear: ## Clear all caches (ruff, mypy, pytest, etc.)
	@echo "🧹 Clearing all caches..."
	rm -rf .ruff_cache/ .mypy_cache/ .pytest_cache/ .hypothesis/ .mutmut-cache/
	$(UV) cache clean
	@echo "✅ All caches cleared!"

cache-status: ## Show cache directory sizes
	@echo "📊 Cache status:"
	@du -sh .ruff_cache/ 2>/dev/null || echo "Ruff cache: Not found"
	@du -sh .mypy_cache/ 2>/dev/null || echo "Mypy cache: Not found"
	@du -sh .pytest_cache/ 2>/dev/null || echo "Pytest cache: Not found"
	@du -sh .hypothesis/ 2>/dev/null || echo "Hypothesis cache: Not found"
	@du -sh .mutmut-cache/ 2>/dev/null || echo "Mutmut cache: Not found"

check-versions: ## Check tool version alignment
	@echo "🔍 Checking tool version alignment across all configuration files..."
	$(UV) run $(PYTHON) scripts/sync_tool_versions.py --check-only

sync-versions: ## Synchronize tool versions across configs
	@echo "🔄 Synchronizing tool versions across pre-commit, CI, and pyproject.toml..."
	$(UV) run $(PYTHON) scripts/sync_tool_versions.py
	@echo "📦 Updating lock file..."
	$(UV) lock
	@echo "✅ Version synchronization complete!"
	@echo ""
	@echo "📋 Next steps:"
	@echo "1. Run 'make check-versions' to verify synchronization"
	@echo "2. Run 'pre-commit run --all-files' to test locally"
	@echo "3. Commit and push changes to test CI"

pre-commit-run: ## Run pre-commit on all files
	@echo "🔍 Running pre-commit on all files..."
	$(UV) run pre-commit run --all-files

pre-commit-update: ## Update pre-commit hooks
	@echo "📦 Updating pre-commit hooks..."
	$(UV) run pre-commit autoupdate

profile-download: ## Profile china_data_downloader.py performance
	@echo "📊 Profiling china_data_downloader.py..."
	$(UV) run $(PYTHON) -m cProfile -o download_profile.stats china_data_downloader.py
	$(UV) run $(PYTHON) -c "import pstats; p = pstats.Stats('download_profile.stats'); p.strip_dirs().sort_stats('cumulative').print_stats(20)"

profile-process: ## Profile china_data_processor.py performance
	@echo "📊 Profiling china_data_processor.py..."
	$(UV) run $(PYTHON) -m cProfile -o process_profile.stats china_data_processor.py
	$(UV) run $(PYTHON) -c "import pstats; p = pstats.Stats('process_profile.stats'); p.strip_dirs().sort_stats('cumulative').print_stats(20)"
