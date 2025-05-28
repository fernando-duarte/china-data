#!/usr/bin/env python3
"""Compliance Report Generator for China Data Project.

This script generates comprehensive compliance reports covering:
- Security checks (bandit, safety)
- Code quality metrics (ruff, mypy, radon)
- Test coverage analysis
- Dependency health assessment
- Documentation coverage

The report includes scoring and recommendations for improvement.
"""

import contextlib
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Compliance thresholds
COMPLIANCE_THRESHOLDS = {
    "coverage_minimum": 80,
    "security_score_minimum": 8,
    "quality_score_minimum": 7,
    "dependency_vulnerabilities_maximum": 0,
    "documentation_coverage_minimum": 75,
}


def run_security_checks() -> dict[str, Any]:
    """Run security-related checks and return results."""
    results = {
        "bandit": {},
        "safety": {},
        "secrets_detected": 0,
        "overall_score": 0,
    }

    try:
        # Run bandit security check
        bandit_result = subprocess.run(
            ["/usr/bin/env", "uv", "run", "bandit", "-r", ".", "-f", "json"],
            capture_output=True,
            text=True,
            check=False,
        )

        if bandit_result.returncode == 0:
            bandit_data = json.loads(bandit_result.stdout)
            results["bandit"] = {
                "issues": len(bandit_data.get("results", [])),
                "confidence_high": len(
                    [r for r in bandit_data.get("results", []) if r.get("issue_confidence") == "HIGH"]
                ),
                "severity_high": len([r for r in bandit_data.get("results", []) if r.get("issue_severity") == "HIGH"]),
            }

        # Run safety check for known vulnerabilities
        safety_result = subprocess.run(
            ["/usr/bin/env", "uv", "run", "safety", "check", "--json"],
            capture_output=True,
            text=True,
            check=False,
        )

        if safety_result.returncode == 0:
            safety_data = json.loads(safety_result.stdout)
            results["safety"] = {
                "vulnerabilities": len(safety_data),
                "critical": len([v for v in safety_data if v.get("severity") == "critical"]),
            }

        # Calculate overall security score
        bandit_issues = results["bandit"].get("issues", 0)
        safety_vulns = results["safety"].get("vulnerabilities", 0)
        results["overall_score"] = min(10, bandit_issues - safety_vulns)

    except (subprocess.SubprocessError, json.JSONDecodeError) as e:
        results["error"] = f"Security check failed: {e}"
        results["overall_score"] = 0

    return results


def run_quality_checks() -> dict[str, Any]:
    """Run code quality checks and return results."""
    results = {
        "ruff_issues": 0,
        "mypy_errors": 0,
        "complexity_score": 0,
        "overall_score": 0,
    }

    try:
        # Run ruff linting
        ruff_result = subprocess.run(
            ["/usr/bin/env", "uv", "run", "ruff", "check", ".", "--output-format=json"],
            capture_output=True,
            text=True,
            check=False,
        )

        if ruff_result.stdout:
            ruff_data = json.loads(ruff_result.stdout)
            results["ruff_issues"] = len(ruff_data)

        # Run mypy type checking
        with tempfile.TemporaryDirectory() as temp_dir:
            mypy_report_dir = Path(temp_dir) / "mypy-report"
            subprocess.run(
                ["/usr/bin/env", "uv", "run", "mypy", ".", "--json-report", str(mypy_report_dir)],
                capture_output=True,
                text=True,
                check=False,
            )

            mypy_report_path = mypy_report_dir / "index.txt"
            if mypy_report_path.exists():
                mypy_content = mypy_report_path.read_text()
                results["mypy_errors"] = mypy_content.count("error:")

        # Run radon complexity analysis
        radon_result = subprocess.run(
            ["/usr/bin/env", "uv", "run", "radon", "cc", ".", "--json"],
            capture_output=True,
            text=True,
            check=False,
        )

        if radon_result.stdout:
            radon_data = json.loads(radon_result.stdout)
            # Calculate average complexity score
            total_complexity = 0
            total_functions = 0
            for file_data in radon_data.values():
                for func in file_data:
                    total_complexity += func.get("complexity", 0)
                    total_functions += 1

            if total_functions > 0:
                avg_complexity = total_complexity / total_functions
                results["complexity_score"] = max(0, 10 - avg_complexity)
            else:
                results["complexity_score"] = 10

        # Calculate overall quality score
        quality_score = 10 - (results["ruff_issues"] * 0.1) - (results["mypy_errors"] * 0.2)
        results["overall_score"] = max(0, min(10, quality_score + results["complexity_score"]) / 2)

    except (subprocess.SubprocessError, json.JSONDecodeError) as e:
        print(f"Error running quality checks: {e}")
        results["overall_score"] = 0

    return results


