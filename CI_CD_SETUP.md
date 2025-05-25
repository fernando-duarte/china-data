# CI/CD Setup for China Data Processing Pipeline

This document describes the comprehensive CI/CD implementation for the China Data Processing Pipeline using GitHub Actions.

## Overview

The CI/CD pipeline is designed to ensure code quality, reliability, and automated deployment for this economic data processing project. It includes multiple workflows that handle different aspects of the development lifecycle.

## Workflows

### 1. Main CI Workflow (`.github/workflows/ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Manual dispatch

**Jobs:**

#### Code Quality
- **Black** formatting check
- **isort** import sorting check
- **flake8** linting
- **pylint** code analysis
- **mypy** type checking

#### Test Suite
- **Matrix testing** across:
  - OS: Ubuntu, Windows, macOS
  - Python versions: 3.8, 3.9, 3.10, 3.11
- **pytest** with coverage reporting
- **Codecov** integration for coverage tracking

#### Security Scanning
- **Safety** check for known vulnerabilities
- **Bandit** security linter

#### Integration Tests
- Mock-based testing of data downloader
- End-to-end processor testing
- Runs only on main/develop branches

#### Documentation Building
- Automatic API documentation generation
- Module documentation extraction

### 2. Release Workflow (`.github/workflows/release.yml`)

**Triggers:**
- Git tags matching `v*` pattern
- Manual dispatch with version input

**Features:**
- **Release validation** with full test suite
- **Branch protection** - only releases from `main` branch
- **Artifact building** with documentation
- **Changelog generation** from git commits
- **GitHub release creation** with assets

### 3. Dependency Management (`.github/workflows/dependency-check.yml`)

**Triggers:**
- Weekly schedule (Mondays at 9 AM UTC)
- Changes to requirements files
- Manual dispatch

**Features:**
- **Security auditing** with multiple tools
- **License compliance** checking
- **Dependency analysis** and reporting
- **Automated PR creation** for dependency updates

### 4. Performance Testing (`.github/workflows/performance.yml`)

**Triggers:**
- Push/PR to main/develop branches
- Weekly schedule (Sundays at 6 AM UTC)
- Manual dispatch with full suite option

**Features:**
- **Data integrity validation**
- **Performance benchmarking**
- **Memory usage monitoring**
- **Regression testing** for PRs
- **Scalability analysis**

## Setup Instructions

### 1. Repository Configuration

#### Required Secrets
No additional secrets are required for basic functionality. The workflows use `GITHUB_TOKEN` which is automatically provided.

#### Optional Enhancements
For enhanced functionality, you may want to add:

```bash
# For Codecov integration (optional)
CODECOV_TOKEN=your_codecov_token

# For enhanced security scanning (optional)
SNYK_TOKEN=your_snyk_token
```

#### Branch Protection Rules
Configure branch protection for `main` and `develop`:

```yaml
# Recommended settings
required_status_checks:
  - "Code Quality"
  - "Test Suite (ubuntu-latest, 3.11)"
  - "Security Scan"
enforce_admins: true
required_pull_request_reviews:
  required_approving_review_count: 1
  dismiss_stale_reviews: true
```

### 2. Issue Templates

The setup includes structured issue templates:
- **Bug reports** with economic data context
- **Feature requests** with implementation details

### 3. Pull Request Template

Comprehensive PR template covering:
- Data processing impact assessment
- Performance considerations
- Security implications

## Usage Guide

### Running Tests Locally

```bash
# Install development dependencies
pip install -r dev-requirements.txt

# Run the full test suite
make test

# Run code quality checks
make lint
make format

# Run specific test categories
pytest tests/data_integrity/ -v
pytest tests/processor/ -v
```

### Creating a Release

**🔒 Important: Releases must be created from the `main` branch only!**

