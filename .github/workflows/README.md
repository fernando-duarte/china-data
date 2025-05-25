# GitHub Actions Workflows Documentation

This directory contains the CI/CD workflows for the China Economic Data Analysis project. This document provides comprehensive information about each workflow, their triggers, requirements, and optimization strategies.

## 📋 Workflow Overview

| Workflow | File | Lines | Purpose | Status |
|----------|------|-------|---------|--------|
| Main CI | `ci.yml` | 377 | Code quality, testing, security | ✅ Active |
| Release | `release.yml` | 436 | Automated releases with dual archives | ✅ Active |
| Dependency Security | `dependency-check.yml` | 371 | Security audits and compliance | ✅ Active |
| Automated Updates | `dependency-update.yml` | 531 | Intelligent dependency management | ✅ Active |
| Auto-Assignment | `auto-assign.yml` | 53 | PR/issue management | ✅ Active |

## 🚀 Workflow Details

### 1. Main CI Pipeline (`ci.yml`)

**Purpose:** Comprehensive code quality, testing, and security validation

**Triggers:**
```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  workflow_dispatch:  # Manual trigger
```

**Jobs Execution Flow:**
1. **Code Quality** (Ubuntu, Python 3.11)
   - Black formatting check (120-char limit)
   - isort import sorting validation
   - flake8 linting with comprehensive rules
   - pylint advanced analysis
   - mypy type checking (non-blocking)

2. **Test Suite** (Matrix: 3 OS × 5 Python versions = 15 combinations)
   - pytest with coverage reporting
   - 80% minimum coverage enforcement
   - HTML coverage reports as artifacts
   - Codecov integration

3. **Security Scan** (Ubuntu, Python 3.11)
   - Bandit security analysis with JSON output
   - Security report artifacts

4. **Integration Tests** (Ubuntu, Python 3.11, main/develop only)
   - End-to-end pipeline validation with mocked data
   - Data integrity validation
   - Import functionality testing

5. **Documentation** (Ubuntu, Python 3.11)
   - Automatic API documentation generation
   - Module documentation extraction

**Artifacts Generated:**
- `flake8-report` - Linting results
- `coverage-html-report` - HTML coverage reports
- `security-reports` - Bandit security analysis
- `documentation` - Generated API docs

### 2. Release Automation (`release.yml`)

**Purpose:** Automated release creation with dual archive system

**Triggers:**
```yaml
on:
  push:
    tags: ['v*']         # Version tags (e.g., v1.0.0)
  workflow_dispatch:     # Manual with version input
    inputs:
      version:           # Version string (e.g., v1.0.0)
```

**Jobs Execution Flow:**
1. **Validate Release**
   - Branch validation (main/master only)
   - Version extraction and validation
   - Full test suite execution
   - Code quality validation

2. **Build Release Artifacts**
   - Documentation generation
   - Full pipeline archive creation
   - Data-only archive creation (public access)
   - Changelog generation from git commits

3. **Create GitHub Release**
   - Release creation with comprehensive notes
   - Asset upload (full + data-only archives)
   - Version manifest attachment

**Special Features:**
- **Dual Release System:**
  - `china-data-{version}.tar.gz/.zip` - Full pipeline
  - `china-data-only-{version}.tar.gz/.zip` - Data only (public access)
- **Branch Protection:** Enforces releases only from main/master
- **Public Access:** Data-only releases downloadable without GitHub account

**Artifacts Generated:**
- `release-artifacts` - All release files and documentation

### 3. Dependency Security Management (`dependency-check.yml`)

**Purpose:** Comprehensive security auditing and compliance checking

**Triggers:**
```yaml
on:
  workflow_dispatch:     # Manual trigger only
```

**Jobs Execution Flow:**
1. **Dependency Audit** (Ubuntu, Python 3.11)
   - Bandit security analysis
   - Dependency tree generation
   - Outdated package detection

2. **License Check** (Ubuntu, Python 3.11)
   - License compatibility analysis
   - Problematic license detection (GPL, AGPL, etc.)
   - License report generation

3. **Compatibility Test** (Matrix: 5 Python versions)
   - Cross-version dependency installation
   - Import capability testing
   - Deprecation warning detection

4. **Update Check** (Ubuntu, Python 3.11)
   - Outdated dependency identification
   - Automated issue creation for updates

5. **Security Advisory** (Ubuntu, Python 3.11)
   - Local security analysis
   - Package version documentation

6. **Summary** (Ubuntu, aggregates all results)
   - Comprehensive report generation
   - Recommendation compilation