def run_coverage_analysis() -> dict[str, Any]:
    """Run test coverage analysis and return results."""
    results = {
        "total_coverage": 0,
        "line_coverage": 0,
        "branch_coverage": 0,
        "missing_lines": 0,
    }

    try:
        # Run pytest with coverage
        subprocess.run(
            ["/usr/bin/env", "uv", "run", "pytest", "--cov=.", "--cov-report=json"],
            capture_output=True,
            text=True,
            check=False,
        )

        coverage_file = Path("coverage.json")
        if coverage_file.exists():
            with coverage_file.open() as f:
                coverage_data = json.load(f)
                results["total_coverage"] = coverage_data.get("totals", {}).get("percent_covered", 0)
                results["line_coverage"] = coverage_data.get("totals", {}).get("percent_covered_display", "0%")
                results["missing_lines"] = coverage_data.get("totals", {}).get("missing_lines", 0)

    except (subprocess.SubprocessError, json.JSONDecodeError) as e:
        print(f"Error running coverage analysis: {e}")

    return results


def run_dependency_audit() -> dict[str, Any]:
    """Run dependency security audit and return results."""
    results = {
        "vulnerable_packages": 0,
        "outdated_packages": 0,
        "license_issues": 0,
        "overall_score": 0,
    }

    try:
        # Run pip-audit for vulnerability scanning
        audit_result = subprocess.run(
            ["/usr/bin/env", "uv", "run", "pip-audit", "--format=json"],
            capture_output=True,
            text=True,
            check=False,
        )

        if audit_result.stdout:
            audit_data = json.loads(audit_result.stdout)
            results["vulnerable_packages"] = len(audit_data.get("vulnerabilities", []))

        # Calculate dependency score
        results["overall_score"] = max(0, 10 - results["vulnerable_packages"])

    except (subprocess.SubprocessError, json.JSONDecodeError) as e:
        print(f"Error running dependency audit: {e}")
        results["overall_score"] = 5  # Default score if audit fails

    return results


def run_doc_coverage() -> dict[str, Any]:
    """Run documentation coverage analysis and return results."""
    results = {
        "coverage_percentage": 0,
        "missing_docstrings": 0,
        "total_functions": 0,
    }

    try:
        # Run interrogate for docstring coverage
        interrogate_result = subprocess.run(
            ["/usr/bin/env", "uv", "run", "interrogate", ".", "--generate-badge", ".", "--quiet"],
            capture_output=True,
            text=True,
            check=False,
        )

        # Parse interrogate output for coverage percentage
        if interrogate_result.stdout:
            lines = interrogate_result.stdout.split("\n")
            for line in lines:
                if "%" in line and "coverage" in line.lower():
                    # Extract percentage from line like "Overall: 85.5%"
                    percentage_str = line.split("%")[0].split()[-1]
                    with contextlib.suppress(ValueError):
                        results["coverage_percentage"] = float(percentage_str)

    except subprocess.SubprocessError as e:
        print(f"Error running documentation coverage: {e}")

    return results


def generate_compliance_report() -> dict[str, Any]:
    """Generate comprehensive compliance report."""
    print("🔍 Running compliance checks...")

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project": "china-data",
        "version": "0.1.0",
        "checks": {
            "security": run_security_checks(),
            "quality": run_quality_checks(),
            "coverage": run_coverage_analysis(),
            "dependencies": run_dependency_audit(),
            "documentation": run_doc_coverage(),
        },
        "compliance_score": {},
        "recommendations": [],
    }

    # Calculate compliance scores
    report["compliance_score"] = calculate_compliance_score(report["checks"])

    # Generate recommendations
    report["recommendations"] = generate_recommendations(report["checks"])

    print("✅ Compliance report generated successfully!")
    return report


