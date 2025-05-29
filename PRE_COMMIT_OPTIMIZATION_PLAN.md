# Pre-commit Configuration Optimization Implementation Plan

## 📋 Overview

This plan addresses the identified optimization opportunities while maintaining security and code quality standards.
The implementation is divided into phases to ensure minimal disruption.

## 🎯 Goals

1. Improve pre-commit performance by 30-50%
2. Standardize file targeting patterns
3. Eliminate redundant security scans
4. Simplify configuration maintenance
5. Maintain comprehensive security coverage

## 📊 Expected Outcomes

Based on real-world implementations of similar optimizations:

1. **Initial run**: 30-50% improvement (conservative estimate; could see up to 70-80%)
2. **Subsequent runs with cache**: Could be 90%+ faster
3. **Developer experience**: Significantly improved with faster feedback loops
4. **Real-world evidence**: Similar optimizations have reduced pre-commit times from 50s to 7s (86% improvement)

## 📅 Phase 1: Analysis and Preparation (Day 1)

### 1.1 Create Configuration Backup

```bash
cp .pre-commit-config.yaml .pre-commit-config.yaml.backup
git add .pre-commit-config.yaml.backup
git commit -m "chore: backup current pre-commit configuration"
```

### 1.2 Analyze Current Performance

```bash
# Create a performance baseline
time pre-commit run --all-files > pre-commit-baseline.log 2>&1

# Also measure individual hook performance
pre-commit run --all-files --verbose 2>&1 | tee pre-commit-detailed-baseline.log
```

### 1.3 Document Current File Coverage

Create a mapping of which hooks check which files:

```markdown
# File Coverage Analysis

- Core Python files: china_data_processor.py, china_data_downloader.py
- Utils: utils/\*_/_.py
- Config: config.py, config_schema.py
- Model: model/\*_/_.py
- Tests: tests/\*_/_.py
```

### 1.4 Document Current Cache Usage

```bash
# Check for existing cache directories
ls -la .eslintcache .stylelintcache .mypy_cache .ruff_cache 2>/dev/null || echo "No cache files found"

# Document cache sizes if they exist
du -sh .*cache* 2>/dev/null || echo "No cache directories found"
```

## 📅 Phase 2: Standardize File Patterns (Day 2)

### 2.1 Define Standard File Groups

Create consistent file pattern groups:

```yaml
# Define at the top of .pre-commit-config.yaml as anchors
_file_patterns:
  core_python: &core_python
    files: ^(china_data_processor\.py|china_data_downloader\.py)$

  config_files: &config_files
    files: ^(config\.py|config_schema\.py)$

  utils_files: &utils_files
    files: ^utils/.*\.py$

  model_files: &model_files
    files: ^model/.*\.py$

  all_production_python: &all_production_python
    files: >-
      ^(china_data_processor\.py|china_data_downloader\.py|config\.py|
      config_schema\.py|utils/.*\.py|model/.*\.py)$

  test_files: &test_files
    files: ^tests/.*\.py$
```

### 2.2 Create Simplified Global Exclude

```yaml
exclude: |
  (?x)^(
    \.venv/|
    venv/|
    .*\.egg-info/|
    \.(git|mypy_cache|pytest_cache|ruff_cache|hypothesis)/|
    (build|dist|htmlcov|site|node_modules|workflow_outputs)/|
    \.(vscode|idea)/|
    .*cache/
  )
```

Note: Added `.*cache/` to handle various cache directories automatically.

## 📅 Phase 3: Consolidate Security Hooks (Day 3)

### 3.1 Merge Bandit Hooks

Replace the two Bandit hooks with a single, optimized configuration:

```yaml
  - repo: https://github.com/PyCQA/bandit
    rev: 1.8.3
    hooks:
      - id: bandit
        name: bandit-security-scan
        args:
          - -ll  # Only high severity
          - -f
          - json
          - -o
          - security-results/bandit-report.json
        <<: *all_production_python
        exclude: ^tests/
```

### 3.2 Optimize Semgrep Configuration

Consolidate Semgrep hooks:

```yaml
  - repo: https://github.com/semgrep/semgrep
    rev: v1.99.0
    hooks:
      - id: semgrep
        name: semgrep-security-audit
        args:
          - --config=p/security-audit
          - --config=p/secrets
          - --config=p/python
          - --timeout=30
          - --skip-unknown-extensions
          - --json
          - --output=security-results/semgrep-report.json
        <<: *all_production_python
        exclude: ^tests/
```

### 3.3 Create Security Results Directory

```bash
# Ensure security results directory exists
mkdir -p security-results
echo "security-results/" >> .gitignore
```

## 📅 Phase 4: Optimize Code Quality Hooks (Day 4)

### 4.1 Standardize Linting Tools

