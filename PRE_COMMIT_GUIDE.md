# Pre-commit Configuration Guide

## Quick Reference

- Standard check: `pre-commit run`
- Check all files: `pre-commit run --all-files`
- Check specific files: `pre-commit run --files file1.py file2.py`
- Check specific hooks: `pre-commit run hook-id`
- Clear caches: `rm -rf .ruff_cache .mypy_cache`
- Install/update hooks: `pre-commit install --install-hooks`

## Performance Optimizations

This configuration has been optimized for performance:

1. **Targeted file patterns**: Each hook only runs on relevant files
2. **Caching enabled**: Ruff and MyPy use caching for faster subsequent runs
3. **Consolidated security scans**: Reduced redundant scanning
4. **Parallel execution**: Multiple hooks can run simultaneously
5. **Smart exclusions**: Cache directories and build artifacts are excluded

## File Patterns

The configuration targets these file groups:

- **Core files**: `china_data_processor.py`, `china_data_downloader.py`
- **Config files**: `config.py`, `config_schema.py`
- **Utils**: All files under `utils/` directory
- **Model**: All files under `model/` directory
- **Tests**: Excluded from most quality checks (except basic syntax)

## Hook Categories

### 1. Basic Checks (Fast)

- YAML/TOML/JSON validation
- Large file detection
- Merge conflict detection
- Private key detection
- Line ending fixes

### 2. Code Formatting (Fast with caching)

- **Ruff**: Lightning-fast Python linter and formatter
- Cache location: `.ruff_cache/`

### 3. Security Scanning (Medium speed)

- **Semgrep**: Security patterns and secrets detection
- **Bandit**: Python security linter (high severity only)
- Results saved to: `security-results/`

### 4. Code Quality (Slower, skipped in CI)

- **Pylint**: Deep code analysis
- **MyPy**: Type checking with cache at `.mypy_cache/`
- **Radon**: Complexity analysis
- **Interrogate**: Docstring coverage

### 5. Dependencies (Slow, skipped in CI)

- **pip-audit**: Vulnerability scanning
- **Safety**: Additional vulnerability checks

## Performance Tips

1. **First run**: Will be slower as caches are built
2. **Subsequent runs**: Much faster due to caching
3. **Partial runs**: Use `pre-commit run --files <files>` for specific files
4. **Skip heavy checks**: Use `SKIP=pylint,mypy pre-commit run` to skip slow hooks

## CI Integration

The following hooks are automatically skipped in CI to speed up builds:

- pip-audit
- pylint
- mypy
- radon-complexity
- interrogate
- bandit-security-scan
- semgrep-security-scan
- safety-check

## Troubleshooting

### Slow performance

1. Check if cache directories exist: `ls -la .*cache`
2. Clear and rebuild caches: `rm -rf .ruff_cache .mypy_cache`
3. Run with verbose output: `pre-commit run --verbose`

### Hook failures

1. Run specific hook: `pre-commit run <hook-id> --all-files`
2. See what changes a hook wants: `pre-commit run --show-diff-on-failure`
3. Auto-fix issues: Many hooks support `--fix` or will auto-fix

### Installation issues

1. Ensure virtual environment is activated
2. Update pre-commit: `pip install --upgrade pre-commit`
3. Clean and reinstall: `pre-commit clean && pre-commit install --install-hooks`

## Cache Management

Caches are stored in:

- `.ruff_cache/` - Ruff linting and formatting cache
- `.mypy_cache/` - MyPy type checking cache
- `.pytest_cache/` - Pytest cache (if using pytest hooks)

All cache directories are:

- Excluded from git (in `.gitignore`)
- Excluded from pre-commit scanning
- Safe to delete if you experience issues

## Security Results

Security scan results are saved to `security-results/`:

- `semgrep-report.json` - Semgrep findings
- `bandit-report.json` - Bandit findings

This directory is excluded from git and should be reviewed locally.