def calculate_compliance_score(checks: dict[str, Any]) -> dict[str, float]:
    """Calculate weighted compliance scores."""
    scores = {}

    # Security score (25% weight)
    security = checks["security"]
    scores["security"] = security.get("overall_score", 0)

    # Quality score (30% weight)
    quality = checks["quality"]
    scores["quality"] = quality.get("overall_score", 0)

    # Coverage score (20% weight)
    coverage = checks["coverage"]
    coverage_pct = coverage.get("total_coverage", 0)
    scores["coverage"] = coverage_pct if isinstance(coverage_pct, int | float) else 0

    # Dependencies score (15% weight)
    dependencies = checks["dependencies"]
    scores["dependencies"] = dependencies.get("overall_score", 0)

    # Documentation score (10% weight)
    docs = checks["documentation"]
    doc_coverage = docs.get("coverage_percentage", 0)
    scores["documentation"] = doc_coverage if isinstance(doc_coverage, int | float) else 0

    # Calculate weighted overall score
    overall = (
        scores["security"] * 0.25
        + scores["quality"] * 0.30
        + scores["coverage"] * 0.20
        + scores["dependencies"] * 0.15
        + scores["documentation"] * 0.10
    )
    scores["overall"] = round(overall, 2)

    return scores


def main() -> int:
    """Main function to generate and save compliance report."""
    report = generate_compliance_report()

    # Print summary
    print("\n📊 Compliance Summary:")
    print(f"Overall Score: {report['compliance_score']['overall']}/10")

    # Save report to file
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_file = f"compliance_report_{timestamp}.json"
    with Path(report_file).open("w") as f:
        json.dump(report, indent=2, fp=f)

    print(f"📄 Report saved to: {report_file}")

    # Print detailed scores
    scores = report["compliance_score"]
    print("\n📈 Detailed Scores:")
    print(f"Security: {scores['security']}/10")
    print(f"Quality: {scores['quality']}/10")
    print(f"Coverage: {scores['coverage']}/10")
    print(f"Dependencies: {scores['dependencies']}/10")
    print(f"Documentation: {scores['documentation']}/10")

    # Print recommendations
    if report["recommendations"]:
        print("\n💡 Recommendations:")
        for rec in report["recommendations"]:
            print(f"- {rec}")

    # Return appropriate exit code
    if report["compliance_score"]["overall"] >= COMPLIANCE_THRESHOLDS["coverage_minimum"]:
        print("✅ Compliance check PASSED")
        return 0
    print("❌ Compliance check FAILED")
    return 1


def generate_recommendations(checks: dict[str, Any]) -> list[str]:
    """Generate recommendations based on check results."""
    recommendations = []

    # Security recommendations
    security = checks["security"]
    if security.get("bandit", {}).get("issues", 0) > 0:
        recommendations.append("Address security issues identified by bandit")
    if security.get("safety", {}).get("vulnerabilities", 0) > 0:
        recommendations.append("Update packages with known vulnerabilities")

    # Quality recommendations
    quality = checks["quality"]
    if quality.get("ruff_issues", 0) > COMPLIANCE_THRESHOLDS["quality_score_minimum"]:
        recommendations.append("Fix linting issues identified by ruff")

    mypy_error_threshold = 5
    if quality.get("mypy_errors", 0) > mypy_error_threshold:
        recommendations.append("Improve type annotations to reduce mypy errors")

    # Coverage recommendations
    coverage = checks["coverage"]
    if coverage.get("line_coverage", 0) < COMPLIANCE_THRESHOLDS["coverage_minimum"]:
        recommendations.append("Increase test coverage to meet minimum threshold")

    # Dependency recommendations
    dependencies = checks["dependencies"]
    if dependencies.get("vulnerabilities", 0) > COMPLIANCE_THRESHOLDS["dependency_vulnerabilities_maximum"]:
        recommendations.append("Update dependencies to fix security vulnerabilities")

    # Documentation recommendations
    docs = checks["documentation"]
    if docs.get("coverage_percentage", 0) < COMPLIANCE_THRESHOLDS["documentation_coverage_minimum"]:
        recommendations.append("Improve documentation coverage by adding docstrings")

    return recommendations


if __name__ == "__main__":
    sys.exit(main())
