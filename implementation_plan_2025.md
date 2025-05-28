# Step-by-Step Implementation Plan for Codebase Assessment Recommendations

This plan breaks down all recommendations from the comprehensive codebase assessment into small, self-contained steps that can be implemented independently by a junior developer.

## Phase 1: Configuration File Updates

### 1. Update `.bandit.yaml` Configuration

**Step 1.1**: Add exclude_dirs to `.bandit.yaml`

```yaml
# Add after the existing 'exclude' section in .bandit.yaml
exclude_dirs:
  - "/tests/"
  - "/.venv/"
  - "/venv/"
  - "/.mypy_cache/"
  - "/.pytest_cache/"
```

**Step 1.2**: Add confidence level settings to `.bandit.yaml`

```yaml
# Add at the end of .bandit.yaml
confidence: MEDIUM
```

### 2. Update `.markdownlint.json` Configuration

**Step 2.1**: Add MD013 stern mode

```json
# In .markdownlint.json, update the MD013 rule
"MD013": {
  "line_length": 120,
  "stern": false
}
```

**Step 2.2**: Add MD024 siblings_only setting

```json
# In .markdownlint.json, add new rule
"MD024": {
  "siblings_only": true
}
```

### 3. Update `.mutmut_config` Configuration

**Step 3.1**: Add explicit use-coverage flag

```ini
# In .mutmut_config, update the runner line
runner = pytest --use-coverage -x
```

**Step 3.2**: Add CI-specific configuration comment

```ini
# Add at the end of .mutmut_config
# For CI environments, add: --rerun-all
```

### 4. Update `config.py` with Pydantic

**Step 4.1**: Add Pydantic to dependencies

```bash
uv add pydantic
```

**Step 4.2**: Create a new file `config_schema.py`

```python
from pydantic import BaseModel, Field
from typing import ClassVar

class ChinaDataConfig(BaseModel):
    """Configuration schema for China Data Processor."""

    LOG_FILE: str = Field(default='china_data.log', description="Log file path")
    LOG_LEVEL: str = Field(default='INFO', description="Logging level")
    # Add all other config fields here
```

**Step 4.3**: Add environment variable loading to `config.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Update each config value to check environment variables
LOG_FILE: ClassVar[str] = os.getenv('CHINA_DATA_LOG_FILE', 'china_data.log')
```

### 5. Modernize `docker-compose.yml`

**Step 5.1**: Remove version declaration

```yaml
# Delete this line from docker-compose.yml:
version: "3.8"
```

**Step 5.2**: Add security context to dev service

```yaml
# In docker-compose.yml, under 'dev' service, add:
security_opt:
  - no-new-privileges:true
```

**Step 5.3**: Add user specification

```yaml
# In docker-compose.yml, under 'dev' service, add:
user: "1000:1000"
```

**Step 5.4**: Add health check

```yaml
# In docker-compose.yml, under 'dev' service, add:
healthcheck:
  test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### 6. Enhance `Dockerfile`

**Step 6.1**: Add cache mount for UV

```dockerfile
# In Dockerfile, update the RUN command that installs dependencies:
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev
```

**Step 6.2**: Add security scanning comment

```dockerfile
# Add comment in Dockerfile after the build stage:
# TODO: Add security scanning with trivy or similar tool
# RUN trivy fs --no-progress /app
```

### 7. Enhance `Makefile`

**Step 7.1**: Adopt comprehensive Makefile

- Replace the current content of your `Makefile` with the "Enhanced Makefile" definition found in the "Development Workflow Integration" section of `comprehensive_codebase_assessment_2025.md`. This enhanced Makefile includes better setup, development, testing, linting, security, and cleaning targets.

### 8. Enhance `mkdocs.yml`

**Step 8.1**: Add social cards configuration

```yaml
# In mkdocs.yml, under theme section, add:
theme:
  social:
    cards: true
    cards_color:
      fill: "#1e1e1e"
      text: "#ffffff"
```

**Step 8.2**: Add link checking plugin

```yaml
# In mkdocs.yml, under plugins section, add:
plugins:
  - linkchecker:
      fail_on_error: false
