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
