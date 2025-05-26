#!/bin/bash
set -e

echo "🚀 Setting up China Data Analysis development environment..."

# Update system packages
sudo apt-get update && sudo apt-get install -y \
    git \
    curl \
    wget \
    build-essential \
    sqlite3 \
    && sudo apt-get clean

# Upgrade pip and install uv for faster dependency resolution
pip install --upgrade pip
pip install uv

# Install project dependencies using uv for speed
echo "📦 Installing project dependencies..."
if ! uv pip install -e ".[dev]"; then
    echo "⚠️  uv installation failed, falling back to pip..."
    pip install -e ".[dev]"
fi

# Install pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
pre-commit install

# Create output directories
echo "📁 Creating output directories..."
mkdir -p output
mkdir -p workflow_outputs

# Set up git configuration for the container
echo "🔧 Configuring git..."
git config --global init.defaultBranch main
git config --global pull.rebase false

# Install Jupyter Lab extensions for better data science experience
echo "🔬 Setting up Jupyter Lab..."
pip install jupyterlab-git jupyterlab-lsp python-lsp-server[all]

# Create a welcome message
echo "✅ Development environment setup complete!"
echo ""
echo "🎯 Quick start commands:"
echo "  • Run data pipeline: ./setup.sh"
echo "  • Run tests: pytest"
echo "  • Start Jupyter Lab: jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root"
echo "  • Build docs: mkdocs serve --dev-addr=0.0.0.0:8000"
echo "  • Format code: black ."
echo "  • Lint code: ruff check ."
echo "  • Type check: mypy ."
echo ""
echo "📚 The project is ready for development!"
