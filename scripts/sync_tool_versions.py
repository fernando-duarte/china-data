#!/usr/bin/env python3
"""Tool Version Synchronization Script.

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
from typing import Any

import yaml


class VersionSynchronizer:
    """Manages version synchronization across configuration files."""

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.pre_commit_config = repo_root / ".pre-commit-config.yaml"
        self.pyproject_toml = repo_root / "pyproject.toml"
        self.workflows_dir = repo_root / ".github" / "workflows"

        # Define tool version mappings
        self.tool_versions: dict[str, dict[str, str | None]] = {
            "pip-audit": {"pre_commit": "v2.7.3", "pyproject": ">=2.7.3,<3.0", "ci_exact": "2.7.3"},
            "detect-secrets": {
                "pre_commit": "v1.5.0",
                "pyproject": ">=1.5.0,<2.0",
                "ci_exact": "1.5.0",
            },  # pragma: allowlist secret
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

    def load_pre_commit_config(self) -> dict[str, Any]:
        """Load pre-commit configuration."""
        with self.pre_commit_config.open() as f:
            config = yaml.safe_load(f)
            if not isinstance(config, dict):
                return {}
            return config

    def load_pyproject_toml(self) -> str:
        """Load pyproject.toml as text (for easier regex manipulation)."""
        with self.pyproject_toml.open() as f:
            return f.read()

    def get_workflow_files(self) -> list[Path]:
        """Get all workflow YAML files."""
        return list(self.workflows_dir.glob("*.yml"))

    def _check_tool_in_repo(self, rev: str, tool_name: str) -> list[str]:
        """Check a specific tool version in a repository."""
        issues = []
        expected = self.tool_versions[tool_name]["pre_commit"]

        if rev != expected:
            issues.append(f"Tool {tool_name} version mismatch: expected {expected}, got {rev}")

        return issues

    def check_pre_commit_versions(self) -> list[str]:
        """Check pre-commit versions against expected values."""
        issues = []
        config = self.load_pre_commit_config()

        tool_mappings = {
            "pip-audit": "pip-audit",
            "detect-secrets": "detect-secrets",  # pragma: allowlist secret
            "pyupgrade": "pyupgrade",
            "prettier": "prettier",
            "markdownlint": "markdownlint",
            "ruff-pre-commit": "ruff",
            "pylint": "pylint",
            "mypy": "mypy",
        }

        repos = config.get("repos", [])
        if isinstance(repos, list):
            for repo in repos:
                if isinstance(repo, dict):
                    repo_url = repo.get("repo", "")
                    rev = repo.get("rev", "")

                    for url_pattern, tool_name in tool_mappings.items():
                        if url_pattern in repo_url:
                            issues.extend(self._check_tool_in_repo(rev, tool_name))
                            break

        return issues

    def check_pyproject_versions(self) -> list[str]:
        """Check pyproject.toml versions against expected values."""
        issues = []
        content = self.load_pyproject_toml()

        for tool, versions in self.tool_versions.items():
            pyproject_version = versions.get("pyproject")
            if pyproject_version is None:
                continue

            # Look for the tool in dev dependencies
            pattern = rf'"{tool}[^"]*"'
            matches = re.findall(pattern, content)

            if not matches:
                issues.append(f"{tool} not found in pyproject.toml dev dependencies")
            else:
                issues.extend(
                    [
                        f"{tool} pyproject.toml version mismatch: {match} should contain {pyproject_version}"
                        for match in matches
                        if pyproject_version not in match
                    ]
                )

        return issues

    def check_workflow_versions(self) -> list[str]:
        """Check workflow file versions against expected values."""
        issues = []

        for workflow_file in self.get_workflow_files():
            with workflow_file.open() as f:
                content = f.read()

            # Check for hardcoded tool versions in workflows
            for tool, versions in self.tool_versions.items():
                ci_exact = versions.get("ci_exact")
                if ci_exact is None:
                    continue

                # Look for tool installation commands
                patterns = [
                    rf"uv add --dev {tool}==[0-9.]+",
                    rf'pip install "{tool}==[0-9.]+"',
                    rf"{tool}==[0-9.]+",
                ]

                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    issues.extend(
                        [
                            f"{tool} in {workflow_file.name}: {match} should use version {ci_exact}"
                            for match in matches
                            if ci_exact not in match
                        ]
                    )

        return issues

    def _update_tool_in_repo(self, repo: dict[str, Any], tool_name: str) -> bool:
        """Update a specific tool version in a repository."""
        expected = self.tool_versions[tool_name]["pre_commit"]
        current_rev = repo.get("rev", "")
        if current_rev != expected:
            repo["rev"] = expected
            return True
        return False

    def update_pre_commit_config(self) -> bool:
        """Update pre-commit configuration with correct versions."""
        config = self.load_pre_commit_config()
        updated = False

        tool_mappings = {
            "pip-audit": "pip-audit",
            "detect-secrets": "detect-secrets",  # pragma: allowlist secret
            "pyupgrade": "pyupgrade",
            "prettier": "prettier",
            "markdownlint": "markdownlint",
            "ruff-pre-commit": "ruff",
            "pylint": "pylint",
            "mypy": "mypy",
        }

        repos = config.get("repos", [])
        if isinstance(repos, list):
            for repo in repos:
                if isinstance(repo, dict):
                    repo_url = repo.get("repo", "")

                    for url_pattern, tool_name in tool_mappings.items():
                        if url_pattern in repo_url:
                            if self._update_tool_in_repo(repo, tool_name):
                                updated = True
                            break

        if updated:
            with self.pre_commit_config.open("w") as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        return updated

    def update_pyproject_toml(self) -> bool:
        """Update pyproject.toml with correct versions."""
        content = self.load_pyproject_toml()
        updated_content = content
        updated = False

        for tool, versions in self.tool_versions.items():
            pyproject_version = versions.get("pyproject")
            if pyproject_version is None:
                continue

            # Update version ranges in dev dependencies
            pattern = rf'"{tool}[^"]*"'
            replacement = f'"{tool}{pyproject_version}"'

            new_content = re.sub(pattern, replacement, updated_content)
            if new_content != updated_content:
                updated_content = new_content
                updated = True

        if updated:
            with self.pyproject_toml.open("w") as f:
                f.write(updated_content)

        return updated

    def generate_ci_workflow_updates(self) -> dict[str, str]:
        """Generate updated CI workflow content."""
        updates = {}

        for workflow_file in self.get_workflow_files():
            with workflow_file.open() as f:
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

    def _add_pyupgrade_step(self, content: str) -> str:
        """Add pyupgrade step to CI workflow."""
        if "pyupgrade" not in content:
            ci_exact = self.tool_versions["pyupgrade"].get("ci_exact", "")
            pyupgrade_step = f"""
      - name: Run pyupgrade syntax modernization
        run: |
          uv add --dev pyupgrade=={ci_exact}
          uv run pyupgrade --py313-plus china_data_processor.py china_data_downloader.py utils/**/*.py || true
