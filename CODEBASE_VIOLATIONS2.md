# Codebase Review Violations

This document lists violations of the guidelines in `CODEBASE_REVIEW.md` found during manual inspection of the repository.

## 1. Missing Module Docstrings
The following modules lack a module-level docstring:
- `utils/caching_utils.py`
- `utils/markdown_utils.py`
- `utils/processor_extrapolation.py`
- `utils/processor_load.py`

Example beginning of `utils/caching_utils.py` showing no docstring:
```
1  from datetime import timedelta
2
3  import requests_cache
```

## 2. File Length Exceeds Limit
`utils/output/markdown_generator.py` contains 227 lines, exceeding the 200 line limit. Several test files also exceed 200 lines:
- `tests/test_economic_indicators.py` (293 lines)
- `tests/test_integration_processor.py` (282 lines)
- `tests/test_wdi_downloader.py` (225 lines)
- `tests/test_pwt_downloader.py` (206 lines)
- `tests/test_processor_cli.py` (201 lines)

## 3. Print Statements Used for Error Reporting
`utils/processor_cli.py` prints validation errors instead of using the logging framework:
```
45          print("Input validation errors:", file=sys.stderr)
46          for error in errors:
47              print(f"  - {error}", file=sys.stderr)
```

## 4. Magic Constants Not Centralized
Several numeric defaults are hard-coded instead of referencing `config.py`:
- `timeout=30` in `utils/data_sources/pwt_downloader.py`
- Default values `1/3`, `3.0`, and `2025` in `utils/processor_cli.py`

## 5. Duplicate Column Mappings
`utils/markdown_utils.py` defines a `column_mapping` dictionary instead of reusing `Config.OUTPUT_COLUMN_MAP` defined in `config.py`.

## 6. Mypy Not Configured in Strict Mode
`pyproject.toml` sets `disallow_untyped_defs = false` and excludes tests, so strict type checking is not enforced.

## 7. Missing Test Function Docstrings
Some test functions, e.g. in `tests/test_downloader.py`, have no docstring explaining their purpose.

These issues conflict with various sections of `CODEBASE_REVIEW.md` concerning documentation, modularity, magic constants, tooling configuration, and code quality standards.
