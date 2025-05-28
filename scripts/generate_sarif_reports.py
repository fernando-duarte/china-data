#!/usr/bin/env python3
"""Generate unified SARIF reports from multiple security tools.

This script runs various security tools and generates SARIF output for local development
and IDE integration. It aggregates results from Semgrep, Bandit, and other tools into
a unified SARIF report.
"""

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class SARIFGenerator:
    """Generate and aggregate SARIF reports from multiple security tools."""

    def __init__(self, output_dir: Path = Path("security-reports")):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
        self.reports: list[dict[str, Any]] = []

    def run_semgrep_sarif(self) -> Path | None:
        """Run Semgrep with SARIF output."""
        output_file = self.output_dir / "semgrep.sarif"

        cmd = [
            "uv",
            "run",
            "semgrep",
            "--config=p/security-audit",
            "--config=p/secrets",
            "--config=p/python",
            "--config=p/bandit",
            "--config=p/owasp-top-ten",
            "--sarif",
            f"--output={output_file}",
            "--timeout=30",
            "--skip-unknown-extensions",
            ".",
        ]

        try:
            print("🔍 Running Semgrep SARIF scan...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=False)

            if output_file.exists() and output_file.stat().st_size > 0:
                print(f"✅ Semgrep SARIF report generated: {output_file}")
                return output_file
            print("⚠️ Semgrep SARIF report is empty or not generated")
            return None

        except subprocess.TimeoutExpired:
            print("⚠️ Semgrep SARIF scan timed out")
            return None
        except Exception as e:
            print(f"❌ Error running Semgrep SARIF: {e}")
            return None

    def run_bandit_sarif(self) -> Path | None:
        """Run Bandit with SARIF output."""
        output_file = self.output_dir / "bandit.sarif"

        # First try with SARIF format
        cmd = [
            "uv",
            "run",
            "bandit",
            "-r",
            ".",
            "-f",
            "sarif",
            "-o",
            str(output_file),
            "--exclude",
            "./venv/*,./tests/*,./.venv/*,./node_modules/*,./htmlcov/*,./workflow_outputs/*",
        ]

        try:
            print("🔍 Running Bandit SARIF scan...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=False)

            if output_file.exists() and output_file.stat().st_size > 0:
                print(f"✅ Bandit SARIF report generated: {output_file}")
                return output_file
            # If SARIF format fails, try JSON and convert
            print("⚠️ Bandit SARIF format not available, trying JSON conversion...")
            return self._convert_bandit_json_to_sarif()

        except subprocess.TimeoutExpired:
            print("⚠️ Bandit SARIF scan timed out")
            return None
        except Exception as e:
            print(f"❌ Error running Bandit SARIF: {e}")
            # Try JSON conversion as fallback
            return self._convert_bandit_json_to_sarif()

    def _convert_bandit_json_to_sarif(self) -> Path | None:
        """Convert Bandit JSON output to SARIF format."""
        json_file = self.output_dir / "bandit.json"
        sarif_file = self.output_dir / "bandit.sarif"

        cmd = [
            "uv",
            "run",
            "bandit",
            "-r",
            ".",
            "-f",
            "json",
            "-o",
            str(json_file),
            "--exclude",
            "./venv/*,./tests/*,./.venv/*,./node_modules/*,./htmlcov/*,./workflow_outputs/*",
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=False)

            if not json_file.exists() or json_file.stat().st_size == 0:
                print("⚠️ Bandit JSON report is empty or not generated")
                return None

            # Convert JSON to SARIF
            with open(json_file) as f:
                bandit_data = json.load(f)

            sarif_data = self._bandit_json_to_sarif(bandit_data)

            with open(sarif_file, "w") as f:
                json.dump(sarif_data, f, indent=2)

            print(f"✅ Bandit SARIF report converted from JSON: {sarif_file}")
            return sarif_file

        except Exception as e:
            print(f"❌ Error converting Bandit JSON to SARIF: {e}")
            return None

    def _bandit_json_to_sarif(self, bandit_data: dict[str, Any]) -> dict[str, Any]:
        """Convert Bandit JSON format to SARIF 2.1.0 format."""
        sarif_data = {
            "version": "2.1.0",
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "Bandit",
                            "version": "1.8.0",
                            "informationUri": "https://bandit.readthedocs.io/",
                            "rules": [],
                        }
                    },
                    "results": [],
                }
            ],
        }

        # Convert results
        for result in bandit_data.get("results", []):
            sarif_result = {
                "ruleId": result.get("test_id", "unknown"),
                "message": {"text": result.get("issue_text", "Security issue detected")},
                "level": self._bandit_severity_to_sarif(result.get("issue_severity", "MEDIUM")),
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": result.get("filename", "unknown")},
                            "region": {"startLine": result.get("line_number", 1), "startColumn": 1},
                        }
                    }
                ],
            }

            sarif_data["runs"][0]["results"].append(sarif_result)

        return sarif_data

    def _bandit_severity_to_sarif(self, severity: str) -> str:
        """Convert Bandit severity to SARIF level."""
        severity_map = {"HIGH": "error", "MEDIUM": "warning", "LOW": "note"}
        return severity_map.get(severity.upper(), "warning")

    def validate_sarif(self, sarif_file: Path) -> bool:
        """Validate SARIF file format."""
        try:
            with open(sarif_file) as f:
                data = json.load(f)

            # Basic SARIF validation
            if not isinstance(data, dict):
                return False

            if data.get("version") != "2.1.0":
                print(f"⚠️ {sarif_file.name}: Non-standard SARIF version: {data.get('version')}")

            if "runs" not in data:
                print(f"❌ {sarif_file.name}: Missing 'runs' property")
                return False

            if not isinstance(data["runs"], list):
                print(f"❌ {sarif_file.name}: 'runs' must be an array")
                return False

            print(f"✅ {sarif_file.name}: Valid SARIF format")
            return True

        except json.JSONDecodeError as e:
            print(f"❌ {sarif_file.name}: Invalid JSON: {e}")
            return False
        except Exception as e:
            print(f"❌ {sarif_file.name}: Validation error: {e}")
            return False

    def aggregate_sarif_reports(self, sarif_files: list[Path]) -> Path:
        """Aggregate multiple SARIF reports into a unified report."""
        unified_report = {
            "version": "2.1.0",
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "runs": [],
        }

        for sarif_file in sarif_files:
            if not sarif_file.exists():
                continue

            try:
                with open(sarif_file) as f:
                    data = json.load(f)

                if "runs" in data and isinstance(data["runs"], list):
                    # Add metadata to distinguish tool runs
                    for run in data["runs"]:
                        if "tool" in run and "driver" in run["tool"]:
                            driver = run["tool"]["driver"]
                            driver["version"] = driver.get("version", "unknown")
                            driver["informationUri"] = driver.get("informationUri", "")

                        # Add timestamp (fixed deprecation warning)
                        run["invocations"] = run.get("invocations", [])
                        if not run["invocations"]:
                            run["invocations"].append({})
                        run["invocations"][0]["startTimeUtc"] = datetime.now(timezone.utc).isoformat()

                    unified_report["runs"].extend(data["runs"])
                    print(f"📄 Added {len(data['runs'])} run(s) from {sarif_file.name}")

            except Exception as e:
                print(f"⚠️ Error processing {sarif_file.name}: {e}")

        # Write unified report
        output_file = self.output_dir / "unified-security-report.sarif"
        with open(output_file, "w") as f:
            json.dump(unified_report, f, indent=2)

        print(f"📊 Unified SARIF report created: {output_file}")
        print(f"📈 Total runs: {len(unified_report['runs'])}")

        return output_file

    def generate_summary(self, sarif_files: list[Path]) -> None:
        """Generate a human-readable summary of security findings."""
        summary_file = self.output_dir / "security-summary.md"

        total_issues = 0
        issues_by_tool = {}
        issues_by_severity = {"error": 0, "warning": 0, "note": 0}

        for sarif_file in sarif_files:
            if not sarif_file.exists():
                continue

            try:
                with open(sarif_file) as f:
                    data = json.load(f)

                tool_name = sarif_file.stem
                tool_issues = 0

                for run in data.get("runs", []):
                    results = run.get("results", [])
                    tool_issues += len(results)

                    for result in results:
                        level = result.get("level", "warning")
                        if level in issues_by_severity:
                            issues_by_severity[level] += 1
                        else:
                            issues_by_severity["warning"] += 1

                issues_by_tool[tool_name] = tool_issues
                total_issues += tool_issues

            except Exception as e:
                print(f"⚠️ Error analyzing {sarif_file.name}: {e}")

        # Generate markdown summary
        with open(summary_file, "w") as f:
            f.write("# Security Scan Summary\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Overview\n\n")
            f.write(f"- **Total Issues:** {total_issues}\n")
            f.write(f"- **Errors:** {issues_by_severity['error']}\n")
            f.write(f"- **Warnings:** {issues_by_severity['warning']}\n")
            f.write(f"- **Notes:** {issues_by_severity['note']}\n\n")

            f.write("## Issues by Tool\n\n")
            for tool, count in issues_by_tool.items():
                f.write(f"- **{tool.title()}:** {count} issues\n")

            f.write("\n## SARIF Reports\n\n")
            for sarif_file in sarif_files:
                if sarif_file.exists():
                    f.write(f"- [{sarif_file.name}](./{sarif_file.name})\n")

            f.write("\n- [Unified Report](./unified-security-report.sarif)\n")

            f.write("\n## IDE Integration\n\n")
            f.write("To integrate these security findings with your IDE:\n\n")
            f.write("1. **VS Code**: Install the SARIF Viewer extension and open `unified-security-report.sarif`\n")
            f.write("2. **IntelliJ/PyCharm**: Use the SARIF plugin to import the unified report\n")
            f.write("3. **GitHub**: Upload SARIF files to GitHub Security tab for repository-wide analysis\n")

        print(f"📋 Security summary generated: {summary_file}")

    def run_all(self, validate: bool = True) -> None:
        """Run all security tools and generate unified SARIF report."""
        print("🚀 Starting unified SARIF report generation...")
        print(f"📁 Output directory: {self.output_dir}")

        sarif_files = []

        # Run Semgrep
        semgrep_sarif = self.run_semgrep_sarif()
        if semgrep_sarif:
            sarif_files.append(semgrep_sarif)

        # Run Bandit
        bandit_sarif = self.run_bandit_sarif()
        if bandit_sarif:
            sarif_files.append(bandit_sarif)

        if not sarif_files:
            print("❌ No SARIF reports generated")
            return

        # Validate SARIF files
        if validate:
            print("\n🔍 Validating SARIF reports...")
            valid_files = []
            for sarif_file in sarif_files:
                if self.validate_sarif(sarif_file):
                    valid_files.append(sarif_file)
            sarif_files = valid_files

        if not sarif_files:
            print("❌ No valid SARIF reports to aggregate")
            return

        # Aggregate reports
        print("\n📊 Aggregating SARIF reports...")
        unified_report = self.aggregate_sarif_reports(sarif_files)

        # Validate unified report
        if validate and self.validate_sarif(unified_report):
            print("✅ Unified SARIF report is valid")

        # Generate summary
        print("\n📋 Generating security summary...")
        self.generate_summary(sarif_files)

        print("\n🎉 SARIF report generation complete!")
        print(f"📁 Reports available in: {self.output_dir}")
        print(f"📊 Unified report: {unified_report}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate unified SARIF security reports")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("security-reports"),
        help="Output directory for SARIF reports (default: security-reports)",
    )
    parser.add_argument("--no-validate", action="store_true", help="Skip SARIF validation")

    args = parser.parse_args()

    generator = SARIFGenerator(output_dir=args.output_dir)
    generator.run_all(validate=not args.no_validate)


if __name__ == "__main__":
    main()
