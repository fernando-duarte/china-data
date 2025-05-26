# GitHub CLI Quick Reference for Actions Logs

Since you have GitHub CLI (`gh`) installed, here are quick commands to access your CI and GitHub Actions logs:

## Authentication

First, make sure you're authenticated:

```bash
gh auth status
# If not authenticated:
gh auth login
```

## Basic Commands

### List Recent Workflow Runs

```bash
# List all recent runs
gh run list

# List runs for specific workflow
gh run list --workflow=ci.yml

# List only failed runs
gh run list --status=failure

# List runs for specific branch
gh run list --branch=main
```

### View Specific Run Details

```bash
# View run details
gh run view RUN_ID

# View run with jobs
gh run view RUN_ID --verbose

# View latest run
gh run view --web  # Opens in browser
```

### Download Logs

```bash
# Download logs for specific run
gh run download RUN_ID

# Download logs to specific directory
gh run download RUN_ID --dir ./logs

# Download logs for latest run
gh run download $(gh run list --limit 1 --json databaseId --jq '.[0].databaseId')
```

### Watch Live Runs

```bash
# Watch a running workflow
gh run watch RUN_ID

# Watch latest run
gh run watch
```

## Useful Combinations

### Find and Download Failed Run Logs

```bash
# Get the latest failed run ID and download its logs
FAILED_RUN=$(gh run list --status=failure --limit=1 --json databaseId --jq '.[0].databaseId')
gh run download $FAILED_RUN --dir ./failed_logs
```

### Monitor CI Status

```bash
# Check if latest CI run passed
gh run list --workflow=ci.yml --limit=1 --json conclusion --jq '.[0].conclusion'
```

### View Logs in Terminal

```bash
# View logs for a specific run (requires downloading first)
gh run download RUN_ID
# Then extract and view the downloaded files
```

## Your Repository Specific Commands

Based on your repository structure, here are commands tailored for your workflows:

```bash
# Check CI status
gh run list --workflow=ci.yml --limit=5

# Check documentation build status
gh run list --workflow=docs.yml --limit=5

# Check security scans
gh run list --workflow=security-enhanced.yml --limit=5

# Download logs for latest CI run
gh run download $(gh run list --workflow=ci.yml --limit=1 --json databaseId --jq '.[0].databaseId')
```

## Pro Tips

1. **Use JSON output for scripting**:

   ```bash
   gh run list --json databaseId,status,conclusion,workflowName
   ```

2. **Filter by date**:

   ```bash
   gh run list --created="2024-01-01..2024-01-31"
   ```

3. **Combine with other tools**:

   ```bash
   # Get failed runs and their details
   gh run list --status=failure --json databaseId,workflowName,conclusion | jq '.[]'
   ```

4. **Set up aliases** in your shell:

   ```bash
   alias ghr='gh run list'
   alias ghrf='gh run list --status=failure'
   alias ghrv='gh run view'
   alias ghrd='gh run download'
   ```

## Quick Troubleshooting

If you encounter issues:

1. **Check authentication**: `gh auth status`
2. **Refresh token**: `gh auth refresh`
3. **Check repository access**: `gh repo view`

## Integration with Your Workflow

Add to your `.zshrc` or `.bashrc`:

```bash
# Function to quickly check CI status
check_ci() {
    echo "Latest CI runs:"
    gh run list --workflow=ci.yml --limit=5

    echo -e "\nLatest failed runs:"
    gh run list --status=failure --limit=3
}

# Function to download latest failed logs
download_failed_logs() {
    FAILED_RUN=$(gh run list --status=failure --limit=1 --json databaseId --jq '.[0].databaseId')
    if [ "$FAILED_RUN" != "null" ]; then
        echo "Downloading logs for failed run: $FAILED_RUN"
        gh run download $FAILED_RUN --dir ./failed_logs_$(date +%Y%m%d_%H%M%S)
    else
        echo "No failed runs found"
    fi
}
```

This gives you immediate access to your GitHub Actions logs without needing to set up additional tools!