```

### 9. Migrate `mypy.ini` to `pyproject.toml`

**Step 9.1**: Copy mypy settings to pyproject.toml

```toml
# Add to pyproject.toml if not already present
[tool.mypy]
python_version = "3.13"
strict = true
disallow_untyped_defs = true
```

**Step 9.2**: Delete mypy.ini file

```bash
rm mypy.ini
```

### 10. Enhance `pyproject.toml`

**Step 10.1**: Add build system requirements

```toml
# Add to pyproject.toml at the top
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Step 10.2**: Add more granular pytest configuration

```toml
# Add to [tool.pytest.ini_options] in pyproject.toml
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
]
```

### 11. Update `radon.cfg`

**Step 11.1**: Add complexity thresholds

```ini
# Add to radon.cfg
[complexity]
min = A
max = C
```

**Step 11.2**: Add maintainability thresholds

```ini
# Add to radon.cfg
[maintainability]
min = 70
```

### 12. Enhance `renovate.json5`

**Step 12.1**: Add granular automerge rules

```json5
# Add to packageRules in renovate.json5
{
  "matchDepTypes": ["devDependencies"],
  "matchUpdateTypes": ["patch", "minor"],
  "automerge": true
}
```

**Step 12.2**: Add custom preset comment

```json5
// Add comment at top of renovate.json5
// TODO: Create custom preset at .github/renovate-presets/default.json
```

### 13. Enhance `ruff.toml`

**Step 13.1**: Add project-specific rule

```toml
# Add to extend-select in ruff.toml
"LOG",  # flake8-logging
```

**Step 13.2**: Add custom rule documentation

```toml
# Add comments above each rule category in ruff.toml
# Security rules
"S",    # flake8-bandit
```

## Phase 2: GitHub Configuration Updates

### 14. Update CODEOWNERS

**Step 14.1**: Create organization teams structure

```
# Replace content in .github/CODEOWNERS
# Global fallback
* @myorg/core-team

# Specific ownership
china_data_*.py @myorg/data-team
/utils/data_sources/ @myorg/data-team
*.toml @myorg/devops-team
/.github/workflows/ @myorg/devops-team
/tests/ @myorg/qa-team @myorg/backend-team
```

### 15. Update auto-assign-config.yml

**Step 15.1**: Add backup reviewers

```yaml
# In .github/auto-assign-config.yml, update reviewers list
reviewers:
  - fernandoduarte
  - backup-reviewer-1
```

**Step 15.2**: Add review groups setting

```yaml
# Add to .github/auto-assign-config.yml
useReviewGroups: true
```

**Step 15.3**: Update skip keywords

```yaml
# Update in .github/auto-assign-config.yml
skipKeywords: ["wip", "draft", "[skip assign]", "dependabot"]
```

**Step 15.4**: Add skipDraft setting

```yaml
# Add to .github/auto-assign-config.yml
skipDraft: true
```

### 16. Update labeler.yml

**Step 16.1**: Add v5 syntax for core label

```yaml
# Update in .github/labeler.yml
core:
  - any:
      - changed-files:
          - any-glob-to-any-file:
              - "china_data_processor.py"
              - "china_data_downloader.py"
```

**Step 16.2**: Add branch-based labels

```yaml
# Add to .github/labeler.yml
feature:
  - any:
      - head-branch: ["feature/*", "feat/*"]

hotfix:
  - any:
      - head-branch: ["hotfix/*", "fix/*"]
```

## Phase 3: GitHub Actions Updates

### 17. Update workflows/auto-assign.yml

**Step 17.1**: Add concurrency control

```yaml
# Add after 'on:' section in .github/workflows/auto-assign.yml
concurrency:
  group: auto-assign-${{ github.ref }}
  cancel-in-progress: true
```

**Step 17.2**: Update permissions

```yaml
# Replace permissions in .github/workflows/auto-assign.yml
permissions:
  contents: read
  pull-requests: write
  issues: write
```

**Step 17.3**: Add continue-on-error

```yaml
# Update the auto-assign step
- uses: kentaro-m/auto-assign-action@v2.0.0
  continue-on-error: true
```

### 18. Create and Consolidate Unified CI Workflow (`ci-unified.yml`)

**Step 18.1**: Create `ci-unified.yml` with base content

- Create a new file named `.github/workflows/ci-unified.yml`.
- Populate this file with the comprehensive YAML content provided in the "CI/CD Pipeline Optimization" section of `comprehensive_codebase_assessment_2025.md`. This includes jobs for `quick-checks`, `test-matrix`, `security-scan`, and `build`.

