# VS Code Development Container

This directory contains the VS Code Development Container configuration for the China Data Analysis project. The devcontainer provides a consistent, fully-configured development environment that works across different machines and operating systems.

## 🚀 Quick Start

### Prerequisites

1. **VS Code** with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. **Docker Desktop** (or Docker Engine on Linux)

### Getting Started

1. **Clone the repository** (if you haven't already):

   ```bash
   git clone <repository-url>
   cd china_data
   ```

2. **Open in VS Code**:

   ```bash
   code .
   ```

3. **Reopen in Container**:

   - VS Code should automatically detect the devcontainer configuration
   - Click "Reopen in Container" when prompted, or
   - Use Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`) → "Dev Containers: Reopen in Container"

4. **Wait for setup**: The container will build and install all dependencies automatically (first time takes ~5-10 minutes)

## 🛠 What's Included

### Base Environment

- **Python 3.11** with all project dependencies
- **Git** and **GitHub CLI** for version control
- **Docker-in-Docker** for container operations
- **SQLite3** for database operations

### VS Code Extensions

- **Python Development**: Python, Black, isort, Pylint, MyPy, Ruff
- **Jupyter Notebooks**: Full Jupyter support with renderers
- **Data Science**: Data Wrangler, Rainbow CSV
- **Git Integration**: GitLens, GitHub Pull Requests
- **Documentation**: Markdown tools, Mermaid diagrams
- **Testing**: pytest integration
- **Code Quality**: Various linting and formatting tools

### Pre-configured Tools

- **Black** formatter (120 character line length)
- **isort** import sorting
- **Ruff** fast Python linter
- **MyPy** static type checking
- **pytest** testing framework
- **pre-commit** hooks
- **Jupyter Lab** with extensions

## 📁 Development Workflow

### Running the Data Pipeline

```bash
# Run the complete pipeline
./setup.sh

# Run with development mode (includes tests)
./setup.sh --dev

# Run with specific parameters
./setup.sh -a=0.5 -k=3.0 --end-year=2024
```

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
ruff check .

# Type checking
mypy .

# Run all pre-commit hooks
pre-commit run --all-files
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=utils

# Run specific test file
pytest tests/test_specific.py
```

### Documentation

```bash
# Serve documentation locally
mkdocs serve --dev-addr=0.0.0.0:8000

# Build documentation
mkdocs build
```

### Jupyter Development

```bash
# Start Jupyter Lab (accessible at http://localhost:8888)
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root
```

## 🔧 Configuration Details

### Python Environment

- **Interpreter**: `/usr/local/bin/python` (Python 3.11)
- **Package Manager**: `uv` for fast dependency resolution
- **Virtual Environment**: Managed automatically by the container

### Code Formatting

- **Line Length**: 120 characters
- **Formatter**: Black with isort integration
- **Auto-format**: On save
- **Import Organization**: Automatic with isort

### Testing Configuration

- **Framework**: pytest
- **Test Discovery**: Automatic in `tests/` directory
- **Coverage**: Available with pytest-cov

### Port Forwarding

- **8888**: Jupyter Lab server
- **8000**: MkDocs development server

## 🐛 Troubleshooting

### Container Won't Start

1. Ensure Docker is running
2. Check Docker has sufficient resources (4GB+ RAM recommended)
3. Try rebuilding: Command Palette → "Dev Containers: Rebuild Container"

### Dependencies Not Installing

1. Check internet connection
2. Try rebuilding with no cache: "Dev Containers: Rebuild Container Without Cache"
3. Check the setup log in VS Code terminal

### Git Issues

1. Ensure your Git credentials are configured
2. The container automatically configures Git safe directories
3. SSH keys from your host should be forwarded automatically

### Performance Issues

1. Increase Docker memory allocation
2. Use volume mounts for better I/O performance
3. Consider using Docker Desktop with WSL2 on Windows

## 🔄 Updating the Container

When dependencies or configuration changes:

1. **Rebuild Container**: Command Palette → "Dev Containers: Rebuild Container"
2. **Update Dependencies**: The setup script will automatically install new dependencies
3. **Extension Updates**: VS Code will prompt to update extensions

## 📚 Additional Resources

- [VS Code Dev Containers Documentation](https://code.visualstudio.com/docs/remote/containers)
- [Docker Documentation](https://docs.docker.com/)
- [Project Documentation](../docs/)

## 🤝 Contributing

When modifying the devcontainer configuration:

1. Test changes thoroughly
2. Update this README if needed
3. Consider backward compatibility
4. Document any new requirements or features

---

**Happy coding! 🎉**