"""  # pragma: allowlist secret

            # Insert after ruff format check
            content = content.replace(
                "          uv run ruff format --check .", "          uv run ruff format --check ." + pyupgrade_step
            )
        return content

    def _add_prettier_step(self, content: str) -> str:
        """Add prettier step to CI workflow."""
        if "prettier" not in content:
            ci_exact = self.tool_versions["prettier"].get("ci_exact", "")
            prettier_step = f"""
      - name: Format YAML and Markdown with prettier
        run: |
          npm install -g prettier@{ci_exact}
          prettier --check "**/*.{{yml,yaml,md}}" --ignore-path .gitignore || true
"""

            # Insert after pyupgrade
            if "pyupgrade" in content:
                pyupgrade_cmd = (
                    "uv run pyupgrade --py313-plus china_data_processor.py "
                    "china_data_downloader.py utils/**/*.py || true"
                )
                content = content.replace(
                    pyupgrade_cmd,
                    pyupgrade_cmd + prettier_step,
                )
        return content

    def _add_markdownlint_step(self, content: str) -> str:
        """Add markdownlint step to CI workflow."""
        if "markdownlint" not in content:
            ci_exact = self.tool_versions["markdownlint"].get("ci_exact", "")
            markdownlint_step = f"""
      - name: Lint Markdown files
        run: |
          npm install -g markdownlint-cli@{ci_exact}
          markdownlint "**/*.md" --ignore node_modules --ignore .github || true
