#!/usr/bin/env python3
"""GitHub Actions Log Viewer.

A script to fetch and view GitHub Actions workflow runs and logs.
"""

import argparse
import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

import requests


class GitHubActionsLogViewer:
    """GitHub Actions Log Viewer for fetching and displaying workflow information."""

    def __init__(self, token: str, owner: str, repo: str) -> None:
        """Initialize the GitHub Actions Log Viewer.

        Args:
            token: GitHub personal access token
            owner: Repository owner (username or organization)
            repo: Repository name
        """
        self.token = token
        self.owner = owner
        self.repo = repo
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def get_workflow_runs(
        self,
        status: str | None = None,
        conclusion: str | None = None,
        branch: str | None = None,
        per_page: int = 30,
    ) -> list[dict[str, Any]]:
        """Get workflow runs for the repository.

        Args:
            status: Filter by status (queued, in_progress, completed)
            conclusion: Filter by conclusion (success, failure, neutral, cancelled, etc.)
            branch: Filter by branch name
            per_page: Number of results per page (max 100)

        Returns:
            List of workflow runs
        """
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/actions/runs"
        params: dict[str, str | int] = {"per_page": per_page}

        if status:
            params["status"] = status
        if conclusion:
            params["conclusion"] = conclusion
        if branch:
            params["branch"] = branch

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching workflow runs: {e}")
            return []
        else:
            response_data = response.json()
            workflow_runs: list[dict[str, Any]] = response_data.get("workflow_runs", [])
            return workflow_runs

    def get_workflow_run_jobs(self, run_id: int) -> list[dict[str, Any]]:
        """Get jobs for a specific workflow run.

        Args:
            run_id: Workflow run ID

        Returns:
            List of jobs in the workflow run
        """
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/actions/runs/{run_id}/jobs"

        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching jobs for run {run_id}: {e}")
            return []
        else:
            response_data = response.json()
            jobs: list[dict[str, Any]] = response_data.get("jobs", [])
            return jobs

    def download_workflow_run_logs(self, run_id: int, output_dir: str | None = None) -> str | None:
        """Download logs for a workflow run.

        Args:
            run_id: Workflow run ID
            output_dir: Directory to save logs (optional)

        Returns:
            Path to downloaded logs or None if failed
        """
        url = f"{self.base_url}/repos/{self.owner}/{self.repo}/actions/runs/{run_id}/logs"

        try:
            response = requests.get(url, headers=self.headers, allow_redirects=True, timeout=30)
            response.raise_for_status()

            if output_dir:
                Path(output_dir).mkdir(parents=True, exist_ok=True)
                log_file = Path(output_dir) / f"workflow_run_{run_id}_logs.zip"
            else:
                log_file = Path(f"workflow_run_{run_id}_logs.zip")

            log_file.write_bytes(response.content)

            print(f"Downloaded logs to: {log_file}")
            return str(log_file)

        except requests.exceptions.RequestException as e:
            print(f"Error downloading logs for run {run_id}: {e}")
            return None

    def extract_and_display_logs(self, zip_path: str, job_name: str | None = None) -> None:
        """Extract and display logs from a zip file.

        Args:
            zip_path: Path to the zip file containing logs
            job_name: Specific job name to display (optional)
        """
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                # List all files in the zip
                file_list = zip_ref.namelist()

                if job_name:
                    # Filter files for specific job
                    matching_files = [f for f in file_list if job_name.lower() in f.lower()]
                    if not matching_files:
                        print(f"No logs found for job: {job_name}")
                        return
                    file_list = matching_files

                for file_name in file_list:
                    if file_name.endswith(".txt"):
                        print(f"\n{'=' * 60}")
                        print(f"LOG FILE: {file_name}")
                        print(f"{'=' * 60}")

                        with zip_ref.open(file_name) as log_file:
                            content = log_file.read().decode("utf-8", errors="ignore")
                            print(content)

                        print(f"{'=' * 60}\n")

        except (zipfile.BadZipFile, OSError) as e:
            print(f"Error extracting logs: {e}")

    def display_workflow_runs(self, runs: list[dict[str, Any]]) -> None:
        """Display workflow runs in a formatted table."""
        if not runs:
            print("No workflow runs found.")
            return

        print(f"\n{'ID':<12} {'Name':<25} {'Status':<12} {'Conclusion':<12} {'Branch':<15} {'Created':<20}")
        print("-" * 110)

        for run in runs:
            run_id = run.get("id", "N/A")
            name = run.get("name", "N/A")[:24]
            status = run.get("status", "N/A")
            conclusion = run.get("conclusion", "N/A") or "N/A"
            branch = run.get("head_branch", "N/A")[:14]
            created = run.get("created_at", "N/A")

            if created != "N/A":
                try:
                    created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    created = created_dt.strftime("%Y-%m-%d %H:%M")
                except ValueError:
                    # Keep original value if parsing fails
                    pass

            print(f"{run_id:<12} {name:<25} {status:<12} {conclusion:<12} {branch:<15} {created:<20}")

    def display_jobs(self, jobs: list[dict[str, Any]]) -> None:
        """Display jobs in a formatted table."""
        if not jobs:
            print("No jobs found.")
            return

        print(f"\n{'ID':<12} {'Name':<30} {'Status':<12} {'Conclusion':<12} {'Started':<20}")
        print("-" * 90)

        for job in jobs:
            job_id = job.get("id", "N/A")
            name = job.get("name", "N/A")[:29]
            status = job.get("status", "N/A")
            conclusion = job.get("conclusion", "N/A") or "N/A"
            started = job.get("started_at", "N/A")

            if started != "N/A":
                try:
                    started_dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
                    started = started_dt.strftime("%Y-%m-%d %H:%M")
                except ValueError:
                    # Keep original value if parsing fails
                    pass

            print(f"{job_id:<12} {name:<30} {status:<12} {conclusion:<12} {started:<20}")