**Artifacts Generated:**
- `security-audit-reports` - Bandit and dependency analysis
- `license-reports` - License compliance data
- `dependency-update-report` - Available updates
- `security-advisory-report` - Security analysis
- `dependency-check-summary` - Consolidated summary

### 4. Automated Dependency Updates (`dependency-update.yml`)

**Purpose:** Intelligent dependency management with security validation

**Triggers:**
```yaml
on:
  workflow_dispatch:
    inputs:
      update_type:       # patch, minor, major
      target_python:     # 3.9, 3.10, 3.11, 3.12, 3.13
```

**Jobs Execution Flow:**
1. **Check Dependencies** (Ubuntu, configurable Python)
   - Update availability detection
   - Security issue identification
   - Update summary generation

2. **Test Updated Dependencies** (Matrix: 3 OS × 5 Python versions)
   - Dependency update testing
   - Core functionality validation
   - Import capability verification

3. **Create Update PR** (Ubuntu, configurable Python)
   - requirements.txt updates
   - Comprehensive PR creation with summaries
   - Security status integration

4. **Notify on Failure** (Ubuntu, on failure)
   - Automated issue creation
   - Failure analysis and recommendations

**Smart Features:**
- **Update Type Control:** Granular patch/minor/major updates
- **Conflict Detection:** Smart dependency resolution
- **Security Validation:** Pre-update vulnerability assessment
- **Multi-Platform Testing:** 15 platform combinations

**Artifacts Generated:**
- `dependency-analysis-{run_number}` - Analysis reports

### 5. Auto-Assignment and Labeling (`auto-assign.yml`)

**Purpose:** Automated PR and issue management

**Triggers:**
```yaml
on:
  pull_request:
    types: [opened, ready_for_review, reopened]
  issues:
    types: [opened]
```

**Jobs Execution Flow:**
1. **Auto-Assignment**
   - PR/issue assignment to maintainers
   - Configuration-based reviewer selection

2. **File-Based Labeling** (PR only)
   - Automatic labeling based on changed files
   - Category-based classification

3. **Size Labeling** (PR only)
   - PR size calculation and labeling
   - XS (<10), S (<100), M (<500), L (<1000), XL (1000+)

**Configuration Files:**
- `.github/auto-assign-config.yml` - Assignment rules
- `.github/labeler.yml` - File-based labeling rules

## 🔧 Required Secrets

### Essential Secrets
**None required** - All workflows use the automatically provided `GITHUB_TOKEN`

### Optional Secrets
```yaml
# For enhanced coverage reporting
CODECOV_TOKEN=your_codecov_token_here
```

**How to Add Secrets:**
1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add secret name and value
4. Save

## 🎯 Workflow Triggers Explained

### Automatic Triggers
- **Push to main/develop:** Triggers main CI pipeline
- **Pull Requests:** Triggers CI pipeline + auto-assignment
- **Version Tags (v*):** Triggers release workflow
- **Issue Creation:** Triggers auto-assignment

### Manual Triggers
- **Dependency Security Check:** On-demand security auditing
- **Dependency Updates:** Configurable update management
- **Release Creation:** Manual release with version input
- **CI Pipeline:** Manual testing and validation

### Trigger Optimization
- **Conditional Execution:** Jobs run only when relevant files change
- **Branch Filtering:** Integration tests only on main/develop
- **Path-Based Filtering:** Reduces unnecessary workflow runs

## 📊 Performance Optimization Tips

### 1. Caching Strategy
**Current Implementation:**
```yaml
- name: Cache dependencies
  uses: actions/cache@v4
  with:
    path: |
      ~/.cache/pip
      ~/.local/lib/python*/site-packages
    key: ${{ runner.os }}-python-${{ matrix.python-version }}-${{ hashFiles('**/requirements*.txt') }}
```

**Benefits:**
- 30-50% reduction in build time
- Intelligent cache invalidation
- Cross-platform optimization

### 2. Matrix Optimization
**Current Strategy:**
- **Full Matrix (15 combinations):** For critical testing
- **Single Platform:** For code quality and documentation
- **Conditional Execution:** Based on branch and file changes

### 3. Job Dependencies
**Parallel Execution:**
- Code quality, security, and tests run in parallel
- Integration tests depend on successful basic tests
- Documentation builds independently

### 4. Artifact Management
**Efficient Storage:**
- JSON reports for programmatic analysis
- HTML reports for human review
- Automatic cleanup of old artifacts

## 🐛 Troubleshooting Guide

### Common Issues and Solutions

#### 1. Test Failures
**Symptoms:** Red X on test jobs
**Investigation:**
```bash
# Local debugging
pytest tests/ -v --tb=long
python3.11 -m pytest tests/  # Match CI Python version
```

