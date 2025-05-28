# Tool Version Synchronization

This document describes the automated tool version synchronization system that ensures consistency between pre-commit
hooks, CI workflows, and other configuration files.

## Overview

Tool version mismatches between local development and CI environments can lead to unexpected failures. This system
addresses that by maintaining strict version alignment across all configuration files.

To ensure consistency between local development and CI environments, all development tools use pinned versions that
are synchronized across:

- `.pre-commit-config.yaml` - Pre-commit hooks for local development
- `.github/workflows/*.yml` - CI/CD workflows
- `pyproject.toml` - Python package dependencies

## Synchronized Tools

### 1. Code Quality Tools

| Tool          | Pre-commit Version | PyProject Version | CI Version | Purpose                |
| ------------- | ------------------ | ----------------- | ---------- | ---------------------- |
| **ruff**      | v0.11.11           | >=0.11.11,<1.0    | 0.11.11    | Linting and formatting |
| **pylint**    | v3.3.1             | >=3.3.1,<4.0      | 3.3.1      | Additional linting     |
| **mypy**      | v1.13.0            | >=1.13.0,<2.0     | 1.13.0     | Type checking          |
| **pyupgrade** | v3.19.0            | >=3.19.0,<4.0     | 3.19.0     | Syntax modernization   |

### 2. Security Tools

| Tool               | Pre-commit Version | PyProject Version | CI Version | Purpose                |
| ------------------ | ------------------ | ----------------- | ---------- | ---------------------- |
| **pip-audit**      | v2.7.3             | >=2.7.3,<3.0      | 2.7.3      | Vulnerability scanning |
| **detect-secrets** | v1.5.0             | >=1.5.0,<2.0      | 1.5.0      | Secrets detection      |
| **bandit**         | N/A (uses Ruff)    | >=1.7.0,<2.0      | 1.7.0      | Security linting       |

### 3. Documentation Tools

| Tool             | Pre-commit Version | PyProject Version | CI Version    | Purpose                  |
| ---------------- | ------------------ | ----------------- | ------------- | ------------------------ |
| **prettier**     | v4.0.0-alpha.8     | N/A               | 4.0.0-alpha.8 | YAML/Markdown formatting |
| **markdownlint** | v0.43.0            | N/A               | 0.43.0        | Markdown linting         |

### 4. Code Analysis Tools

| Tool            | Pre-commit Version | PyProject Version | CI Version | Purpose             |
| --------------- | ------------------ | ----------------- | ---------- | ------------------- |
| **radon**       | local hook         | >=6.0.0,<7.0      | 6.0.0      | Complexity analysis |
| **interrogate** | local hook         | >=1.7.0,<2.0      | 1.7.0      | Docstring coverage  |

## Synchronization Strategy

### Version Pinning Philosophy

1. **Pre-commit**: Uses exact versions (e.g., `v2.7.3`) for reproducible local development
2. **PyProject.toml**: Uses compatible version ranges (e.g., `>=2.7.3,<3.0`) for flexibility
3. **CI Workflows**: Uses exact versions (e.g., `2.7.3`) for reproducible builds

### Automated Synchronization

The project includes a synchronization script at `scripts/sync_tool_versions.py` that:

- Checks for version mismatches across configuration files
- Updates versions automatically when run in update mode
- Can be run in check-only mode for validation

#### Usage

```bash
# Check for version mismatches
python scripts/sync_tool_versions.py --check-only

# Update all versions to synchronized state
python scripts/sync_tool_versions.py
```

## CI/CD Integration

### Main CI Workflow (`.github/workflows/ci.yml`)

The main CI workflow now includes all tools that are used in pre-commit:

1. **Ruff** - Linting and formatting
2. **PyUpgrade** - Syntax modernization
3. **Prettier** - YAML/Markdown formatting
4. **Markdownlint** - Markdown linting
5. **Radon** - Code complexity analysis
6. **Interrogate** - Docstring coverage
7. **Pylint** - Additional linting
8. **MyPy** - Type checking
9. **Bandit** - Security scanning

### Security Workflow (`.github/workflows/security-enhanced.yml`)

The security workflow uses pinned versions for:

1. **pip-audit** - Vulnerability scanning
2. **detect-secrets** - Secrets detection
3. **bandit** - Security linting

## Pre-commit Configuration

The `.pre-commit-config.yaml` includes a hook to automatically check version synchronization:

```yaml
- repo: local
  hooks:
    - id: check-tool-versions
      name: check tool version alignment
      entry: python
      language: system
      args: [scripts/sync_tool_versions.py, --check-only]
      files: ^(\.pre-commit-config\.yaml|\.github/workflows/.*\.yml|pyproject\.toml)$
      pass_filenames: false
      require_serial: true
```

This ensures that any changes to configuration files are automatically validated for version consistency.

## Maintenance

### Updating Tool Versions

When updating tool versions:

1. Update the version in `scripts/sync_tool_versions.py`
2. Run the synchronization script: `python scripts/sync_tool_versions.py`
3. Test locally with pre-commit: `pre-commit run --all-files`
4. Commit and push changes
5. Verify CI passes with new versions

### Adding New Tools

To add a new tool to the synchronization system:

1. Add the tool to the `tool_versions` dictionary in `scripts/sync_tool_versions.py`
2. Add the tool to `.pre-commit-config.yaml`
3. Add the tool to `pyproject.toml` dev dependencies
4. Add the tool to relevant CI workflows
5. Run the synchronization script to validate

## Benefits

### Consistency

- Same tool versions across all environments
- Reproducible builds and linting results
- No "works on my machine" issues

### Maintainability

- Single source of truth for tool versions
- Automated validation of version consistency
- Easy bulk updates of tool versions

### Quality Assurance

- All quality checks run in both local and CI environments
- No gaps between pre-commit and CI validation
- Comprehensive security and code quality coverage

## Troubleshooting

### Version Mismatch Errors

If you see version mismatch errors:

1. Run `python scripts/sync_tool_versions.py --check-only` to identify issues
2. Run `python scripts/sync_tool_versions.py` to fix automatically
3. If manual fixes are needed, update all three locations consistently

### CI Failures After Version Updates

1. Check that the new version is available in the package repositories
2. Verify that the new version is compatible with your Python version
3. Test locally first with `pre-commit run --all-files`
4. Check for breaking changes in the tool's changelog

### Pre-commit Hook Failures

1. Ensure all tools are installed: `pre-commit install`
2. Update pre-commit hooks: `pre-commit autoupdate`
3. Clear pre-commit cache: `pre-commit clean`
4. Run specific hook: `pre-commit run <hook-id> --all-files`

## Related Files

- `scripts/sync_tool_versions.py` - Version synchronization script
- `.pre-commit-config.yaml` - Pre-commit hook configuration
- `pyproject.toml` - Python package dependencies
- `.github/workflows/ci.yml` - Main CI workflow
- `.github/workflows/security-enhanced.yml` - Security workflow
- `Makefile` - Build automation (includes sync-versions target)
