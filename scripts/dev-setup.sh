#!/bin/bash
# scripts/dev-setup.sh - One-command development environment

set -euo pipefail

echo "🚀 Setting up China Data Processor development environment..."

# Check prerequisites
check_prerequisites() {
    echo "📋 Checking prerequisites..."

    # Check if Python 3.10+ is available
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required but not found"
        exit 1
    fi

    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    required_version="3.10"

    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
        echo "❌ Python 3.10 or higher is required. Found: $python_version"
        exit 1
    fi

    echo "✅ Python $python_version found"

    # Check if Git is available
    if ! command -v git &> /dev/null; then
        echo "❌ Git is required but not found"
        exit 1
    fi

    echo "✅ Git found"
}

# Install UV if not present
install_uv() {
    if command -v uv &> /dev/null; then
        echo "✅ UV already installed: $(uv --version)"
    else
        echo "📦 Installing UV package manager..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
        echo "✅ UV installed: $(uv --version)"
    fi
}

# Setup virtual environment and dependencies
setup_environment() {
    echo "🔧 Setting up Python environment..."

    # Create virtual environment and install dependencies
    uv sync --all-extras
    echo "✅ Dependencies installed"
}

# Setup pre-commit hooks
setup_pre_commit() {
    echo "🪝 Setting up pre-commit hooks..."

    uv run pre-commit install
    uv run pre-commit install --hook-type commit-msg
    echo "✅ Pre-commit hooks installed"
}

# Create necessary directories
setup_directories() {
    echo "📁 Creating necessary directories..."

    mkdir -p input output workflow_outputs
    touch input/.gitkeep output/.gitkeep workflow_outputs/.gitkeep
    echo "✅ Directories created"
}

# Setup IDE configuration
setup_ide() {
    echo "🛠️ Setting up IDE configuration..."

    # Create .env.example if it doesn't exist
    if [ ! -f .env.example ]; then
        cat > .env.example << 'EOF'
# Environment Configuration
ENVIRONMENT=development
CHINA_DATA_LOG_LEVEL=INFO
CHINA_DATA_STRUCTURED_LOGGING_ENABLED=true
OTEL_ENDPOINT=http://localhost:4317
UV_CACHE_DIR=/tmp/uv-cache
DB_PASSWORD=development
EOF
        echo "✅ Created .env.example"
    fi

    # Setup local .env if it doesn't exist
    if [ ! -f .env ]; then
        cp .env.example .env
        echo "✅ Created .env from template"
    fi
}

# Run initial tests
run_initial_tests() {
    echo "🧪 Running initial tests..."

    # Run a quick test to verify everything works
    if uv run pytest tests/ -x --tb=short -q; then
        echo "✅ Initial tests passed"
    else
        echo "⚠️ Some tests failed - this might be expected for initial setup"
    fi
}

# Display helpful information
show_next_steps() {
    echo ""
    echo "🎉 Development environment setup complete!"
    echo ""
    echo "📋 Next steps:"
    echo "  1. Activate the environment: source .venv/bin/activate"
    echo "  2. Run data download: uv run python china_data_downloader.py"
    echo "  3. Process data: uv run python china_data_processor.py"
    echo "  4. Run tests: uv run pytest"
    echo "  5. Start development: uv run python -m china_data_processor --dev"
    echo ""
    echo "📖 Available commands:"
    echo "  make dev          - Start development mode"
    echo "  make test         - Run comprehensive test suite"
    echo "  make lint         - Run code quality checks"
    echo "  make security     - Run security scans"
    echo "  make docs-serve   - Start documentation server"
    echo ""
    echo "🔧 IDE Setup:"
    echo "  - VS Code: Install recommended extensions"
    echo "  - PyCharm: Configure interpreter to .venv/bin/python"
    echo ""
    echo "📚 Documentation: https://fernandoduarte.github.io/china_data/"
}

# Main execution
main() {
    check_prerequisites
    install_uv
    setup_environment
    setup_pre_commit
    setup_directories
    setup_ide
    run_initial_tests
    show_next_steps
}

# Run main function
main "$@"