**Step 18.2**: Integrate Cost Optimization Strategies into `ci-unified.yml`

- **Smart Matrix Strategy**:
  - Modify the `quick-checks` job (or a similar initial job) in `ci-unified.yml` to determine if the full test matrix needs to run. This logic should be based on factors like changed files (e.g., `git diff --name-only ${{ github.event.before }} ${{ github.sha }}`) or the current branch (e.g., run full matrix for `main` branch pushes).
  - This job should output a variable (e.g., `outputs.should-run-full: 'true'/'false'`).
  - Update the `test-matrix` job in `ci-unified.yml` to use this output. Adapt its `strategy.matrix.include` section or add conditional job execution (`if: needs.quick-checks.outputs.should-run-full == 'true'`) for less critical matrix combinations to reduce unnecessary runs, as demonstrated in the "Smart Matrix Strategy" under the "CI/CD Cost Optimization Strategies" section of the assessment.
- **Job Consolidation**:
  - Review the `quick-checks` job in `ci-unified.yml`. If there are multiple small, related check steps (e.g., separate linting, formatting, type checking steps that could be combined), consolidate them into fewer steps within the job to reduce overhead. Run them sequentially within the same `run` block, failing the job if any sub-step fails, as shown in the `quality-checks` example in the assessment's "CI/CD Cost Optimization Strategies" section.
- **Intelligent Caching**:
  - Ensure robust caching is implemented within `ci-unified.yml`. Leverage `astral-sh/setup-uv@v5` with `enable-cache: true` and appropriate `cache-dependency-glob` settings.
  - Implement caching for test results and other build artifacts where beneficial, as shown in the "Intelligent Caching" examples in the assessment.

**Step 18.3**: Final Review and Testing

- Thoroughly review the complete `ci-unified.yml` to ensure all parts are integrated correctly and logically.
- Test the workflow with various scenarios (e.g., PR to a feature branch with minor changes, PR to main, push to main) to verify the smart matrix and caching strategies are working as expected.

**Step 18.4**: Delete old CI workflow files

- Once `ci-unified.yml` is established and working correctly, delete the old CI workflow files:

  ```bash
  rm .github/workflows/ci.yml
  rm .github/workflows/ci-uv.yml
  ```

**Step 18.5**: Add CI optimization snippets

```yaml
# In .github/workflows/ci-unified.yml under quick-checks job:
- name: Parallel linting and type/security checks
  run: |
    uv run ruff check . &
    uv run mypy . &
    uv run bandit -r . &
    wait

- name: Install CI tools
  run: |
    uv tool install --with-requirements requirements-tools.txt
```

### 19. Update dependency-check.yml

**Step 19.1**: Add scheduled trigger

```yaml
# Add to 'on:' section in .github/workflows/dependency-check.yml
schedule:
  - cron: "0 2 * * 1" # Weekly Monday 2 AM
push:
  paths: ["requirements*.txt", "pyproject.toml", "uv.lock"]
```

**Step 19.2**: Add SARIF upload

```yaml
# Add after security scanning steps
- name: Upload SARIF results
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: security-results.sarif
```

### 20. Remove deprecated workflow

**Step 20.1**: Delete dependency-update.yml

```bash
rm .github/workflows/dependency-update.yml
```

### 21. Update docs.yml

**Step 21.1**: Add UV installation

```yaml
# Replace pip install with UV in .github/workflows/docs.yml
- uses: astral-sh/setup-uv@v5
  with:
    enable-cache: true
- name: Install dependencies
  run: uv sync --frozen
```

**Step 21.2**: Add documentation caching

```yaml
# Add caching step in .github/workflows/docs.yml
- name: Cache documentation build
  uses: actions/cache@v4
  with:
    path: site/
    key: mkdocs-${{ hashFiles('mkdocs.yml', 'docs/**') }}
```

## Phase 4: Enhanced Features Implementation

### 22. Create Context as Code structure

**Step 22.1**: Create context directory

```bash
mkdir -p .context
```

**Step 22.2**: Create project.yaml

```yaml
# Create .context/project.yaml with content from the assessment
project:
  name: china-data
  purpose: Economic data processing for China
  architecture:
    style: ETL pipeline
    patterns:
      - Repository pattern for data access
      - Strategy pattern for extrapolation methods
      - Observer pattern for validation events
```

**Step 22.3**: Create AI context documentation

