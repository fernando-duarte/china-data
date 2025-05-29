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
