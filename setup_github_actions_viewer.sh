#!/bin/bash

# GitHub Actions Log Viewer Setup Script

echo "🚀 Setting up GitHub Actions Log Viewer..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Install required Python packages
echo "📦 Installing required Python packages..."
pip3 install requests

# Make the script executable
chmod +x github_actions_log_viewer.py

echo "🔧 Setting up GitHub token..."
echo "You need to create a GitHub Personal Access Token with 'repo' and 'actions' scopes."
echo ""
echo "Steps to create a token:"
echo "1. Go to: https://github.com/settings/tokens"
echo "2. Click 'Generate new token (classic)'"
echo "3. Select scopes: 'repo' and 'actions'"
echo "4. Copy the generated token"
echo ""

# Check if GITHUB_TOKEN is already set
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GITHUB_TOKEN environment variable is not set."
    echo ""
    echo "To set it temporarily:"
    echo "export GITHUB_TOKEN='your_token_here'"
    echo ""
    echo "To set it permanently, add the above line to your ~/.bashrc or ~/.zshrc"
    echo ""
    read -p "Do you want to set GITHUB_TOKEN now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your GitHub token: " -s token
        echo
        export GITHUB_TOKEN="$token"
        echo "✅ GITHUB_TOKEN set for this session."
        echo "To make it permanent, add this to your shell profile:"
        echo "export GITHUB_TOKEN='$token'"
    fi
else
    echo "✅ GITHUB_TOKEN is already set."
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Test the installation with:"
echo "python3 github_actions_log_viewer.py --help"
echo ""
echo "Example usage:"
echo "python3 github_actions_log_viewer.py fernandoduarte china_data"
echo "python3 github_actions_log_viewer.py fernandoduarte china_data --conclusion failure"
echo "python3 github_actions_log_viewer.py fernandoduarte china_data --show-jobs"
echo ""
echo "For more information, see GITHUB_ACTIONS_GUIDE.md"
