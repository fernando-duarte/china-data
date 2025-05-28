#!/usr/bin/env python3
"""SARIF Report Generator for China Data Project.

This script generates unified SARIF (Static Analysis Results Interchange Format) reports
from various security and quality tools for IDE integration and security analysis.

SARIF is a standard format for static analysis tool output that can be imported into
IDEs like VS Code, GitHub, and other security analysis platforms.
"""

import argparse
import json
import subprocess  # nosec B404
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class SarifReportGenerator:
    """Generates unified SARIF reports from multiple security tools."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # SARIF schema version
        self.sarif_version = "2.1.0"
        self.schema_uri = (
            "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json"
        )

    def run_bandit(self) -> dict[str, Any]:
        """Run bandit security scan and return SARIF results."""
        try:
            result = subprocess.run(  # nosec B603 B607 S607
                ["uv", "run", "bandit", "-r", ".", "-f", "sarif", "-o", "-"],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.stdout:
                return json.loads(result.stdout)
            return self._create_empty_sarif("bandit")

        except (subprocess.SubprocessError, json.JSONDecodeError) as e:
            print(f"Warning: Bandit SARIF generation failed: {e}")
            return self._create_empty_sarif("bandit")

    def run_semgrep(self) -> dict[str, Any]:
        """Run semgrep security scan and return SARIF results."""
        try:
            result = subprocess.run(  # nosec B603 B607 S607
                ["uv", "run", "semgrep", "--config=auto", "--sarif", "--output=-"],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.stdout:
                return json.loads(result.stdout)
            return self._create_empty_sarif("semgrep")

        except (subprocess.SubprocessError, json.JSONDecodeError) as e:
            print(f"Warning: Semgrep SARIF generation failed: {e}")
            return self._create_empty_sarif("semgrep")

    def run_ruff_sarif(self) -> dict[str, Any]:
        """Run ruff linting and convert to SARIF format."""
        try:
            result = subprocess.run(  # nosec B603 B607 S607
                ["uv", "run", "ruff", "check", ".", "--output-format=sarif"],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.stdout:
                return json.loads(result.stdout)
            return self._create_empty_sarif("ruff")

        except (subprocess.SubprocessError, json.JSONDecodeError) as e:
            print(f"Warning: Ruff SARIF generation failed: {e}")
            return self._create_empty_sarif("ruff")

    def run_mypy_sarif(self) -> dict[str, Any]:
        """Run mypy type checking and convert to SARIF format."""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                report_dir = Path(temp_dir) / "mypy-sarif"

                # Run mypy with SARIF output
                subprocess.run(  # nosec B603 B607 S607
                    ["uv", "run", "mypy", ".", "--output", "sarif", "--sarif-file", str(report_dir / "mypy.sarif")],
                    capture_output=True,
                    text=True,
                    check=False,
                )

                sarif_file = report_dir / "mypy.sarif"
                if sarif_file.exists():
                    with sarif_file.open() as f:
                        return json.load(f)

            return self._create_empty_sarif("mypy")

        except (subprocess.SubprocessError, json.JSONDecodeError) as e:
            print(f"Warning: MyPy SARIF generation failed: {e}")
            return self._create_empty_sarif("mypy")

    def _create_empty_sarif(self, tool_name: str) -> dict[str, Any]:
        """Create an empty SARIF report for a tool."""
        return {
            "$schema": self.schema_uri,
            "version": self.sarif_version,
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": tool_name,
                            "version": "unknown",
                            "informationUri": f"https://github.com/tool/{tool_name}",
                        }
                    },
                    "results": [],
                }
            ],
        }

    def merge_sarif_reports(self, reports: list[dict[str, Any]]) -> dict[str, Any]:
        """Merge multiple SARIF reports into a unified report."""
        unified_report = {
            "$schema": self.schema_uri,
            "version": self.sarif_version,
            "runs": [],
        }

        for report in reports:
            if "runs" in report:
                unified_report["runs"].extend(report["runs"])

        # Add metadata
        unified_report["runs"].insert(
            0,
            {
                "tool": {
                    "driver": {
                        "name": "china-data-unified-security",
                        "version": "1.0.0",
                        "informationUri": "https://github.com/fernandoduarte/china_data",
                        "semanticVersion": "1.0.0",
                    }
                },
                "invocation": {
                    "executionSuccessful": True,
                    "startTimeUtc": datetime.now(timezone.utc).isoformat(),
                    "workingDirectory": {"uri": f"file://{Path.cwd()}"},
                },
                "results": [],
            },
        )

        return unified_report

    def generate_individual_reports(self) -> dict[str, dict[str, Any]]:
        """Generate individual SARIF reports from each tool."""
        print("🔍 Generating individual SARIF reports...")

        reports = {}

        print("  Running bandit security scan...")
        reports["bandit"] = self.run_bandit()

        print("  Running semgrep security scan...")
        reports["semgrep"] = self.run_semgrep()

        print("  Running ruff linting...")
        reports["ruff"] = self.run_ruff_sarif()

        print("  Running mypy type checking...")
        reports["mypy"] = self.run_mypy_sarif()

        return reports

    def save_reports(self, reports: dict[str, dict[str, Any]], unified_report: dict[str, Any]) -> None:
        """Save individual and unified SARIF reports to files."""
        print(f"💾 Saving SARIF reports to {self.output_dir}...")

        # Save individual reports
        for tool_name, report in reports.items():
            output_file = self.output_dir / f"{tool_name}-security-report.sarif"
            with output_file.open("w") as f:
                json.dump(report, f, indent=2)
            print(f"  ✅ Saved {tool_name} report: {output_file}")

        # Save unified report
        unified_file = self.output_dir / "unified-security-report.sarif"
        with unified_file.open("w") as f:
            json.dump(unified_report, f, indent=2)
        print(f"  ✅ Saved unified report: {unified_file}")

    def generate_summary(self, reports: dict[str, dict[str, Any]]) -> None:
        """Generate a summary of findings."""
        print("\n📊 SARIF Report Summary:")

        total_issues = 0
        for tool_name, report in reports.items():
            tool_issues = 0
            for run in report.get("runs", []):
                tool_issues += len(run.get("results", []))

            print(f"  {tool_name}: {tool_issues} issues")
            total_issues += tool_issues

        print(f"  Total: {total_issues} issues across all tools")

        if total_issues == 0:
            print("  🎉 No security or quality issues found!")
        else:
            print(f"  ⚠️  {total_issues} issues found - review SARIF reports for details")

    def generate_reports(self) -> int:
        """Generate all SARIF reports."""
        try:
            # Generate individual reports
            reports = self.generate_individual_reports()

            # Create unified report
            print("\n🔗 Merging reports into unified SARIF...")
            unified_report = self.merge_sarif_reports(list(reports.values()))

            # Save all reports
            self.save_reports(reports, unified_report)

            # Generate summary
            self.generate_summary(reports)

            print(f"\n✅ SARIF reports generated successfully in {self.output_dir}")
            print("\n💡 IDE Integration:")
            print("  - VS Code: Install 'SARIF Viewer' extension and open .sarif files")
            print("  - GitHub: Upload SARIF files to Security tab for code scanning alerts")
            print("  - Other IDEs: Import unified-security-report.sarif for integrated security analysis")

        except (subprocess.SubprocessError, json.JSONDecodeError, OSError) as e:
            print(f"❌ Error generating SARIF reports: {e}")
            return 1
        else:
            return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate unified SARIF security reports")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("security-reports"),
        help="Output directory for SARIF reports (default: security-reports)",
    )

    args = parser.parse_args()

    generator = SarifReportGenerator(args.output_dir)
    return generator.generate_reports()


if __name__ == "__main__":
    sys.exit(main())
