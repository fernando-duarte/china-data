#!/usr/bin/env python3
"""Tool Version Synchronization Script

This script ensures that tool versions are synchronized across:
- .pre-commit-config.yaml
- .github/workflows/*.yml
- pyproject.toml

It can be run in check-only mode or update mode.
"""

import argparse
import re
import sys
from pathlib import Path

import yaml


class VersionSynchronizer:
    """Manages version synchronization across configuration files."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.pre_commit_config = repo_root / ".pre-commit-config.yaml"
        self.pyproject_toml = repo_root / "pyproject.toml"
        self.workflows_dir = repo_root / ".github" / "workflows"

        # Define tool version mappings
        self.tool_versions = {
            "pip-audit": {"pre_commit": "v2.7.3", "pyproject": ">=2.7.3,<3.0", "ci_exact": "2.7.3"},
            "detect-secrets": {"pre_commit": "v1.5.0", "pyproject": ">=1.5.0,<2.0", "ci_exact": "1.5.0"},
            "bandit": {
                "pre_commit": None,  # Commented out, uses Ruff
                "pyproject": ">=1.7.0,<2.0",
                "ci_exact": "1.7.0",
            },
            "pyupgrade": {"pre_commit": "v3.19.0", "pyproject": ">=3.19.0,<4.0", "ci_exact": "3.19.0"},
            "prettier": {
                "pre_commit": "v4.0.0-alpha.8",
                "pyproject": None,  # Not a Python package
                "ci_exact": "4.0.0-alpha.8",
            },
            "markdownlint": {
                "pre_commit": "v0.43.0",
                "pyproject": None,  # Not a Python package
                "ci_exact": "0.43.0",
            },
            "radon": {
                "pre_commit": "local",  # Local hook
                "pyproject": ">=6.0.0,<7.0",
                "ci_exact": "6.0.0",
            },
            "interrogate": {
                "pre_commit": "local",  # Local hook
                "pyproject": ">=1.7.0,<2.0",
                "ci_exact": "1.7.0",
            },
            "ruff": {"pre_commit": "v0.11.11", "pyproject": ">=0.11.11,<1.0", "ci_exact": "0.11.11"},
            "pylint": {"pre_commit": "v3.3.1", "pyproject": ">=3.3.1,<4.0", "ci_exact": "3.3.1"},
            "mypy": {"pre_commit": "v1.13.0", "pyproject": ">=1.13.0,<2.0", "ci_exact": "1.13.0"},
        }

    def load_pre_commit_config(self) -> dict:
        """Load pre-commit configuration."""
        with open(self.pre_commit_config) as f:
            return yaml.safe_load(f)

    def load_pyproject_toml(self) -> str:
        """Load pyproject.toml as text (for easier regex manipulation)."""
        with open(self.pyproject_toml) as f:
            return f.read()

    def get_workflow_files(self) -> list[Path]:
        """Get all workflow YAML files."""
        return list(self.workflows_dir.glob("*.yml"))

    def check_pre_commit_versions(self) -> list[str]:
        """Check pre-commit versions against expected values."""
        issues = []
        config = self.load_pre_commit_config()

        for repo in config.get("repos", []):
            repo_url = repo.get("repo", "")
            rev = repo.get("rev", "")

            # Check specific tools
            if "pip-audit" in repo_url:
                expected = self.tool_versions["pip-audit"]["pre_commit"]
                if rev != expected:
                    issues.append(f"pip-audit pre-commit version mismatch: {rev} != {expected}")

            elif "detect-secrets" in repo_url:
                expected = self.tool_versions["detect-secrets"]["pre_commit"]
                if rev != expected:
                    issues.append(f"detect-secrets pre-commit version mismatch: {rev} != {expected}")

            elif "pyupgrade" in repo_url:
                expected = self.tool_versions["pyupgrade"]["pre_commit"]
                if rev != expected:
                    issues.append(f"pyupgrade pre-commit version mismatch: {rev} != {expected}")

            elif "prettier" in repo_url:
                expected = self.tool_versions["prettier"]["pre_commit"]
                if rev != expected:
                    issues.append(f"prettier pre-commit version mismatch: {rev} != {expected}")

            elif "markdownlint" in repo_url:
                expected = self.tool_versions["markdownlint"]["pre_commit"]
                if rev != expected:
                    issues.append(f"markdownlint pre-commit version mismatch: {rev} != {expected}")

            elif "ruff-pre-commit" in repo_url:
                expected = self.tool_versions["ruff"]["pre_commit"]
                if rev != expected:
                    issues.append(f"ruff pre-commit version mismatch: {rev} != {expected}")

            elif "pylint" in repo_url:
                expected = self.tool_versions["pylint"]["pre_commit"]
                if rev != expected:
                    issues.append(f"pylint pre-commit version mismatch: {rev} != {expected}")

            elif "mypy" in repo_url:
                expected = self.tool_versions["mypy"]["pre_commit"]
                if rev != expected:
                    issues.append(f"mypy pre-commit version mismatch: {rev} != {expected}")

        return issues

    def check_pyproject_versions(self) -> list[str]:
        """Check pyproject.toml versions against expected values."""
        issues = []
        content = self.load_pyproject_toml()

        for tool, versions in self.tool_versions.items():
            if versions["pyproject"] is None:
                continue

            # Look for the tool in dev dependencies
            pattern = rf'"{tool}[^"]*"'
            matches = re.findall(pattern, content)

            if not matches:
                issues.append(f"{tool} not found in pyproject.toml dev dependencies")
            else:
                for match in matches:
                    if versions["pyproject"] not in match:
                        issues.append(
                            f"{tool} pyproject.toml version mismatch: {match} should contain {versions['pyproject']}"
                        )

        return issues

    def check_workflow_versions(self) -> list[str]:
        """Check workflow file versions against expected values."""
        issues = []

        for workflow_file in self.get_workflow_files():
            with open(workflow_file) as f:
                content = f.read()

            # Check for hardcoded tool versions in workflows
            for tool, versions in self.tool_versions.items():
                if versions["ci_exact"] is None:
                    continue

                # Look for tool installation commands
                patterns = [
                    rf"uv add --dev {tool}==[0-9.]+",
                    rf'pip install "{tool}==[0-9.]+"',
                    rf"{tool}==[0-9.]+",
                ]

                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if versions["ci_exact"] not in match:
                            issues.append(
                                f"{tool} in {workflow_file.name}: {match} should use version {versions['ci_exact']}"
                            )

        return issues

    def update_pre_commit_config(self) -> bool:
        """Update pre-commit configuration with correct versions."""
        config = self.load_pre_commit_config()
        updated = False

        for repo in config.get("repos", []):
            repo_url = repo.get("repo", "")

            # Update specific tools
            if "pip-audit" in repo_url:
                expected = self.tool_versions["pip-audit"]["pre_commit"]
                if repo.get("rev") != expected:
                    repo["rev"] = expected
                    updated = True

            elif "detect-secrets" in repo_url:
                expected = self.tool_versions["detect-secrets"]["pre_commit"]
                if repo.get("rev") != expected:
                    repo["rev"] = expected
                    updated = True

            elif "pyupgrade" in repo_url:
                expected = self.tool_versions["pyupgrade"]["pre_commit"]
                if repo.get("rev") != expected:
                    repo["rev"] = expected
                    updated = True

            elif "prettier" in repo_url:
                expected = self.tool_versions["prettier"]["pre_commit"]
                if repo.get("rev") != expected:
                    repo["rev"] = expected
                    updated = True

            elif "markdownlint" in repo_url:
                expected = self.tool_versions["markdownlint"]["pre_commit"]
                if repo.get("rev") != expected:
                    repo["rev"] = expected
                    updated = True

            elif "ruff-pre-commit" in repo_url:
                expected = self.tool_versions["ruff"]["pre_commit"]
                if repo.get("rev") != expected:
                    repo["rev"] = expected
                    updated = True

            elif "pylint" in repo_url:
                expected = self.tool_versions["pylint"]["pre_commit"]
                if repo.get("rev") != expected:
                    repo["rev"] = expected
                    updated = True

            elif "mypy" in repo_url:
                expected = self.tool_versions["mypy"]["pre_commit"]
                if repo.get("rev") != expected:
                    repo["rev"] = expected
                    updated = True

        if updated:
            with open(self.pre_commit_config, "w") as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        return updated

    def update_pyproject_toml(self) -> bool:
        """Update pyproject.toml with correct versions."""
        content = self.load_pyproject_toml()
        updated_content = content
        updated = False

        for tool, versions in self.tool_versions.items():
            if versions["pyproject"] is None:
                continue

            # Update version ranges in dev dependencies
            pattern = rf'"{tool}[^"]*"'
            replacement = f'"{tool}{versions["pyproject"]}"'

            new_content = re.sub(pattern, replacement, updated_content)
            if new_content != updated_content:
                updated_content = new_content
                updated = True

        if updated:
            with open(self.pyproject_toml, "w") as f:
                f.write(updated_content)

        return updated

    def generate_ci_workflow_updates(self) -> dict[str, str]:
        """Generate updated CI workflow content."""
        updates = {}

        for workflow_file in self.get_workflow_files():
            with open(workflow_file) as f:
                content = f.read()

            updated_content = content

            # Add missing tools to CI workflows
            if workflow_file.name == "ci.yml":
                updated_content = self._update_main_ci_workflow(updated_content)
            elif workflow_file.name == "security-enhanced.yml":
                updated_content = self._update_security_workflow(updated_content)

            if updated_content != content:
                updates[str(workflow_file)] = updated_content

        return updates

    def _update_main_ci_workflow(self, content: str) -> str:
        """Update main CI workflow with missing tools."""
        # Add pyupgrade step
        if "pyupgrade" not in content:
            pyupgrade_step = """
      - name: Run pyupgrade syntax modernization
        run: |
          uv add --dev pyupgrade=={version}
          uv run pyupgrade --py313-plus china_data_processor.py china_data_downloader.py utils/**/*.py || true