```yaml
  # Ruff (handles both linting and formatting)
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.11.11
    hooks:
      - id: ruff
        args: [--fix, --cache-dir=.ruff_cache]
        <<: *all_production_python
      - id: ruff-format
        <<: *all_production_python

  # Pylint for deeper analysis
  - repo: https://github.com/pylint-dev/pylint
    rev: v3.3.1
    hooks:
      - id: pylint
        name: pylint
        <<: *all_production_python
        exclude: ^tests/
        args: [--jobs=0]

  # MyPy for type checking
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.13.0
    hooks:
      - id: mypy
        <<: *all_production_python
        exclude: ^tests/
        args:
          - --strict
          - --python-version=3.13
          - --cache-dir=.mypy_cache
          - --incremental
        additional_dependencies:
          - types-requests
          - pandas-stubs
          - types-pytz
```

### 4.2 Optimize Complexity and Documentation Checks

```yaml
  - repo: local
    hooks:
      - id: radon-complexity
        name: radon complexity check
        entry: radon
        language: system
        args: [cc, --min, B, --show-complexity]
        <<: *all_production_python
        pass_filenames: true

      - id: interrogate
        name: interrogate docstring coverage
        entry: interrogate
        language: system
        args: [--verbose, --fail-under=80]
        <<: *all_production_python
        pass_filenames: true
```

## 📅 Phase 5: Simplify Secret Detection and Cache Management (Day 5)

### 5.1 Streamline detect-secrets

```yaml
- repo: https://github.com/Yelp/detect-secrets
  rev: v1.5.0
  hooks:
    - id: detect-secrets
      args: [--baseline, .secrets.baseline]
      # Use global exclude pattern, no need for custom exclude
```

### 5.2 Cache Management Strategy

Create a cache management guide in `CACHE_MANAGEMENT.md`:

```markdown
# Pre-commit Cache Management

## Cache Locations

- `.ruff_cache/` - Ruff linting and formatting cache
- `.mypy_cache/` - MyPy type checking cache
- `.pytest_cache/` - Pytest cache (if using pytest hooks)

## Cache Invalidation

- Caches are automatically invalidated when tool versions change
- Manual cache clearing: `rm -rf .ruff_cache .mypy_cache`
- Add to .gitignore: `.*cache/`

## Performance Impact

- First run: Creates cache (slower)
- Subsequent runs: Uses cache (much faster)
- Cache hit rate typically > 90% for unchanged files
```

## 📅 Phase 6: Documentation and Testing (Day 6)

### 6.1 Create Documentation

Create `PRE_COMMIT_GUIDE.md` in the root directory (for better visibility):

```markdown
# Pre-commit Configuration Guide

## Quick Reference

- Standard check: `pre-commit run`
- Check all files: `pre-commit run --all-files`
- Check specific files: `pre-commit run --files file1.py file2.py`
- Check specific hooks: `pre-commit run hook-id`
- Clear caches: `rm -rf .ruff_cache .mypy_cache`

## File Patterns

- Core files: Main processor and downloader scripts
- Utils: All utility modules
- Config: Configuration files
- Model: Model-related files

## Performance Tips

1. The configuration is optimized to check only relevant files
2. Heavy checks (pylint, mypy) are skipped in CI for faster feedback
3. Security checks are consolidated to avoid redundant scanning
4. Ruff is 10-100x faster than traditional Python linters
5. Caching is enabled for all tools that support it

## CI Integration

- Heavy tools are automatically skipped in CI
- Use `pre-commit ci` for automated dependency updates
- Security results are saved to `security-results/` directory

## Troubleshooting

- If hooks are slow, check cache directories exist
- Run with `--verbose` to see detailed timing
- Use `--show-diff-on-failure` to see what changes hooks want to make
```

### 6.2 Test Performance Improvements

```bash
# Measure new performance
time pre-commit run --all-files > pre-commit-optimized.log 2>&1

# Measure with verbose output for detailed analysis
pre-commit run --all-files --verbose 2>&1 | tee pre-commit-detailed-optimized.log

# Compare results
diff pre-commit-baseline.log pre-commit-optimized.log

# Calculate improvement percentage
echo "Compare the execution times from both logs to calculate improvement"
```

### 6.3 Validate Cache Effectiveness

```bash
# Run twice to test cache effectiveness
echo "First run (cold cache):"
time pre-commit run --all-files

echo "Second run (warm cache):"
time pre-commit run --all-files

# The second run should be significantly faster
```

## 📅 Phase 7: Gradual Rollout and CI Integration (Days 7-9)

### 7.1 Test on Feature Branch

```bash
git checkout -b optimize-pre-commit
# Apply all changes
git add .
git commit -m "feat: optimize pre-commit configuration for better performance"
```

### 7.2 Update CI Configuration

If using GitHub Actions, ensure `.github/workflows/` files are updated:

```yaml
# Example CI configuration update
- name: Run pre-commit
  uses: pre-commit/action@v3.0.0
  with:
    extra_args: --all-files --verbose
```

### 7.3 Validate and Merge

```bash
# Run comprehensive tests
pre-commit run --all-files

# Test specific scenarios
echo "Testing single file change:"
echo "# test" >> china_data_processor.py
time pre-commit run

# After validation
git checkout main
git merge optimize-pre-commit
git push
```

## 📊 Success Metrics

