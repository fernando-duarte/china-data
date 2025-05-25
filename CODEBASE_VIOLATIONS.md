# Codebase Violations - To-Do List

This document tracks all violations found during the codebase assessment against `CODEBASE_REVIEW.md` standards.

## 🔴 HIGH PRIORITY - Must Fix

### File Length Violations (200 line limit)
- [ ] **tests/test_economic_indicators.py** (293 lines) - Break into smaller test classes or modules
- [ ] **tests/test_integration_processor.py** (282 lines) - Split integration tests across multiple files
- [ ] **utils/output/markdown_generator.py** (227 lines) - Extract template and helper functions
- [ ] **tests/test_wdi_downloader.py** (225 lines) - Split test cases into focused test classes
- [ ] **utils/data_sources/fallback_loader.py** (216 lines) - Break into smaller functions
- [ ] **tests/test_pwt_downloader.py** (206 lines) - Split test cases into focused test classes  
- [ ] **tests/test_processor_cli.py** (201 lines) - Split CLI tests into categories

### Linting Issues (flake8 violations)

#### Unused Imports (F401)
- [ ] **tests/data_integrity/test_value_ranges.py:1** - Remove unused `numpy as np`
- [ ] **tests/processor/test_capital.py:6** - Remove unused `utils.capital.project_capital_stock`
- [ ] **tests/processor/test_extrapolation.py:3** - Remove unused `unittest.mock`
- [ ] **tests/processor/test_extrapolation.py:33-34** - Remove unused arima and linear_regression modules
- [ ] **tests/processor/test_human_capital.py:3** - Remove unused `unittest.mock`
- [ ] **tests/processor/test_loading.py:4,6** - Remove unused `unittest.mock` and `pandas as pd`
- [ ] **tests/processor/test_output.py:3** - Remove unused `os`
- [ ] **tests/processor/test_processed_properties.py:5** - Remove unused `pytest`
- [ ] **tests/test_dataframe_ops.py:1** - Remove unused `os`
- [ ] **tests/test_downloader.py:10-14** - Remove unused imports: `builtins`, `io`, `os`, `types`, `unittest.mock`
- [ ] **tests/test_imf_loader.py:1,3** - Remove unused `MagicMock` and `numpy as np`
- [ ] **tests/test_integration_processor.py:4,6** - Remove unused `MagicMock` and `numpy as np`
- [ ] **tests/test_path_constants.py:2,4** - Remove unused imports
- [ ] **tests/test_pwt_downloader.py:1** - Remove unused `MagicMock`
- [ ] **tests/test_wdi_downloader.py:4** - Remove unused `ANY` and `MagicMock`
- [ ] **utils/data_sources/fallback_loader.py:16** - Remove unused validation imports
- [ ] **utils/data_sources/imf_loader.py:5** - Remove unused `Any` and `Dict`
- [ ] **utils/processor_hc.py:9** - Remove unused `Union`

#### Line Length Issues (E501)
- [ ] **utils/data_sources/fallback_loader.py:31,82,110,116,148,155,161,213,215** - Fix long lines
- [ ] **utils/data_sources/wdi_downloader.py:91,95** - Fix long lines
- [ ] **utils/output/markdown_generator.py:161** - Fix long line
- [ ] **utils/validation_utils.py:71,79** - Fix long lines

#### Invalid Escape Sequences (W605)
- [ ] **utils/output/markdown_generator.py:162,163,201** - Fix escape sequences in LaTeX formulas (use raw strings)

#### Code Style Issues
- [ ] **tests/test_imf_loader.py:131,141** - Fix `== True`/`== False` comparisons (use `is True`/`is False`)
- [ ] **utils/data_sources/wdi_downloader.py:54** - Remove blank line with whitespace
- [ ] **utils/output/__init__.py:4** - Remove trailing whitespace
- [ ] **tests/test_downloader.py:34** - Fix redefinition of unused 'os'
- [ ] **tests/test_economic_indicators.py:237** - Remove unused local variable 'result'