"""

            # Insert after prettier
            if "prettier" in content:
                content = content.replace(
                    'prettier --check "**/*.{yml,yaml,md}" --ignore-path .gitignore || true',
                    'prettier --check "**/*.{yml,yaml,md}" --ignore-path .gitignore || true' + markdownlint_step,
                )
        return content

    def _add_radon_step(self, content: str) -> str:
        """Add radon complexity check to CI workflow."""
        if "radon" not in content:
            ci_exact = self.tool_versions["radon"].get("ci_exact", "")
            radon_step = f"""
      - name: Check code complexity with radon
        run: |
          uv add --dev radon=={ci_exact}
          uv run radon cc china_data_processor.py china_data_downloader.py utils/ --min B --show-complexity || true
"""

            # Insert after markdownlint
            if "markdownlint" in content:
                content = content.replace(
                    'markdownlint "**/*.md" --ignore node_modules --ignore .github || true',
                    'markdownlint "**/*.md" --ignore node_modules --ignore .github || true' + radon_step,
                )
        return content

    def _add_interrogate_step(self, content: str) -> str:
        """Add interrogate docstring coverage to CI workflow."""
        if "interrogate" not in content:
            ci_exact = self.tool_versions["interrogate"].get("ci_exact", "")
            interrogate_step = f"""
      - name: Check docstring coverage with interrogate
        run: |
          uv add --dev interrogate=={ci_exact}
          uv run interrogate china_data_processor.py china_data_downloader.py utils/ --verbose --fail-under=80 || true
"""

            # Insert after radon
            if "radon" in content:
                radon_cmd = (
                    "uv run radon cc china_data_processor.py china_data_downloader.py utils/ "
                    "--min B --show-complexity || true"
                )
                content = content.replace(
                    radon_cmd,
                    radon_cmd + interrogate_step,
                )
        return content

    def _update_tool_versions_in_content(self, content: str) -> str:
        """Update existing tool versions in content."""
        for tool, versions in self.tool_versions.items():
            ci_exact = versions.get("ci_exact")
            if ci_exact is None:
                continue

            # Update hardcoded versions
            patterns = [
                (rf"uv add --dev {tool}==[0-9.]+", f"uv add --dev {tool}=={ci_exact}"),
                (rf'pip install "{tool}==[0-9.]+"', f'pip install "{tool}=={ci_exact}"'),
            ]

            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)

        return content

    def _update_main_ci_workflow(self, content: str) -> str:
        """Update main CI workflow with missing tools."""
        content = self._add_pyupgrade_step(content)
        content = self._add_prettier_step(content)
        content = self._add_markdownlint_step(content)
        content = self._add_radon_step(content)
        content = self._add_interrogate_step(content)
        return self._update_tool_versions_in_content(content)

    def _update_security_workflow(self, content: str) -> str:
        """Update security workflow with pinned versions."""
        # Pin detect-secrets version
        detect_secrets_version = self.tool_versions["detect-secrets"].get("ci_exact", "")
        content = re.sub(
            r'uv pip install "detect-secrets[^"]*"',
            f'uv pip install "detect-secrets=={detect_secrets_version}"',
            content,
        )

        # Ensure bandit is pinned
        bandit_version = self.tool_versions["bandit"].get("ci_exact", "")
        if "bandit" in content and "bandit==" not in content:
            content = re.sub(
                r"uv run bandit",
                f"uv add --dev bandit=={bandit_version} && uv run bandit",
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
            with Path(workflow_path).open("w") as f:
                f.write(new_content)
            print(f"✅ Updated {Path(workflow_path).name}")
            updated = True

        return updated


def main() -> int:
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
    print("i No updates needed - all versions already synchronized")
    return 0


if __name__ == "__main__":
    sys.exit(main())