def _handle_specific_run(viewer: GitHubActionsLogViewer, args: argparse.Namespace) -> None:
    """Handle operations for a specific workflow run.

    Args:
        viewer: GitHubActionsLogViewer instance
        args: Parsed command line arguments
    """
    print(f"Fetching details for workflow run: {args.run_id}")

    if args.show_jobs:
        jobs = viewer.get_workflow_run_jobs(args.run_id)
        viewer.display_jobs(jobs)

    if args.download_logs:
        log_file = viewer.download_workflow_run_logs(args.run_id, args.output_dir)
        if log_file and input("Extract and display logs? (y/N): ").lower() == "y":
            viewer.extract_and_display_logs(log_file, args.job_name)


def _handle_multiple_runs(viewer: GitHubActionsLogViewer, args: argparse.Namespace) -> None:
    """Handle operations for multiple workflow runs.

    Args:
        viewer: GitHubActionsLogViewer instance
        args: Parsed command line arguments
    """
    # Get workflow runs
    print(f"Fetching workflow runs for {args.owner}/{args.repo}...")
    runs = viewer.get_workflow_runs(
        status=args.status, conclusion=args.conclusion, branch=args.branch, per_page=args.limit
    )

    # Display runs
    viewer.display_workflow_runs(runs[: args.limit])

    # Show jobs if requested
    if args.show_jobs and runs:
        for run in runs[:3]:  # Show jobs for first 3 runs
            print(f"\nJobs for workflow run {run['id']} ({run['name']}):")
            jobs = viewer.get_workflow_run_jobs(run["id"])
            viewer.display_jobs(jobs)

    # Download logs if requested
    if args.download_logs and runs:
        for run in runs[: args.limit]:
            print(f"\nDownloading logs for run {run['id']}...")
            viewer.download_workflow_run_logs(run["id"], args.output_dir)


def main() -> None:
    """Main function to handle command line arguments and execute operations."""
    parser = argparse.ArgumentParser(description="GitHub Actions Log Viewer")
    parser.add_argument("owner", help="Repository owner (username or organization)")
    parser.add_argument("repo", help="Repository name")
    parser.add_argument("--token", help="GitHub personal access token (or set GITHUB_TOKEN env var)")
    parser.add_argument(
        "--status", choices=["queued", "in_progress", "completed"], help="Filter by workflow run status"
    )
    parser.add_argument(
        "--conclusion",
        choices=["success", "failure", "neutral", "cancelled", "timed_out", "action_required", "skipped"],
        help="Filter by workflow run conclusion",
    )
    parser.add_argument("--branch", help="Filter by branch name")
    parser.add_argument("--run-id", type=int, help="Specific workflow run ID to view")
    parser.add_argument("--download-logs", action="store_true", help="Download logs for the workflow runs")
    parser.add_argument("--output-dir", help="Directory to save downloaded logs")
    parser.add_argument("--show-jobs", action="store_true", help="Show jobs for each workflow run")
    parser.add_argument("--extract-logs", help="Extract and display logs from a zip file")
    parser.add_argument("--job-name", help="Filter logs by job name when extracting")
    parser.add_argument("--limit", type=int, default=10, help="Limit number of runs to display")

    args = parser.parse_args()

    # Get GitHub token
    token = args.token or os.getenv("GITHUB_TOKEN")
    if not token:
        print("Error: GitHub token required. Use --token or set GITHUB_TOKEN environment variable.")
        sys.exit(1)

    # If extracting logs from a file, do that and exit
    if args.extract_logs:
        viewer = GitHubActionsLogViewer(token, args.owner, args.repo)
        viewer.extract_and_display_logs(args.extract_logs, args.job_name)
        return

    # Initialize the viewer
    viewer = GitHubActionsLogViewer(token, args.owner, args.repo)

    # If specific run ID provided, focus on that
    if args.run_id:
        _handle_specific_run(viewer, args)
    else:
        _handle_multiple_runs(viewer, args)


if __name__ == "__main__":
    main()