""".format(version=self.tool_versions["pyupgrade"]["ci_exact"])

            # Insert after ruff format check
            content = content.replace(
                "          uv run ruff format --check .", "          uv run ruff format --check ." + pyupgrade_step
            )

        # Add prettier step
        if "prettier" not in content:
            prettier_step = """
      - name: Format YAML and Markdown with prettier
        run: |
          npm install -g prettier@{version}
          prettier --check "**/*.{{yml,yaml,md}}" --ignore-path .gitignore || true
""".format(version=self.tool_versions["prettier"]["ci_exact"])

            # Insert after pyupgrade
            if "pyupgrade" in content:
                content = content.replace(
                    "uv run pyupgrade --py313-plus china_data_processor.py china_data_downloader.py utils/**/*.py || true",
                    "uv run pyupgrade --py313-plus china_data_processor.py china_data_downloader.py utils/**/*.py || true"
                    + prettier_step,
                )

        # Add markdownlint step
        if "markdownlint" not in content:
            markdownlint_step = """
      - name: Lint Markdown files
        run: |
          npm install -g markdownlint-cli@{version}
          markdownlint "**/*.md" --ignore node_modules --ignore .github || true
""".format(version=self.tool_versions["markdownlint"]["ci_exact"])

            # Insert after prettier
            if "prettier" in content:
                content = content.replace(
                    'prettier --check "**/*.{yml,yaml,md}" --ignore-path .gitignore || true',
                    'prettier --check "**/*.{yml,yaml,md}" --ignore-path .gitignore || true' + markdownlint_step,
                )

        # Add radon complexity check
        if "radon" not in content:
            radon_step = """
      - name: Check code complexity with radon
        run: |
          uv add --dev radon=={version}
          uv run radon cc china_data_processor.py china_data_downloader.py utils/ --min B --show-complexity || true