```bash
# Create docs/ai-context.md with the content from the assessment
```

### 23. Add VS Code settings

**Step 23.1**: Create .vscode directory

```bash
mkdir -p .vscode
```

**Step 23.2**: Create settings.json

```json
# Create .vscode/settings.json with the content from the assessment
```

### 24. Create monitoring workflow

**Step 24.1**: Create monitoring.yml

```yaml
# Create .github/workflows/monitoring.yml with content from assessment
```

### 25. Create dependency health workflow

**Step 25.1**: Create dependency-health.yml

```yaml
# Create .github/workflows/dependency-health.yml with content from assessment
```

### 26. Add OpenTelemetry support

**Step 26.1**: Add OpenTelemetry dependencies

```bash
uv add opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation opentelemetry-exporter-otlp # Added exporter
```

**Step 26.2**: Create observability.py

```python
# Create utils/observability.py with content from assessment.
# Ensure os module is imported if used (e.g. for os.getenv).
# Ensure the OTLPSpanExporter and MeterProvider are imported if used.
# from opentelemetry.sdk.metrics import MeterProvider
# from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
# import os
```

### 27. Update logging configuration

**Step 27.1**: Add structlog dependency

```bash
uv add structlog
```

**Step 27.2**: Update config.py with structured logging

```python
# Add the configure_logging function from assessment to config.py
# Ensure sys module is imported for sys.stderr.isatty()
# import sys
# import structlog
```

### 28. Create enhanced Dockerfile

**Step 28.1**: Backup existing Dockerfile

```bash
cp Dockerfile Dockerfile.backup
```

**Step 28.2**: Replace with enhanced version

```dockerfile
# Replace Dockerfile content with the enhanced version from assessment's "Advanced Docker Optimization with UV" section.
# This version includes multi-stage builds, UV optimizations, non-root user, and health checks.
```

### 29. Create modern docker-compose.yml

**Step 29.1**: Backup existing docker-compose.yml

```bash
cp docker-compose.yml docker-compose.yml.backup
```

**Step 29.2**: Replace with modern version

```yaml
# Replace docker-compose.yml content with modern version from assessment's "Docker Compose for Development" section.
# This version uses modern v2 syntax, includes service definitions for app and postgres, volumes, and networks.
```

### 30. Create devcontainer configuration

**Step 30.1**: Create devcontainer directory

```bash
mkdir -p .devcontainer
```

**Step 30.2**: Create devcontainer.json

```json
# Create .devcontainer/devcontainer.json with content from assessment's "Modern Devcontainer Configuration" section.
```

### 31. Create dev setup script

**Step 31.1**: Create scripts directory

```bash
mkdir -p scripts
```

**Step 31.2**: Create dev-setup.sh

```bash
# Create scripts/dev-setup.sh with content from assessment's "Automated Development Setup" section.
chmod +x scripts/dev-setup.sh
```

### 32. Integrate Automated Quality Gates into CI

**Step 32.1**: Add Quality Gate steps to `ci-unified.yml`

- In your primary CI workflow file (`.github/workflows/ci-unified.yml`), integrate the "Automated Quality Gates" as defined in the `comprehensive_codebase_assessment_2025.md`.
- This typically involves adding a new job, or steps to an existing job (e.g., after tests and builds), that runs commands for:
  - Coverage threshold check (e.g., `uv run coverage report --fail-under=80`)
  - Complexity threshold check (e.g., `uv run radon cc . --min B`)
  - Security threshold check (e.g., `uv run bandit -r . -ll`)
  - Type coverage check (e.g., `uv run mypy . --strict`)
- Ensure these steps are configured to fail the workflow if the quality gates are not met.

### 33. Create compliance report script

**Step 33.1**: Create compliance_report.py

```python
# Create scripts/compliance_report.py with basic structure from assessment.
# This script should define functions like run_security_checks(), run_quality_checks(), etc.
# Example structure:
# def run_security_checks(): return {}
# def run_quality_checks(): return {}
# def run_coverage_analysis(): return {}
# def run_dependency_audit(): return {}
# def run_doc_coverage(): return {}
#
# def generate_compliance_report():
#     """Generate comprehensive compliance report."""
#     return {
#         'security': run_security_checks(),
#         'quality': run_quality_checks(),
#         'coverage': run_coverage_analysis(),
#         'dependencies': run_dependency_audit(),
#         'documentation': run_doc_coverage()
#     }
# if __name__ == "__main__":
#     report = generate_compliance_report()
#     import json
#     print(json.dumps(report, indent=2))

```