### Test Coverage Issues
- [ ] **Overall coverage: 75%** - Increase to required 95%
- [ ] **china_data_downloader.py: 0%** - Add tests for main downloader script
- [ ] **utils/data_sources/fallback_loader.py: 0%** - Add comprehensive test coverage
- [ ] **utils/capital/investment.py: 7%** - Increase test coverage from 7% to 95%
- [ ] **utils/capital/projection.py: 25%** - Increase test coverage from 25% to 95%
- [ ] **utils/data_sources/pwt_downloader.py: 48%** - Increase test coverage
- [ ] **utils/processor_extrapolation.py: 62%** - Increase test coverage
- [ ] **utils/processor_hc.py: 59%** - Increase test coverage

## 🟡 MEDIUM PRIORITY - Should Fix

### Test Reliability Issues
- [ ] **Fix 15 failing tests** - Address external API dependency issues
- [ ] **tests/test_downloader.py::test_download_wdi_data_failure** - Fix DataDownloadError handling
- [ ] **tests/test_downloader.py::test_get_pwt_data_success** - Mock PWT API to avoid 503 errors
- [ ] **tests/test_integration_processor.py::test_economic_indicators_calculation** - Fix assertion precision
- [ ] **tests/test_pwt_downloader.py** - Mock all PWT API calls (10 failing tests)
- [ ] **tests/test_wdi_downloader.py::test_download_wdi_data_logs_error** - Fix log assertion
- [ ] **tests/test_wdi_downloader.py::test_download_wdi_data_return_type** - Fix type assertion

### Math Formatting Issues
- [ ] **SyntaxWarning: invalid escape sequence** - Fix mathematical formula rendering in markdown
- [ ] **Ensure LaTeX formulas render correctly** in pandoc PDF compilation
- [ ] **Test mathematical notation display** in terminal/screen output

### Documentation Updates
- [ ] **Update README.md** - Reflect any changes made during violation fixes
- [ ] **Add missing docstrings** - Ensure all functions have complete documentation
- [ ] **Update module docstrings** - Reflect current implementation state
- [ ] **Missing Module Docstrings** - The following modules lack a module-level docstring:
    - `utils/caching_utils.py`
    - `utils/markdown_utils.py`
    - `utils/processor_extrapolation.py`
    - `utils/processor_load.py`
- [ ] **Missing Test Function Docstrings** - Some test functions have no docstring explaining their purpose (e.g. `tests/test_downloader.py`)
- [ ] **Print Statements Used for Error Reporting** - Replace print statements in `utils/processor_cli.py` (lines 45-47) with proper logging
- [ ] **Magic Constants Not Centralized** - Replace hard-coded numeric defaults with references to `config.py`:
    - `timeout=30` in `utils/data_sources/pwt_downloader.py`
    - Default values `1/3`, `3.0`, and `2025` in `utils/processor_cli.py`
- [ ] **Duplicate Column Mappings** - Consolidate `column_mapping` in `utils/markdown_utils.py` to use `Config.OUTPUT_COLUMN_MAP`
- [ ] **Mypy Not Configured in Strict Mode** - Enable strict type checking in `pyproject.toml` (`disallow_untyped_defs = true`) and include tests

## 🟢 LOW PRIORITY - Nice to Have

### Code Organization Improvements
- [ ] **Further modularize large utility modules** - Consider breaking down complex modules
- [ ] **Enhance error messages** - Make error messages more user-friendly
- [ ] **Add more type hints** - Improve type coverage where missing
- [ ] **Optimize import statements** - Group imports more logically

### Performance Optimizations
- [ ] **Review pandas operations** - Ensure efficient data processing
- [ ] **Optimize test execution time** - Mock external calls for faster tests
- [ ] **Cache intermediate results** - Reduce redundant calculations

## ✅ COMPLIANT AREAS (No Action Needed)

### Security ✅
- No dangerous code execution found (`eval()`, `exec()`, `pickle.loads()`)
- Proper SSL verification in place
- Appropriate network timeouts configured

### Type Checking ✅
- mypy passes with zero errors
- Type hints used appropriately

### Configuration Management ✅
- Centralized configuration in `config.py`
- No magic numbers found
- All constants properly defined

### Error Handling ✅
- Consistent logging framework usage
- Proper exception hierarchy
- No print() statements for errors

---

## Progress Tracking

**Overall Completion: 0%**

- High Priority: 0/X items completed
- Medium Priority: 0/X items completed  
- Low Priority: 0/X items completed

**Target Completion Date:** _[Set target date]_

**Assigned Reviewer:** _[Assign reviewer for verification]_ 