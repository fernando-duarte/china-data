#!/usr/bin/env python3
"""Compliance Report Generator for China Data Project.

This script generates comprehensive compliance reports covering security,
quality, coverage, dependencies, and documentation aspects.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def run_command(cmd: list[str], capture_output: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    try:
        return subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            check=False,  # Don't raise on non-zero exit
        )
    except subprocess.CalledProcessError as e:
        return subprocess.CompletedProcess(cmd, e.returncode, e.stdout, e.stderr)


def run_security_checks() -> dict[str, Any]:
    """Run security checks and return results."""
    security_results = {}

    # Bandit security scan
    print("Running Bandit security scan...")
    bandit_result = run_command(["uv", "run", "bandit", "-r", ".", "-f", "json", "-o", "bandit-report.json"])
    security_results["bandit"] = {
        "exit_code": bandit_result.returncode,
        "passed": bandit_result.returncode == 0,
        "report_file": "bandit-report.json"
    }

    # Safety vulnerability check
    print("Running Safety vulnerability check...")
    safety_result = run_command(["uv", "run", "safety", "check", "--json", "--output", "safety-report.json"])
    security_results["safety"] = {
        "exit_code": safety_result.returncode,
        "passed": safety_result.returncode == 0,
        "report_file": "safety-report.json"
    }

    # pip-audit
    print("Running pip-audit...")
    audit_result = run_command(["uv", "run", "pip-audit", "--format=json", "--output=pip-audit-report.json"])
    security_results["pip_audit"] = {
        "exit_code": audit_result.returncode,
        "passed": audit_result.returncode == 0,
        "report_file": "pip-audit-report.json"
    }

    return security_results


def run_quality_checks() -> dict[str, Any]:
    """Run code quality checks and return results."""
    quality_results = {}

    # Ruff linting
    print("Running Ruff linting...")
    ruff_result = run_command(["uv", "run", "ruff", "check", "."])
    quality_results["ruff"] = {
        "exit_code": ruff_result.returncode,
        "passed": ruff_result.returncode == 0,
        "issues": ruff_result.stdout.count("error") if ruff_result.stdout else 0
    }

    # MyPy type checking
    print("Running MyPy type checking...")
    mypy_result = run_command(["uv", "run", "mypy", "."])
    quality_results["mypy"] = {
        "exit_code": mypy_result.returncode,
        "passed": mypy_result.returncode == 0,
        "issues": mypy_result.stdout.count("error") if mypy_result.stdout else 0
    }

    # Radon complexity
    print("Running Radon complexity analysis...")
    radon_result = run_command(["uv", "run", "radon", "cc", ".", "--min", "B"])
    quality_results["radon"] = {
        "exit_code": radon_result.returncode,
        "passed": radon_result.returncode == 0,
        "complex_functions": radon_result.stdout.count("C ") + radon_result.stdout.count("D ") + radon_result.stdout.count("E ") + radon_result.stdout.count("F ") if radon_result.stdout else 0
    }

    return quality_results


def run_coverage_analysis() -> dict[str, Any]:
    """Run test coverage analysis and return results."""
    coverage_results = {}

    print("Running test coverage analysis...")
    # Run pytest with coverage
    coverage_result = run_command([
        "uv", "run", "pytest",
        "--cov",
        "--cov-report=json",
        "--cov-report=term-missing",
        "tests/"
    ])

    coverage_results["pytest"] = {
        "exit_code": coverage_result.returncode,
        "passed": coverage_result.returncode == 0
    }

    # Parse coverage report if available
    coverage_file = Path("coverage.json")
    if coverage_file.exists():
        with open(coverage_file) as f:
            coverage_data = json.load(f)
            coverage_results["total_coverage"] = coverage_data.get("totals", {}).get("percent_covered", 0)
            coverage_results["missing_coverage"] = coverage_data.get("totals", {}).get("missing_lines", 0)
    else:
        coverage_results["total_coverage"] = 0
        coverage_results["missing_coverage"] = "unknown"

    return coverage_results


def run_dependency_audit() -> dict[str, Any]:
    """Run dependency audit and return results."""
    dependency_results = {}

    print("Running dependency audit...")

    # Check for outdated packages
    outdated_result = run_command(["uv", "run", "pip", "list", "--outdated", "--format=json"])

    if outdated_result.returncode == 0 and outdated_result.stdout:
        try:
            outdated_packages = json.loads(outdated_result.stdout)
            dependency_results["outdated_count"] = len(outdated_packages)
            dependency_results["outdated_packages"] = [pkg["name"] for pkg in outdated_packages[:10]]  # Top 10
        except json.JSONDecodeError:
            dependency_results["outdated_count"] = "unknown"
            dependency_results["outdated_packages"] = []
    else:
        dependency_results["outdated_count"] = 0
        dependency_results["outdated_packages"] = []

    # Total package count
    list_result = run_command(["uv", "run", "pip", "list", "--format=json"])
    if list_result.returncode == 0 and list_result.stdout:
        try:
            packages = json.loads(list_result.stdout)
            dependency_results["total_packages"] = len(packages)
        except json.JSONDecodeError:
            dependency_results["total_packages"] = "unknown"
    else:
        dependency_results["total_packages"] = "unknown"

    return dependency_results


def run_doc_coverage() -> dict[str, Any]:
    """Run documentation coverage and return results."""
    doc_results = {}

    print("Running documentation coverage...")
    # Use interrogate for docstring coverage
    interrogate_result = run_command(["uv", "run", "interrogate", "--config", "pyproject.toml", "."])

    doc_results["interrogate"] = {
        "exit_code": interrogate_result.returncode,
        "passed": interrogate_result.returncode == 0
    }

    # Try to extract coverage percentage from output
    if interrogate_result.stdout:
        lines = interrogate_result.stdout.split("\n")
        for line in lines:
            if "Overall interrogate coverage:" in line:
                try:
                    percentage = float(line.split(":")[1].strip().rstrip("%"))
                    doc_results["coverage_percentage"] = percentage
                    break
                except (ValueError, IndexError):
                    pass

    if "coverage_percentage" not in doc_results:
        doc_results["coverage_percentage"] = "unknown"

    return doc_results


def generate_compliance_report() -> dict[str, Any]:
    """Generate comprehensive compliance report."""
    print("🔍 Generating compliance report...")

    report = {
        "timestamp": datetime.now().isoformat(),
        "project": "china-data",
        "version": "0.1.0",
        "compliance_checks": {
            "security": run_security_checks(),
            "quality": run_quality_checks(),
            "coverage": run_coverage_analysis(),
            "dependencies": run_dependency_audit(),
            "documentation": run_doc_coverage()
        }
    }

    # Calculate overall compliance score
    score = calculate_compliance_score(report["compliance_checks"])
    report["compliance_score"] = score

    return report


def calculate_compliance_score(checks: dict[str, Any]) -> dict[str, Any]:
    """Calculate overall compliance score."""
    scores = {
        "security": 0,
        "quality": 0,
        "coverage": 0,
        "dependencies": 0,
        "documentation": 0
    }

    # Security score (40% weight)
    security = checks["security"]
    security_passed = sum(1 for check in security.values() if isinstance(check, dict) and check.get("passed", False))
    security_total = len([check for check in security.values() if isinstance(check, dict)])
    scores["security"] = (security_passed / security_total * 100) if security_total > 0 else 0

    # Quality score (30% weight)
    quality = checks["quality"]
    quality_passed = sum(1 for check in quality.values() if isinstance(check, dict) and check.get("passed", False))
    quality_total = len([check for check in quality.values() if isinstance(check, dict)])
    scores["quality"] = (quality_passed / quality_total * 100) if quality_total > 0 else 0

    # Coverage score (20% weight)
    coverage = checks["coverage"]
    coverage_pct = coverage.get("total_coverage", 0)
    scores["coverage"] = coverage_pct if isinstance(coverage_pct, (int, float)) else 0

    # Dependencies score (5% weight)
    deps = checks["dependencies"]
    outdated_count = deps.get("outdated_count", 0)
    total_packages = deps.get("total_packages", 1)
    if isinstance(outdated_count, int) and isinstance(total_packages, int) and total_packages > 0:
        scores["dependencies"] = max(0, 100 - (outdated_count / total_packages * 100))
    else:
        scores["dependencies"] = 50  # Unknown state

    # Documentation score (5% weight)
    docs = checks["documentation"]
    doc_coverage = docs.get("coverage_percentage", 0)
    scores["documentation"] = doc_coverage if isinstance(doc_coverage, (int, float)) else 0

    # Calculate weighted overall score
    weights = {
        "security": 0.4,
        "quality": 0.3,
        "coverage": 0.2,
        "dependencies": 0.05,
        "documentation": 0.05
    }

    overall = sum(scores[key] * weights[key] for key in scores)

    return {
        "overall": round(overall, 2),
        "breakdown": scores,
        "weights": weights
    }


def main():
    """Main function to generate and save compliance report."""
    report = generate_compliance_report()

    # Save report to file
    report_file = f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w") as f:
        json.dump(report, indent=2, fp=f)

    # Print summary
    print("\n" + "="*50)
    print("COMPLIANCE REPORT SUMMARY")
    print("="*50)
    print(f"Overall Score: {report['compliance_score']['overall']:.1f}%")
    print("\nBreakdown:")
    for category, score in report["compliance_score"]["breakdown"].items():
        print(f"  {category.title()}: {score:.1f}%")

    print(f"\n📊 Full report saved to: {report_file}")

    # Return appropriate exit code
    if report["compliance_score"]["overall"] >= 80:
        print("✅ Compliance check PASSED")
        return 0
    print("❌ Compliance check FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
