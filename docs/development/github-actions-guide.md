# GitHub Actions Log Viewer Guide

This guide explains how to access and view your GitHub Actions CI logs using the provided script and other methods.

## Prerequisites

1. **GitHub Personal Access Token**: You need a GitHub personal access token with `repo` and `actions` scopes.
2. **Python Dependencies**: Install required packages:

   ```bash
   pip install requests
   ```

## Setting Up Your GitHub Token

### Option 1: Environment Variable (Recommended)

```bash
export GITHUB_TOKEN="your_github_token_here"
```

### Option 2: Pass as Command Line Argument

Use the `--token` flag when running the script.

## Getting Your GitHub Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Select scopes: `repo` and `actions`
4. Copy the generated token

## Using the GitHub Actions Log Viewer Script

### Basic Usage

```bash
# View recent workflow runs
python3 github_actions_log_viewer.py fernandoduarte china_data

# View failed workflow runs only
python3 github_actions_log_viewer.py fernandoduarte china_data --conclusion failure

# View workflow runs for a specific branch
python3 github_actions_log_viewer.py fernandoduarte china_data --branch main

# Show jobs for each workflow run
python3 github_actions_log_viewer.py fernandoduarte china_data --show-jobs
```

### Advanced Usage

```bash
# Download logs for recent workflow runs
python3 github_actions_log_viewer.py fernandoduarte china_data --download-logs --output-dir ./logs

# View specific workflow run with jobs
python3 github_actions_log_viewer.py fernandoduarte china_data --run-id 123456789 --show-jobs

# Download and extract logs for a specific run
python3 github_actions_log_viewer.py fernandoduarte china_data --run-id 123456789 --download-logs

# Extract logs from a previously downloaded zip file
python3 github_actions_log_viewer.py fernandoduarte china_data --extract-logs workflow_run_123456789_logs.zip

# Filter logs by job name when extracting
python3 github_actions_log_viewer.py fernandoduarte china_data --extract-logs logs.zip --job-name "test"
```

### Command Line Options

- `--status`: Filter by status (`queued`, `in_progress`, `completed`)
- `--conclusion`: Filter by conclusion (`success`, `failure`, `neutral`, `cancelled`, `timed_out`, `action_required`, `skipped`)
- `--branch`: Filter by branch name
- `--run-id`: View specific workflow run
- `--download-logs`: Download log files
- `--output-dir`: Directory to save logs
- `--show-jobs`: Show jobs for workflow runs
- `--extract-logs`: Extract and display logs from zip file
- `--job-name`: Filter logs by job name
- `--limit`: Limit number of runs to display (default: 10)

## Alternative Methods to Access Logs

### 1. GitHub CLI (gh)

Install GitHub CLI and authenticate:

```bash
# Install gh (if not already installed)
brew install gh  # macOS
# or
sudo apt install gh  # Ubuntu

# Authenticate
gh auth login

# View workflow runs
gh run list --repo fernandoduarte/china_data

# View specific run
gh run view RUN_ID --repo fernandoduarte/china_data

# Download logs
gh run download RUN_ID --repo fernandoduarte/china_data
```

### 2. Direct API Calls with curl

```bash
# List workflow runs
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
     -H "Accept: application/vnd.github+json" \
     https://api.github.com/repos/fernandoduarte/china_data/actions/runs

# Get specific run
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
     -H "Accept: application/vnd.github+json" \
     https://api.github.com/repos/fernandoduarte/china_data/actions/runs/RUN_ID

# Download logs
curl -L -H "Authorization: Bearer $GITHUB_TOKEN" \
     -H "Accept: application/vnd.github+json" \
     https://api.github.com/repos/fernandoduarte/china_data/actions/runs/RUN_ID/logs \
     -o logs.zip
```

### 3. VS Code GitHub Actions Extension

1. Install the "GitHub Actions" extension in VS Code
2. Open your repository in VS Code
3. View the GitHub Actions panel
4. Click on workflow runs to see logs directly in VS Code

## Understanding Your Workflow Structure

Based on your repository, you have these workflow files:

- `ci.yml` - Main CI pipeline
- `docs.yml` - Documentation building
- `dependency-check.yml` - Dependency management
- `security-enhanced.yml` - Security scanning
- `vulnerability-scan.yml` - Vulnerability scanning
- `release.yml` - Release automation

## Common Use Cases

### 1. Debug Failed CI Runs

```bash
# Find recent failed runs
python3 github_actions_log_viewer.py fernandoduarte china_data --conclusion failure --limit 5

# Download logs for investigation
python3 github_actions_log_viewer.py fernandoduarte china_data --run-id FAILED_RUN_ID --download-logs
```

### 2. Monitor Specific Branch

```bash
# Check main branch status
python3 github_actions_log_viewer.py fernandoduarte china_data --branch main --status completed
```

### 3. Analyze Test Results

```bash
# Show jobs to see which tests failed
python3 github_actions_log_viewer.py fernandoduarte china_data --show-jobs --conclusion failure
```

## Troubleshooting

### Common Issues

1. **Authentication Error**: Ensure your GitHub token has the correct scopes (`repo` and `actions`)
2. **Rate Limiting**: GitHub API has rate limits. Wait a few minutes if you hit them
3. **Log Expiration**: GitHub Actions logs are only available for a limited time (typically 90 days)
4. **Permission Denied**: Ensure you have access to the repository

### Error Messages

- `410 Gone`: Logs have expired and are no longer available
- `403 Forbidden`: Token doesn't have required permissions
- `404 Not Found`: Repository or run doesn't exist or you don't have access

## Best Practices

1. **Use Environment Variables**: Store your GitHub token in environment variables, not in scripts
2. **Filter Results**: Use status and conclusion filters to find relevant runs quickly
3. **Download Selectively**: Only download logs you need to avoid unnecessary API calls
4. **Regular Cleanup**: Clean up downloaded log files periodically

## Integration with Your Development Workflow

### Pre-commit Hooks

You can integrate log checking into your development workflow:

```bash
# Check if latest CI run passed before pushing
python3 github_actions_log_viewer.py fernandoduarte china_data --branch $(git branch --show-current) --limit 1
```

### Automated Monitoring

Set up automated monitoring of your CI/CD pipeline:

```bash
# Create a script to check for failures
#!/bin/bash
FAILED_RUNS=$(python3 github_actions_log_viewer.py fernandoduarte china_data --conclusion failure --limit 1 | grep -c "failure")
if [ "$FAILED_RUNS" -gt 0 ]; then
    echo "Warning: Recent CI failures detected!"
    # Send notification or take action
fi
```

## Next Steps

1. Set up your GitHub token
2. Test the script with basic commands
3. Integrate into your development workflow
4. Consider setting up automated monitoring

For more advanced usage, refer to the [GitHub Actions API documentation](https://docs.github.com/en/rest/actions).
