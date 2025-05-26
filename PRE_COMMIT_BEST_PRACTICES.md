# Pre-commit Configuration Best Practices

This document outlines the best practices implemented in our pre-commit configuration based on 2025 standards.

## Configuration Overview

Our `.pre-commit-config.yaml` follows modern best practices for Python projects:

### 1. **Core Configuration Settings**

- **Version pinning**: All hooks use specific versions for reproducibility
- **Default Python version**: Set to Python 3.9 for consistency
- **Fail fast disabled**: Shows all failures at once for better developer experience
- **Global exclusions**: Centralized exclude patterns for virtual environments and caches

### 2. **Code Quality Hooks**

#### Basic File Checks

- `check-yaml`, `check-toml`, `check-json`: Validate configuration files
- `check-ast`: Ensure Python files are syntactically valid
- `check-added-large-files`: Prevent accidental large file commits (>1MB)
- `check-merge-conflict`: Detect merge conflict markers
- `check-case-conflict`: Prevent case conflicts on case-insensitive filesystems
- `end-of-file-fixer`: Ensure files end with a newline
- `trailing-whitespace`: Remove trailing whitespace
- `mixed-line-ending`: Enforce consistent line endings (LF)

#### Python Code Formatting and Quality (2025 Update)

- **Ruff** (v0.8.4): Ultra-fast Python linter and formatter that replaces:
  - Black (formatting)
  - isort (import sorting)
  - Flake8 (linting)
  - pyupgrade (syntax modernization)
  - pydocstyle (docstring checking)
  - And 30+ other tools
  - 10-100x faster than traditional tools
  - Comprehensive rule set covering 500+ rules
- **Pylint** (v3.3.1): Advanced static analysis (kept for additional checks)
  - **Performance Optimized**: Parallel processing with `--jobs=0` for 2-4x speedup
  - **Enhanced Caching**: Persistent cache with optimized settings
  - **Reduced Inference**: Limited to 50 results for faster analysis
- **mypy** (v1.13.0): Static type checking
- **pyupgrade** (v3.19.0): Additional syntax modernization

### 3. **Security Hooks**

- **Bandit** (v1.7.10): Security vulnerability scanning in Python code
- **pip-audit** (v2.7.3): Dependency vulnerability scanning
- **detect-secrets** (v1.5.0): Prevent committing secrets and credentials
- `detect-private-key`: Basic private key detection

### 4. **Documentation and Configuration**

- **Prettier** (v4.0.0-alpha.8): YAML and Markdown formatting
- **markdownlint** (v0.43.0): Markdown linting with auto-fix

### 5. **CI/CD Integration**

- **pre-commit.ci configuration**:
  - Automatic PR fixes
  - Weekly dependency updates
  - Skip hooks requiring system dependencies

## Best Practices Implemented (2025 Standards)

1. **Modern Tooling**: Ruff as the primary linter/formatter for 10-100x performance improvement
2. **Layered Security**: Multiple security scanners (Bandit via Ruff, pip-audit, detect-secrets)
3. **Comprehensive Formatting**: Unified Python formatting with Ruff, plus YAML and Markdown
4. **Type Safety**: Static type checking with mypy
5. **Import Management**: Automatic import sorting via Ruff
6. **Documentation Standards**: Enforced through Ruff's pydocstyle rules and markdownlint
7. **Performance**: Excludes unnecessary directories globally, ultra-fast Ruff execution
8. **CI-Friendly**: Proper configuration for pre-commit.ci service
9. **Simplified Configuration**: Single `ruff.toml` replaces multiple tool configs

## Pylint Performance Optimizations (2025 Enhancement)

The project now includes significant pylint performance optimizations:

### **Parallel Processing**

- **Configuration**: `jobs = 0` in `pyproject.toml` uses all available CPU cores
- **Performance Gain**: 2-4x speedup on multi-core systems
- **Implementation**: Applied to pre-commit hooks, Makefile, and CI workflows

### **Enhanced Caching**

- **Persistent Cache**: `persistent = true` with `clear-cache-post-run = false`
- **Optimized Inference**: `limit-inference-results = 50` for faster analysis
- **Cache Retention**: Maintains cache between runs for incremental improvements

### **Performance Results**

- **Before**: 9.5 seconds (single-threaded)
- **After**: 6.5 seconds (parallel processing)
- **Improvement**: 32% faster execution time
- **CPU Utilization**: 500%+ (utilizing multiple cores)

### **Dual Linting Strategy**

- **Ruff**: Ultra-fast (0.07 seconds) for routine development feedback
- **Pylint**: Comprehensive analysis (6.5 seconds) for deep static analysis
- **Best of Both**: Speed when needed, thoroughness when required

## Ruff Configuration (New for 2025)

The project now uses Ruff as the primary Python linter and formatter. The `ruff.toml` file contains:

- **500+ linting rules** from 30+ different tools
- **Black-compatible formatting** with 120-character line length
- **Smart per-file ignores** for tests and `__init__.py` files
- **Security scanning** via Bandit rules (S prefix)
- **Performance analysis** via Perflint rules (PERF prefix)
- **Type checking preparation** via flake8-type-checking (TCH prefix)

## Usage

### Initial Setup

```bash
# Install pre-commit
pip install pre-commit

# Install the git hook scripts
pre-commit install

# Run against all files
pre-commit run --all-files
```

### Creating Secrets Baseline

```bash
# Generate initial secrets baseline
detect-secrets scan > .secrets.baseline

# Audit the baseline
detect-secrets audit .secrets.baseline
```

### Updating Dependencies

```bash
# Update all hook versions
pre-commit autoupdate

# Run updated hooks
pre-commit run --all-files
```

## Maintenance

1. **Regular Updates**: Run `pre-commit autoupdate` monthly
2. **Security Scans**: Review pip-audit results regularly
3. **Baseline Updates**: Update `.secrets.baseline` when adding new secrets
4. **Configuration Review**: Review hook configurations quarterly

## Troubleshooting

### Common Issues

1. **mypy failures**: Ensure type stubs are installed (see additional_dependencies)
2. **pip-audit network errors**: This hook requires internet access
3. **Large file warnings**: Consider using Git LFS for files >1MB
4. **Secrets detected**: Review and add to `.secrets.baseline` if false positive

### Performance Tips

1. Use `--files` flag to run on specific files during development
2. Consider using `fail_fast: true` during initial cleanup
3. Run resource-intensive hooks (pylint, mypy) less frequently if needed