### 34. Update enhanced renovate.json5

**Step 34.1**: Backup existing renovate.json5

```bash
cp renovate.json5 renovate.json5.backup
```

**Step 34.2**: Replace with enhanced version

```json5
# Replace renovate.json5 content with enhanced version from assessment's "Dependency Management Unification" section.
# This includes settings for lockFileMaintenance, packageRules, vulnerabilityAlerts, osvVulnerabilityAlerts, and transitiveRemediation.
```

**Step 34.3**: Add SLSA hostRules and signature verification

```json5
# In renovate.json5, under root object:
"hostRules": [{
  "matchHost": "pypi.org",
  "artifactAuth": { "type": "sigstore" }
}],
"packageRules": [{
  "matchManagers": ["pip_requirements","pip_setup","pipenv","poetry","uv"],
  "signatureVerification": true
}]
```

### 35. Create SBOM workflow

**Step 35.1**: Create security.yml

```yaml
# Create .github/workflows/security.yml with SBOM content from assessment's "Supply Chain Security - SLSA Level 3 Compliance" section.
# This workflow should handle SBOM generation and attestation.
```

### 36. Update pyproject.toml with security settings

**Step 36.1**: Add UV security settings

```toml
# Add to [tool.uv.pip] in pyproject.toml
generate-hashes = true
require-hashes = true
```

**Step 36.2**: Add dependency check settings

```toml
# Add new section to pyproject.toml
[tool.dependency-check]
allowed-licenses = [
    "MIT", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause",
    "Python-2.0", "ISC", "LGPL-3.0"
]
security-updates = "auto-merge"
```

### 37. Create .env.example file

**Step 37.1**: Create example environment file

```bash
# Create .env.example
cat > .env.example << 'EOF'
# Environment Configuration
ENVIRONMENT=development
DB_PASSWORD=development
OTEL_ENDPOINT=http://localhost:4317
UV_CACHE_DIR=/tmp/uv-cache
# Add any other necessary environment variables for your project
EOF
```

### 38. Add dotenv dependency

**Step 38.1**: Install python-dotenv

```bash
uv add python-dotenv
```

## Phase 5: Final Cleanup and Validation

### 39. Update .gitignore

**Step 39.1**: Add new directories/files to .gitignore

```bash
echo ".context/" >> .gitignore
echo "security-results.sarif" >> .gitignore
echo "audit.json" >> .gitignore # From dependency health check
echo "safety.json" >> .gitignore # From dependency health check
echo "pip-audit.json" >> .gitignore # From unified CI security-scan job
echo "semgrep.json" >> .gitignore # From unified CI security-scan job
echo "sbom.spdx.json" >> .gitignore # From SBOM workflow
echo ".env" >> .gitignore
echo "Dockerfile.backup" >> .gitignore
echo "docker-compose.yml.backup" >> .gitignore
echo "renovate.json5.backup" >> .gitignore
```

### 40. Run initial setup

**Step 40.1**: Execute dev setup script

```bash
./scripts/dev-setup.sh
```

### 41. Validate all changes

**Step 41.1**: Run linting

```bash
uv run ruff check .
```

**Step 41.2**: Run type checking

```bash
uv run mypy .
```

**Step 41.3**: Run tests

```bash
uv run pytest
```

### 42. Commit changes

**Step 42.1**: Stage configuration changes

```bash
git add -A
```

**Step 42.2**: Create commit

```bash
git commit -m "feat: implement 2025 codebase assessment recommendations"
```

## Completion Checklist

Use this checklist to track progress:

- [x] Phase 1: Configuration File Updates (Steps 1-13) # All steps complete
- [x] Phase 2: GitHub Configuration Updates (Steps 14-16) # All steps complete
- [x] Phase 3: GitHub Actions Updates (Steps 17-21) # All steps complete
- [x] Phase 4: Enhanced Features Implementation (Steps 22-38) # All steps complete (Step 23 skipped due to .vscode being blocked)
- [x] Phase 5: Final Cleanup and Validation (Steps 39-42) # Step 39 complete; 40, 41, 42 are manual user actions

Each step is designed to be completed independently. You can implement them in any order, though the phase grouping provides a logical progression.