""".format(version=self.tool_versions["radon"]["ci_exact"])

            # Insert after markdownlint
            if "markdownlint" in content:
                content = content.replace(
                    'markdownlint "**/*.md" --ignore node_modules --ignore .github || true',
                    'markdownlint "**/*.md" --ignore node_modules --ignore .github || true' + radon_step,
                )

        # Add interrogate docstring coverage
        if "interrogate" not in content:
            interrogate_step = """
      - name: Check docstring coverage with interrogate
        run: |
          uv add --dev interrogate=={version}
          uv run interrogate china_data_processor.py china_data_downloader.py utils/ --verbose --fail-under=80 || true
""".format(version=self.tool_versions["interrogate"]["ci_exact"])

            # Insert after radon
            if "radon" in content:
                content = content.replace(
                    "uv run radon cc china_data_processor.py china_data_downloader.py utils/ --min B --show-complexity || true",
                    "uv run radon cc china_data_processor.py china_data_downloader.py utils/ --min B --show-complexity || true"
                    + interrogate_step,
                )

        # Update existing tool versions
        for tool, versions in self.tool_versions.items():
            if versions["ci_exact"] is None:
                continue

            # Update hardcoded versions
            patterns = [
                (rf"uv add --dev {tool}==[0-9.]+", f"uv add --dev {tool}=={versions['ci_exact']}"),
                (rf'pip install "{tool}==[0-9.]+"', f'pip install "{tool}=={versions["ci_exact"]}"'),
            ]

            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)

        return content

    def _update_security_workflow(self, content: str) -> str:
        """Update security workflow with pinned versions."""
        # Pin detect-secrets version
        content = re.sub(
            r'uv pip install "detect-secrets[^"]*"',
            f'uv pip install "detect-secrets=={self.tool_versions["detect-secrets"]["ci_exact"]}"',
            content,
        )

        # Ensure bandit is pinned
        if "bandit" in content and "bandit==" not in content:
            content = re.sub(
                r"uv run bandit",
                f"uv add --dev bandit=={self.tool_versions['bandit']['ci_exact']} && uv run bandit",
                content,
            )

        return content

    def run_check(self) -> tuple[bool, list[str]]:
        """Run version synchronization check."""
        all_issues = []

        # Check pre-commit versions
        all_issues.extend(self.check_pre_commit_versions())

        # Check pyproject.toml versions
        all_issues.extend(self.check_pyproject_versions())

        # Check workflow versions
        all_issues.extend(self.check_workflow_versions())

        return len(all_issues) == 0, all_issues

    def run_update(self) -> bool:
        """Run version synchronization update."""
        updated = False

        # Update pre-commit config
        if self.update_pre_commit_config():
            print("✅ Updated .pre-commit-config.yaml")
            updated = True

        # Update pyproject.toml
        if self.update_pyproject_toml():
            print("✅ Updated pyproject.toml")
            updated = True

        # Generate workflow updates
        workflow_updates = self.generate_ci_workflow_updates()
        for workflow_path, new_content in workflow_updates.items():
            with open(workflow_path, "w") as f:
                f.write(new_content)
            print(f"✅ Updated {Path(workflow_path).name}")
            updated = True

        return updated


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Synchronize tool versions across configuration files")
    parser.add_argument("--check-only", action="store_true", help="Only check for version mismatches")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root directory")

    args = parser.parse_args()

    synchronizer = VersionSynchronizer(args.repo_root)

    if args.check_only:
        success, issues = synchronizer.run_check()

        if success:
            print("✅ All tool versions are synchronized!")
            return 0
        print("❌ Version synchronization issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    if synchronizer.run_update():
        print("✅ Tool versions synchronized successfully!")
        return 0
    print("ℹ️ No updates needed - all versions already synchronized")
    return 0


if __name__ == "__main__":
    sys.exit(main())