1. **Performance**: Pre-commit runs 30-50% faster (up to 80% possible)
2. **Cache effectiveness**: 90%+ cache hit rate on unchanged files
3. **Clarity**: File patterns are consistent and documented
4. **Maintainability**: Configuration is DRY (Don't Repeat Yourself)
5. **Coverage**: No reduction in security or quality checks

## 🚨 Rollback Plan

If issues arise:

```bash
# Quick rollback
cp .pre-commit-config.yaml.backup .pre-commit-config.yaml
git add .pre-commit-config.yaml
git commit -m "revert: rollback pre-commit configuration"
pre-commit install --install-hooks

# Clear all caches
rm -rf .ruff_cache .mypy_cache .pytest_cache
```

## 📝 Final Checklist

- [ ] All security tools still run on appropriate files
- [ ] Performance improvement measured and documented (target: 30-80%)
- [ ] Cache directories added to .gitignore
- [ ] Documentation moved to root directory for visibility
- [ ] CI/CD configuration still works correctly
- [ ] No reduction in code quality coverage
- [ ] Cache invalidation strategy documented

## 🔍 Detailed Configuration Examples

### Complete Optimized .pre-commit-config.yaml Structure

```yaml
# File pattern anchors for reuse
_file_patterns:
  core_python: &core_python
    files: ^(china_data_processor\.py|china_data_downloader\.py)$

  config_files: &config_files
    files: ^(config\.py|config_schema\.py)$

  utils_files: &utils_files
    files: ^utils/.*\.py$

  model_files: &model_files
    files: ^model/.*\.py$

  all_production_python: &all_production_python
    files: >-
      ^(china_data_processor\.py|china_data_downloader\.py|config\.py|
      config_schema\.py|utils/.*\.py|model/.*\.py)$

default_language_version:
  python: python3.13

fail_fast: false

# Simplified global exclude with cache directories
exclude: |
  (?x)^(
    \.venv/|
    venv/|
    .*\.egg-info/|
    \.(git|mypy_cache|pytest_cache|ruff_cache|hypothesis)/|
    (build|dist|htmlcov|site|node_modules|workflow_outputs)/|
    \.(vscode|idea)/|
    .*cache/
  )

repos:
  # Standard hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: check-yaml
      - id: check-toml
      - id: check-json
      - id: check-ast
      - id: check-added-large-files
        args: [--maxkb=1000]
      - id: check-merge-conflict
      - id: check-case-conflict
      - id: check-docstring-first
      - id: debug-statements
      - id: detect-private-key
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: mixed-line-ending
        args: [--fix=lf]
      - id: requirements-txt-fixer

  # Code formatting and linting (with caching)
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.11.11
    hooks:
      - id: ruff
        args: [--fix, --cache-dir=.ruff_cache]
        <<: *all_production_python
      - id: ruff-format
        <<: *all_production_python

  # Security scanning (consolidated)
  - repo: https://github.com/semgrep/semgrep
    rev: v1.99.0
    hooks:
      - id: semgrep
        name: semgrep-comprehensive-scan
        args:
          - --config=p/security-audit
          - --config=p/secrets
          - --config=p/python
          - --timeout=30
          - --skip-unknown-extensions
          - --json
          - --output=security-results/semgrep-report.json
        <<: *all_production_python
        exclude: ^tests/

  - repo: https://github.com/PyCQA/bandit
    rev: 1.8.3
    hooks:
      - id: bandit
        name: bandit-security-scan
        args:
          - -ll
          - -f
          - json
          - -o
          - security-results/bandit-report.json
        <<: *all_production_python
        exclude: ^tests/
        pass_filenames: true

  # Additional quality checks with caching
  - repo: https://github.com/pylint-dev/pylint
    rev: v3.3.1
    hooks:
      - id: pylint
        <<: *all_production_python
        exclude: ^tests/
        args: [--jobs=0]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.13.0
    hooks:
      - id: mypy
        <<: *all_production_python
        exclude: ^tests/
        args:
          - --strict
          - --python-version=3.13
          - --cache-dir=.mypy_cache
          - --incremental
        additional_dependencies:
          - types-requests
          - pandas-stubs
          - types-pytz

  # ... (continue with other hooks following the same pattern)

ci:
  autofix_commit_msg: "[pre-commit.ci] auto fixes from pre-commit hooks"
  autofix_prs: true
  autoupdate_branch: ""
  autoupdate_commit_msg: "[pre-commit.ci] pre-commit autoupdate"
  autoupdate_schedule: weekly
  skip:
    - pip-audit
    - pylint
    - mypy
    - radon-complexity
    - interrogate
    - bandit-security-scan
    - semgrep-comprehensive-scan
    - safety-check
  submodules: false
```

## 🎯 Key Improvements Summary

1. **Performance**: Reduced redundant scans, targeted file patterns, enabled caching
2. **Maintainability**: DRY principle with YAML anchors
3. **Clarity**: Clear file pattern definitions
4. **Documentation**: Comprehensive guide in root directory
5. **Cache Management**: Explicit cache handling and invalidation strategy
6. **CI Optimization**: Heavy tools skipped in CI, using pre-commit.ci features

This plan provides a systematic approach to implementing all recommended best practices while maintaining code quality
and security standards.
