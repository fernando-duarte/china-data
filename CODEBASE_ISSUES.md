# Codebase Issues to Fix

## Critical Issues

### 1. Syntax Errors
- **File:** `tests/test_wdi_downloader.py:167`
  - **Issue:** IndentationError - unexpected unindent
  - **Impact:** File cannot be imported, breaks test collection

### 2. Linting Violations (flake8)

#### Unused Imports (F401)
- **File:** `tests/test_downloader.py`
  - Lines 10-13: `builtins`, `io`, `types`, `unittest.mock` imported but unused

- **File:** `tests/test_economic_indicators.py`
  - Line 1: `unittest.mock.MagicMock` imported but unused
  - Line 7: `config.Config` imported but unused

- **File:** `tests/test_economic_indicators_extra.py`
  - Line 8: `utils.economic_indicators.calculate_tfp` imported but unused

- **File:** `tests/test_integration_processor.py`
  - Line 4: `unittest.mock.mock_open` imported but unused

- **File:** `tests/test_integration_processor_output.py`
  - Lines 1-3: `os`, `shutil`, `tempfile` imported but unused

- **File:** `tests/test_wdi_downloader_additional.py`
  - Line 2: `datetime.datetime` imported but unused
  - Line 3: `unittest.mock` imported but unused
  - Line 6: `numpy as np` imported but unused
  - Line 8: `pytest` imported but unused
  - Line 9: `requests` imported but unused
  - Line 11: `config.Config` imported but unused
  - Line 13: `utils.error_handling.DataDownloadError` imported but unused

- **File:** `utils/data_sources/fallback_loader.py`
  - Line 14: `config.Config` imported but unused

- **File:** `utils/data_sources/fallback_utils.py`
  - Line 10: `typing.Optional` imported but unused
  - Line 15: `utils.error_handling.log_error_with_context` imported but unused

#### Invalid Escape Sequences (W605)
- **File:** `utils/output/markdown_template.py`
  - Line 42: `'\_'` - invalid escape sequence
  - Line 43: `'\_'` - invalid escape sequence
  - Line 81: `'\d'` - invalid escape sequence (appears twice)

#### Formatting Issues
- **File:** `tests/processor/test_extrapolation.py`
  - Line 32: E303 - too many blank lines (2)
  - Line 33: E306 - expected 1 blank line before nested definition, found 0

- **File:** `tests/test_integration_processor_output.py`
  - Line 45: E301 - expected 1 blank line, found 0

#### Trailing Blank Lines (W391)
- `tests/test_economic_indicators.py:171`
- `tests/test_integration_processor.py:189`
- `tests/test_processor_cli.py:183`
- `tests/test_pwt_downloader.py:183`
- `utils/data_sources/fallback_utils.py:191`

### 3. Test Coverage Below Required 95%

**Current Coverage: 23% (Target: 95%)**

#### Zero Coverage Files
- `china_data_downloader.py` (0%)
- `china_data_processor.py` (0%)
- `utils/data_sources/fallback_loader.py` (0%)
- `utils/data_sources/fallback_utils.py` (0%)

#### Critically Low Coverage (<10%)
- `utils/capital/calculation.py` (6%)
- `utils/capital/investment.py` (7%)
- `utils/capital/projection.py` (5%)
- `utils/output/formatters.py` (9%)
- `utils/output/markdown_generator.py` (12%)
- `utils/processor_extrapolation.py` (9%)
- `utils/processor_hc.py` (7%)
- `utils/processor_units.py` (14%)
- `utils/economic_indicators/indicators_calculator.py` (9%)

#### Low Coverage (<25%)
- `utils/data_sources/imf_loader.py` (15%)
- `utils/data_sources/pwt_downloader.py` (22%)
- `utils/data_sources/wdi_downloader.py` (23%)
- `utils/processor_dataframe/merge_operations.py` (14%)
- `utils/processor_dataframe/metadata_operations.py` (16%)
- `utils/processor_dataframe/output_operations.py` (20%)
- `utils/processor_load.py` (18%)
- `utils/economic_indicators/tfp_calculator.py` (21%)
- `utils/extrapolation_methods/arima.py` (23%)
- `utils/extrapolation_methods/linear_regression.py` (23%)

### 4. Error Handling Violations

#### Print Statements Instead of Logging
- **File:** `utils/processor_cli.py`
  - Lines 44-46: Uses `print()` statements for error output instead of logging framework
  - **Code:**
    ```python
    print("Input validation errors:", file=sys.stderr)
    for error in validation_errors:
        print(f"  - {error}", file=sys.stderr)
    ```

### 5. Type Checking Configuration Issues

#### Permissive mypy Configuration
- **File:** `pyproject.toml`
  - Line 38: `disallow_untyped_defs = false` should be `true` for strict type checking
  - Line 40: `exclude = ["venv", "tests"]` - tests should be type-checked

## Medium Priority Issues

### 6. Incomplete Test Implementation
- **File:** `tests/test_wdi_downloader.py`
  - File appears truncated at line 167
  - Last function `test_no_sleep_in_successful_download` is incomplete
  - Missing closing function implementation

### 7. Documentation Issues

#### Missing Function Docstrings
- **File:** `tests/test_downloader.py`
  - Line 36: Function `make_df(rows)` lacks docstring
  - Multiple test functions lack descriptive docstrings

### 8. Math Formatting Issues
- **File:** `utils/output/markdown_template.py`
  - Invalid LaTeX escape sequences that may not render correctly in pandoc PDF conversion
  - Need proper escaping for mathematical notation

### 9. Configuration Inconsistencies
- Some modules may still contain hardcoded values that should be moved to `config.py`
- Review needed for complete centralization of configuration

## Summary

**Total Issues:** 50+ individual violations across multiple categories
**Critical Blockers:** 4 (syntax error, test coverage, linting, error handling)
**Files Requiring Immediate Attention:** 15+
**Estimated Effort:** High - requires systematic cleanup across entire codebase 