1. **Switch to main branch and prepare:**
   ```bash
   # Ensure you're on main branch  
   git checkout main
   git pull origin main
   
   # Ensure all tests pass
   make test
   
   # Update version in relevant files and commit
   git commit -m "Prepare release v1.0.0"
   git push origin main
   ```

2. **Create and push tag FROM MAIN:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. **Monitor the release workflow:**
   - ✅ Validates tag is from main branch
   - ✅ Runs full test suite
   - ✅ Creates both full and data-only releases
   - ✅ Publishes to GitHub Releases

### **⚠️ What Happens if You Tag From Wrong Branch**

```bash
# ❌ This will FAIL:
git checkout feature-branch
git tag v1.0.0 && git push origin v1.0.0

# Error message:
# "Release tags must be created from main/master branch"
```

Each release will create **two sets of archives**:
- **Full pipeline:** `china-data-v1.0.0.tar.gz` & `.zip` (complete codebase)
- **Data only:** `china-data-only-v1.0.0.tar.gz` & `.zip` (just the output data files)

### **🌐 Public Access & Sharing**

Since this is a **public repository**, all releases are publicly accessible:

- ✅ **Direct download links** can be shared with anyone
- ✅ **No GitHub account required** for downloading
- ✅ **Perfect for academic collaboration** and research sharing
- ✅ **Stable URLs** for citations and references

**Example download URLs:**
```
https://github.com/owner/repo/releases/download/v1.0.0/china-data-only-v1.0.0.zip
https://github.com/owner/repo/releases/download/v1.0.0/china-data-v1.0.0.tar.gz
```

### Manual Workflow Triggers

#### Performance Testing
```bash
# Trigger via GitHub UI or API
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/owner/repo/actions/workflows/performance.yml/dispatches \
  -d '{"ref":"main","inputs":{"run_full_suite":"true"}}'
```

#### Dependency Updates
```bash
# Trigger dependency check manually
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/owner/repo/actions/workflows/dependency-check.yml/dispatches \
  -d '{"ref":"main"}'
```

## Monitoring and Maintenance

### Workflow Status

Monitor workflow health through:
- GitHub Actions dashboard
- Email notifications (configure in GitHub settings)
- Status badges in README

### **📋 Status Badges for Public Repository**

Consider adding these badges to your README.md for public visibility:

```markdown
![CI](https://github.com/owner/repo/workflows/CI/badge.svg)
![Release](https://github.com/owner/repo/workflows/Release/badge.svg)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/owner/repo)
![GitHub Downloads](https://img.shields.io/github/downloads/owner/repo/total)
```

These badges show:
- ✅ Current CI status
- 📦 Latest release version  
- 📥 Total download counts
- 🔄 Build health

### Performance Metrics

The performance workflow tracks:
- **Data loading time** (threshold: 5 seconds)
- **Processing time** (threshold: 10 seconds)
- **Memory usage** (threshold: 500 MB increase)

### Security Monitoring

Regular security scans check for:
- Known vulnerabilities in dependencies
- Code security issues
- License compliance

### Dependency Management

Automated dependency updates:
- Run weekly on Mondays
- Create PRs for review
- Include security scan results

## Troubleshooting

### Common Issues

#### Test Failures in CI
```bash
# Check specific test output
pytest tests/ -v --tb=long

# Run tests with same Python version as CI
python3.11 -m pytest tests/
```

#### Performance Regression
```bash
# Run local performance tests
python -m pytest tests/ --benchmark-only

# Check memory usage
python -m memory_profiler your_script.py
```

#### Dependency Conflicts
```bash
# Check dependency tree
pip install pipdeptree
pipdeptree --warn=fail

# Resolve conflicts
pip-compile requirements.in --upgrade
```

### Workflow Debugging

#### Enable Debug Logging
Add to workflow environment:
```yaml
env:
  ACTIONS_STEP_DEBUG: true
  ACTIONS_RUNNER_DEBUG: true
```

#### Check Artifact Outputs
Download and inspect:
- Test reports
- Coverage reports
- Performance benchmarks
- Security scan results

