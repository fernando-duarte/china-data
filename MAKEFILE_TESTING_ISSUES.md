# Makefile Testing Issues and Untested Commands

## Overview

This document lists all issues encountered during Makefile testing and commands that were not tested.

## 🚫 Untested Commands

### Testing Commands

- `make test-parallel` - Not tested (would likely have same failures as `make test`)
- `make test-integration` - Not tested (would likely have same failures as `make test`)
- `make test-mutation` - Skipped due to time constraints (expected to take several minutes)
- `make test-mutation-quick` - Not tested
- `make test-all` - Not tested (runs all test types)

### Security Commands

- `make security-full` - Not tested (includes semgrep which has timeout issues)
- `make security-scan` - Not tested
- `make security-sarif` - Not tested
- `make security-sarif-custom` - Not tested
- `make security-sarif-validate` - Not tested

### Documentation Commands

- `make docs-serve` - Not tested (would start server requiring manual termination)
- `make docs-deploy` - Not tested (would deploy to GitHub Pages)

### Data Processing Commands

- `make run-download` - Not tested

### Maintenance Commands

- `make cache-clear` - Not tested
- `make sync-versions` - Not tested
- `make pre-commit-run` - Not tested
- `make pre-commit-update` - Not tested
- `make profile-download` - Not tested
- `make profile-process` - Not tested
- `make dev` - Not tested (runs processor continuously)
- `make validate` - Not tested (combines lint, test, and security)

## ❌ Failed Tests

### Unit Test Failures (`make test` and `make test-standard`)

1. **test_download_wdi_data_success**

   - Error: `DataDownloadError: Failed to download from World Bank WDI: All 3 download attempts failed`
   - Issue: 'WdiDownloader' object is not iterable

2. **test_tfp_with_zero_values**

   - Error: `assert nan == 0`
   - Issue: TFP calculation returns NaN for zero values instead of 0

3. **test_create_china_growth_scenario**

   - Error: `AssertionError: GDP should be strongly correlated with time`
   - Issue: GDP correlation (0.876-0.881) is below required threshold (0.9)

4. **test_factory_data_consistency**

   - Error: `AssertionError: GDP accounting identity violated: 0.334-0.354`
   - Issue: Discrepancy exceeds allowed threshold (0.3)

5. **test_parametrized_factory_attributes** (3 variants)
   - Error: `fixture 'economic_data__gdp_usd_bn' not found`
   - Issue: Case sensitivity in fixture naming

### Property-Based Test Failures (`make test-property`)

1. **test_tfp_alpha_sensitivity_property**

   - Error: `AssertionError: TFP should change with different alpha values`
   - Issue: TFP remains constant when alpha changes

2. **test_time_series_monotonicity_property**

   - Error: `AssertionError: Series should have positive correlation with time: -0.574`
   - Issue: Negative correlation found when positive expected

3. **test_gdp_accounting_identity_property**
   - Error: `AssertionError: GDP accounting identity violated: discrepancy = 0.312`
   - Issue: Exceeds allowed threshold (0.3)

### Factory Test Failures (`make test-factories`)

1. **test_create_china_growth_scenario**

   - Same as in unit tests

2. **test_factory_data_consistency**
   - Same as in unit tests

### Additional Test Failures

- **test_comparative_analysis[6000.0-5000.0]**
  - Error: Tax revenue assertion failure (849.67 < 1002.26)
- **test_check_and_update_hash_new_file**
  - Error: FileNotFoundError for IMF dataset
- **test_markdown_output_format**
  - Error: Expected header not found in output
- **test_basic_markdown_creation**
  - Error: Mock file assertion failure

## ⚠️ Commands with Issues

### Linting Issues (`make lint` and `make quick-check`)

- **MyPy Errors**: 114-135 type checking errors across 14-16 files
  - Missing type parameters for pandas Series
  - Type incompatibilities in various modules
  - Missing stub packages (types-PyYAML)
  - Pydantic type issues

### Security Scan Issues (`make security`)

1. **pip-audit**

   - Found 1 vulnerability: `py 1.11.0` - ReDoS vulnerability (PYSEC-2022-42969)
   - Warning: china-data package not found on PyPI

2. **safety**
   - Error: `ModuleNotFoundError: No module named 'ruamel'`
   - Despite adding ruamel.yaml to dependencies, safety still fails

### Documentation Issues (`make docs-test`)

- Failed in strict mode with 3 warnings:
  - Missing file: `adrs/002-type-checking-strategy.md`
  - Missing file: `adrs/003-documentation-strategy.md`
  - Missing file: `user-guide/customization.md`

### Other Issues

1. **Jupyter Notebook** (`make notebook`)

   - Works but requires manual termination
   - Exit code 143 when killed

2. **Pre-commit Configuration**
   - Warning: "Unexpected key(s) present at root: \_file_patterns"

## 📊 Summary Statistics

- **Total Commands**: ~45
- **Tested Commands**: 23
- **Untested Commands**: 22
- **Fully Working**: 12
- **Working with Issues**: 7
- **Failed**: 4

## 🔧 Recommendations

1. **Fix Test Failures**: Address the failing unit, property, and factory tests
2. **Type Annotations**: Add missing type hints to resolve MyPy errors
3. **Security Dependencies**: Investigate why safety still fails despite ruamel.yaml installation
4. **Documentation**: Create missing documentation files or update links
5. **Test Coverage**: Run the untested commands, especially:
   - Mutation testing
   - Security SARIF reports
   - Performance profiling
6. **CI Integration**: Test commands that interact with external services (docs-deploy, etc.)