**Common Causes:**
- Python version compatibility issues
- Missing test dependencies
- Environment-specific failures

#### 2. Coverage Failures
**Symptoms:** Coverage below 80% threshold
**Investigation:**
```bash
# Local coverage check
pytest tests/ --cov=. --cov-report=html
coverage report --show-missing
```

**Solutions:**
- Add tests for uncovered code
- Remove dead code
- Update coverage configuration

#### 3. Security Scan Issues
**Symptoms:** Bandit reports security vulnerabilities
**Investigation:**
```bash
# Local security scan
bandit -r . --exclude "./venv/*,./tests/*"
```

**Solutions:**
- Review and fix security issues
- Add bandit exclusions for false positives
- Update vulnerable dependencies

#### 4. Dependency Conflicts
**Symptoms:** pip installation failures
**Investigation:**
```bash
# Check dependency tree
pip install pipdeptree
pipdeptree --warn=fail
```

**Solutions:**
- Use pip-tools for dependency resolution
- Pin conflicting package versions
- Update requirements files

#### 5. Release Failures
**Symptoms:** Release workflow fails
**Common Causes:**
- Tag created from wrong branch
- Test failures in validation
- Missing release artifacts

**Solutions:**
- Ensure tag is from main/master branch
- Fix failing tests before release
- Check artifact generation steps

### Debug Mode
**Enable detailed logging:**
```yaml
env:
  ACTIONS_STEP_DEBUG: true
  ACTIONS_RUNNER_DEBUG: true
```

### Artifact Analysis
**Download artifacts for analysis:**
1. Go to failed workflow run
2. Scroll to "Artifacts" section
3. Download relevant reports
4. Analyze locally

## 🔒 Security Best Practices

### 1. Permissions
**Principle of Least Privilege:**
```yaml
permissions:
  contents: read          # Read repository contents
  security-events: write  # Write security scan results
  pull-requests: write    # Comment on PRs
  checks: write          # Update check status
```

### 2. Secret Management
- Use repository secrets for sensitive data
- Never log secret values
- Rotate secrets regularly
- Use environment-specific secrets

### 3. Supply Chain Security
- Pin action versions to specific commits
- Regular dependency audits
- Automated vulnerability scanning
- License compliance monitoring

## 📈 Monitoring and Alerts

### Workflow Status
**Monitor via:**
- GitHub Actions dashboard
- Email notifications (in repository settings)
- Status badges in README.md
- Slack/Discord integrations (if configured)

### Performance Metrics
**Track:**
- Build time trends
- Cache hit rates
- Test execution time
- Coverage trends

### Security Monitoring
**Monitor:**
- Vulnerability scan results
- License compliance status
- Dependency update success rates
- Security advisory notifications

## 🔄 Maintenance Schedule

### Weekly
- Review failed workflow runs
- Check security scan results
- Monitor dependency update PRs

### Monthly
- Review workflow performance metrics
- Update action versions if needed
- Analyze coverage trends

### Quarterly
- Comprehensive security audit
- Performance optimization review
- Documentation updates

## 🚀 Advanced Configuration

### Custom Workflow Variables
```yaml
env:
  PYTHONUNBUFFERED: "1"    # Immediate output
  FORCE_COLOR: "1"         # Colored output
  PIP_CACHE_DIR: ~/.cache/pip
```

### Matrix Customization
```yaml
strategy:
  fail-fast: false          # Continue other jobs on failure
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    python-version: ["3.9", "3.10", "3.11", "3.12", "3.13"]
    include:
      - os: ubuntu-latest
        python-version: "3.11"
        coverage: true       # Only run coverage on one combination
```

### Conditional Job Execution
```yaml
if: github.event_name == 'push' || (github.event_name == 'pull_request' && contains(github.event.pull_request.changed_files, '*.py'))
```

## 📚 Additional Resources

### Documentation
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Python CI/CD Best Practices](https://docs.python.org/3/distributing/)
- [Security Best Practices](https://docs.github.com/en/actions/security-guides)

### Tools Used
- **Black:** Code formatting with 120-character line limit
- **isort:** Import sorting with black compatibility
- **flake8:** Linting with comprehensive rules
- **pylint:** Advanced code analysis
- **mypy:** Optional type checking
- **pytest:** Testing framework with coverage
- **Bandit:** Security analysis
- **Codecov:** Coverage tracking and trends

---

**Documentation Version:** 1.0  
**Last Updated:** January 2025  
**Workflows Covered:** 5/5  
**Status:** ✅ Complete and Operational 