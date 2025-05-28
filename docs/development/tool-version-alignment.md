# Tool Version Alignment

This document explains the tool version alignment system that ensures consistency between pre-commit hooks and CI workflows.

## Overview

To prevent discrepancies between local development and CI environments, this project maintains strict alignment between tool versions used in:

- Pre-commit hooks (`.pre-commit-config.yaml`)
- CI workflows (`.github/workflows/ci.yml`)
- Project dependencies (`pyproject.toml` and `uv.lock`)

## Current Tool Versions

| Tool   | Version | Source                    |
| ------ | ------- | ------------------------- |
| Ruff   | 0.11.11 | Pre-commit, CI, Lock file |
| Pylint | 3.3.1   | Pre-commit, CI            |
| MyPy   | 1.13.0  | Pre-commit, CI            |

## Alignment System Components

### 1. Version Synchronization Script

The `scripts/sync_tool_versions.py` script automatically synchronizes tool versions:

```bash
# Check alignment without making changes
python scripts/sync_tool_versions.py --check-only

# Synchronize versions (updates CI and pyproject.toml)
python scripts/sync_tool_versions.py
```

### 2. Makefile Targets

Convenient make targets for version management:

```bash
# Check current version alignment
make check-versions

# Synchronize all tool versions
make sync-versions
```

### 3. Pre-commit Hook

A pre-commit hook automatically checks version alignment when configuration files change:

```yaml
- id: check-tool-versions
  name: check tool version alignment
  entry: python
  language: system
  args: [scripts/sync_tool_versions.py, --check-only]
  files: ^(\.pre-commit-config\.yaml|\.github/workflows/.*\.yml|pyproject\.toml)$
```

## Workflow

### When Updating Tool Versions

1. **Update pre-commit configuration** (`.pre-commit-config.yaml`)
2. **Run synchronization**:

   ```bash
   make sync-versions
   ```

3. **Test locally**:

   ```bash
   pre-commit run --all-files
   ```

4. **Commit changes** (including updated lock file)

### Automatic Checks

The system automatically checks alignment:

- **Pre-commit**: When configuration files are modified
- **CI**: Versions are pinned to match pre-commit
- **Make targets**: For manual verification

## Benefits

### 1. **Consistency**

- Same tool versions across all environments
- Predictable behavior between local and CI

### 2. **Automation**

- Automatic detection of version misalignment
- Easy synchronization with single command

### 3. **Maintenance**

- Clear documentation of current versions
- Simplified update process

## Troubleshooting

### Version Misalignment Detected

If the pre-commit hook fails with version misalignment:

```bash
❌ Tool version misalignment detected:
  - ruff: pre-commit=0.11.11, CI=0.11.10
```

**Solution**:

```bash
make sync-versions
```

### CI Failures After Local Success

If pre-commit passes locally but CI fails:

1. Check if versions are aligned:

   ```bash
   make check-versions
   ```

2. Synchronize if needed:

   ```bash
   make sync-versions
   ```

3. Update lock file:

   ```bash
   uv lock
   ```

### Tool Not Found in CI

If CI can't find a tool that works locally:

1. Ensure the tool is in `pyproject.toml` dev dependencies
2. Check that CI installs the exact version:

   ```yaml
   uv add --dev tool==x.y.z
   ```

## Best Practices

### 1. **Regular Updates**

- Use `pre-commit autoupdate` to check for newer versions
- Test thoroughly after version updates
- Update all environments simultaneously

### 2. **Version Pinning Strategy**

- Pin exact versions for critical tools (ruff, pylint, mypy)
- Use ranges for less critical dependencies
- Document version choices in commit messages

### 3. **Testing**

- Always test both pre-commit and CI after version changes
- Run full test suite with new tool versions
- Check for any behavior changes in linting/formatting

## Implementation Details

### Script Architecture

The synchronization script:

1. **Extracts** versions from `.pre-commit-config.yaml`
2. **Compares** with CI workflow versions
3. **Updates** CI and pyproject.toml files
4. **Reports** any misalignments

### CI Integration

The CI workflow uses exact version pinning:

```yaml
- name: Lint and format check with Ruff
  run: |
    # Use exact ruff version from pre-commit (v0.11.11)
    uv add --dev ruff==0.11.11
    uv run ruff check . --output-format=github
```

This ensures the same tool behavior as pre-commit hooks.

## Future Enhancements

- **Automated version updates** via GitHub Actions
- **Version compatibility matrix** for different Python versions
- **Integration with dependency update tools** (Renovate, Dependabot)
- **Support for additional tools** as they're added to the project