## Best Practices

### Code Quality
- Always run `make format` before committing
- Address linting issues promptly
- Maintain test coverage above 80%

### Performance
- Monitor performance metrics in PRs
- Profile code changes that affect data processing
- Use appropriate data structures for large datasets

### Security
- Review dependency update PRs carefully
- Address security scan findings promptly
- Keep dependencies up to date

### Documentation
- Update documentation with code changes
- Use clear commit messages
- Include examples in docstrings

## Integration with Development Workflow

### Pre-commit Hooks (Recommended)

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
EOF

# Install hooks
pre-commit install
```

### IDE Integration

Configure your IDE to use the same tools:
- Black for formatting
- isort for import sorting
- flake8 for linting
- mypy for type checking

This ensures consistency between local development and CI.

## Customization

### Adding New Workflows

1. Create new workflow file in `.github/workflows/`
2. Follow existing patterns for:
   - Python setup
   - Dependency caching
   - Artifact handling

### Modifying Existing Workflows

1. Test changes in a feature branch
2. Monitor workflow runs carefully
3. Update documentation accordingly

### Environment-Specific Configuration

Use workflow inputs and environment variables for:
- Different test configurations
- Environment-specific settings
- Feature flags

## Release Types

### Full Pipeline Release
- **Archives:** `china-data-{version}.tar.gz` and `china-data-{version}.zip`
- **Contents:** Complete source code, tests, documentation, and setup scripts
- **Target users:** Developers, researchers who want to modify the pipeline
- **Use cases:** Running the pipeline, customizing processing, contributing to development

### Data-Only Release  
- **Archives:** `china-data-only-{version}.tar.gz` and `china-data-only-{version}.zip`
- **Contents:** Just the processed economic data files
  - `china_data_raw.md` - Raw data from World Bank, Penn World Table, IMF
  - `china_data_processed.csv` - Processed data in CSV format
  - `china_data_processed.md` - Processed data with methodology notes
  - `README.md` - Data documentation and usage guide
- **Target users:** Researchers, analysts who just need the data
- **Use cases:** Economic analysis, data visualization, research input
- **🌐 Publicly accessible:** Anyone can download these data files directly

### **📋 Academic & Research Use**

With the repository now public, the data releases are ideal for:

- **📚 Academic Research:** Direct download links for papers and studies
- **🎓 Teaching:** Professors can share data links with students
- **📊 Policy Analysis:** Government and NGO researchers can access current data
- **📰 Journalism:** Economic reporters can download latest indicators
- **🔬 Reproducible Research:** Stable URLs ensure long-term accessibility

### **📖 Citation Guidelines**

When using the public data releases, users should cite:
1. **Original data sources** (World Bank WDI, Penn World Table, IMF)
2. **This processed dataset** with version and release date
3. **DOI or GitHub release URL** for reproducibility

This CI/CD setup provides a robust foundation for maintaining code quality, ensuring reliability, and automating deployment processes for the China Data Processing Pipeline. 


---


1. **`.github/workflows/ci.yml`** - Main CI pipeline with:
   - Code quality checks (black, isort, flake8, pylint, mypy)
   - Matrix testing across Python 3.8-3.11 and multiple OS
   - Security scanning (safety, bandit)
   - Integration tests with mocked external APIs
   - Coverage reporting and documentation generation

2. **`.github/workflows/release.yml`** - Release automation with:
   - Release validation and artifact building
   - Automatic changelog generation
   - GitHub release creation with downloadable archives
   - Data-only releases for direct data consumption


3. **`.github/workflows/dependency-check.yml`** - Dependency management with:
   - Weekly security audits
   - License compliance checking
   - Automated dependency update PRs
   - Comprehensive dependency analysis





8. **`CI_CD_SETUP.md`** - Complete documentation covering:
   - Setup instructions and configuration
   - Usage guidelines and best practices
   - Troubleshooting and monitoring
