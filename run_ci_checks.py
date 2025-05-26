#!/usr/bin/env python3

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime


class WorkflowRunner:
    def __init__(self, workspace_dir: str = ".", python_version: str = "3.11"):
        self.workspace_dir = os.path.abspath(workspace_dir)
        self.python_version = python_version
        self.output_dir = os.path.join(self.workspace_dir, "workflow_outputs")
        os.makedirs(self.output_dir, exist_ok=True)

    def run_command(self, cmd: list[str], check: bool = True) -> tuple[int, str, str]:
        """Run a shell command and return exit code, stdout, and stderr"""
        try:
            result = subprocess.run(
                cmd,
                shell=False,  # Changed to False since we're using list
                check=check,
                capture_output=True,
                text=True,
                cwd=self.workspace_dir,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return e.returncode, e.stdout, e.stderr

    def setup_environment(self):
        """Setup virtual environment and install dependencies"""
        print("\n🔧 Setting up environment...")

        venv_dir = os.path.join(self.workspace_dir, "venv")
        if not os.path.exists(venv_dir):
            self.run_command([sys.executable, "-m", "venv", venv_dir])

        # Install dependencies
        pip_cmd = os.path.join(venv_dir, "bin", "pip") if os.name != "nt" else os.path.join(venv_dir, "Scripts", "pip")
        self.run_command([pip_cmd, "install", "-r", "requirements.txt"])
        self.run_command([pip_cmd, "install", "-r", "dev-requirements.txt"])

        return venv_dir

    def run_code_quality_checks(self, venv_dir: str) -> dict[str, bool]:
        """Run code quality checks (black, isort, flake8, pylint, mypy)"""
        print("\n🔍 Running code quality checks...")
        results = {}

        python_cmd = (
            os.path.join(venv_dir, "bin", "python") if os.name != "nt" else os.path.join(venv_dir, "Scripts", "python")
        )

        # Black
        print("\nRunning black...")
        code, out, err = self.run_command(
            [python_cmd, "-m", "black", "--check", "--diff", ".", "--exclude=venv"], check=False
        )
        results["black"] = code == 0
        if code != 0:
            print("⚠️  Black formatting issues found:")
            print(err or out)

        # isort
        print("\nRunning isort...")
        code, out, err = self.run_command(
            [python_cmd, "-m", "isort", "--check", "--diff", ".", "--skip", "venv"], check=False
        )
        results["isort"] = code == 0
        if code != 0:
            print("⚠️  Import sorting issues found:")
            print(err or out)

        # flake8
        print("\nRunning flake8...")
        flake8_report = os.path.join(self.output_dir, "flake8-report.txt")
        code, out, err = self.run_command(
            [python_cmd, "-m", "flake8", ".", "--exclude=venv", "--statistics", "--output-file", flake8_report],
            check=False,
        )
        results["flake8"] = code == 0
        if code != 0:
            print("⚠️  Flake8 issues found:")
            print(err or out)

        # pylint
        print("\nRunning pylint...")
        code, out, err = self.run_command(
            [
                python_cmd,
                "-m",
                "pylint",
                "china_data_processor.py",
                "china_data_downloader.py",
                "utils/",
                "--ignore=venv",
            ],
            check=False,
        )
        results["pylint"] = code == 0
        if code != 0:
            print("⚠️  Pylint issues found:")
            print(err or out)

        # mypy
        print("\nRunning mypy...")
        code, out, err = self.run_command(
            [python_cmd, "-m", "mypy", "china_data_processor.py", "china_data_downloader.py"], check=False
        )
        results["mypy"] = code == 0
        if code != 0:
            print("⚠️  Type checking issues found:")
            print(err or out)

        return results

    def run_tests(self, venv_dir: str) -> dict[str, bool]:
        """Run test suite with coverage"""
        print("\n🧪 Running tests...")
        results = {}

        python_cmd = (
            os.path.join(venv_dir, "bin", "python") if os.name != "nt" else os.path.join(venv_dir, "Scripts", "python")
        )

        # Create output directory
        os.makedirs("output", exist_ok=True)

        # Run tests with coverage
        print("\nRunning pytest with coverage...")
        code, out, err = self.run_command(
            [
                python_cmd,
                "-m",
                "pytest",
                "tests/",
                "-v",
                "--tb=short",
                "--cov=.",
                "--cov-report=xml",
                "--cov-report=html",
                "--cov-report=term-missing",
            ],
            check=False,
        )
        results["tests"] = code == 0
        if code != 0:
            print("⚠️  Test failures found:")
            print(err or out)

        return results

    def run_security_checks(self, venv_dir: str) -> dict[str, bool]:
        """Run security checks using bandit"""
        print("\n🔒 Running security checks...")
        results = {}

        python_cmd = (
            os.path.join(venv_dir, "bin", "python") if os.name != "nt" else os.path.join(venv_dir, "Scripts", "python")
        )

        # Bandit security check
        print("\nRunning bandit...")
        bandit_report = os.path.join(self.output_dir, "bandit-report.json")
        code, out, err = self.run_command(
            [
                python_cmd,
                "-m",
                "bandit",
                "-r",
                ".",
                "-f",
                "json",
                "-o",
                bandit_report,
                "--exclude",
                "./venv/*,./tests/*",
            ],
            check=False,
        )
        results["bandit"] = code == 0
        if code != 0:
            print("⚠️  Security issues found:")
            print(err or out)

        return results

    def run_dependency_checks(self, venv_dir: str) -> dict[str, bool]:
        """Run dependency checks and license compliance"""
        print("\n📦 Running dependency checks...")
        results = {}

        python_cmd = (
            os.path.join(venv_dir, "bin", "python") if os.name != "nt" else os.path.join(venv_dir, "Scripts", "python")
        )
        pip_cmd = os.path.join(venv_dir, "bin", "pip") if os.name != "nt" else os.path.join(venv_dir, "Scripts", "pip")

        # Check for outdated packages
        print("\nChecking for outdated packages...")
        outdated_report = os.path.join(self.output_dir, "outdated-packages.json")
        with open(outdated_report, "w") as f:
            code, out, err = self.run_command([pip_cmd, "list", "--outdated", "--format=json"], check=False)
            if code == 0:
                f.write(out)
        results["outdated_check"] = code == 0

        # Generate dependency tree
        print("\nGenerating dependency tree...")
        self.run_command([pip_cmd, "install", "pipdeptree"], check=False)
        dep_tree_file = os.path.join(self.output_dir, "dependency-tree.txt")
        with open(dep_tree_file, "w") as f:
            code, out, err = self.run_command([python_cmd, "-m", "pipdeptree"], check=False)
            if code == 0:
                f.write(out)
        results["dependency_tree"] = code == 0

        return results

    def generate_report(self, all_results: dict[str, dict[str, bool]]):
        """Generate a summary report of all checks"""
        print("\n📋 Generating summary report...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "python_version": self.python_version,
            "results": all_results,
            "summary": {
                "total_checks": sum(len(r) for r in all_results.values()),
                "passed_checks": sum(sum(1 for v in r.values() if v) for r in all_results.values()),
                "failed_checks": sum(sum(1 for v in r.values() if not v) for r in all_results.values()),
            },
        }

        report_file = os.path.join(self.output_dir, "workflow-summary.json")
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print("\n✨ Summary:")
        print("Total checks: {total}".format(total=report["summary"]["total_checks"]))
        print("Passed: {passed}".format(passed=report["summary"]["passed_checks"]))
        print("Failed: {failed}".format(failed=report["summary"]["failed_checks"]))
        print(f"\nDetailed reports available in: {self.output_dir}")

    def run_all(self):
        """Run all workflow checks"""
        try:
            venv_dir = self.setup_environment()

            results = {
                "code_quality": self.run_code_quality_checks(venv_dir),
                "tests": self.run_tests(venv_dir),
                "security": self.run_security_checks(venv_dir),
                "dependencies": self.run_dependency_checks(venv_dir),
            }

            self.generate_report(results)

            # Return non-zero exit code if any checks failed
            if any(not check for category in results.values() for check in category.values()):
                return 1
            return 0

        except Exception as e:
            print(f"\n❌ Error running workflows: {e}")
            return 1


def main():
    parser = argparse.ArgumentParser(description="Run CI workflow checks locally")
    parser.add_argument("--workspace", default=".", help="Path to workspace directory")
    parser.add_argument("--python-version", default="3.11", help="Python version to use")
    args = parser.parse_args()

    runner = WorkflowRunner(args.workspace, args.python_version)
    sys.exit(runner.run_all())


if __name__ == "__main__":
    main()
