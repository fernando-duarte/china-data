# Contributing

We welcome contributions to the China Economic Data Analysis package! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git
- UV package manager (recommended)

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/fernandoduarte/china_data.git
cd china_data

# One-command setup
make setup

# Verify installation
make test
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Follow our coding standards:

- Use type hints
- Write docstrings
- Add tests for new functionality
- Follow PEP 8 style guidelines

### 3. Run Quality Checks

```bash
# Format code
make format

# Run linting
make lint

# Run tests
make test

# Run security checks
make security
```

### 4. Commit Changes

We use conventional commits:

```bash
git commit -m "feat: add new data source connector"
git commit -m "fix: resolve data validation issue"
git commit -m "docs: update API documentation"
```

### 5. Submit Pull Request

- Push your branch to GitHub
- Create a pull request
- Ensure all CI checks pass
- Request review from maintainers

## Code Standards

### Python Style

- Follow PEP 8
- Use type hints for all functions
- Maximum line length: 120 characters
- Use descriptive variable names

### Documentation

- Write docstrings for all public functions
- Use Google-style docstrings
- Include examples in docstrings
- Update documentation for new features

### Testing

- Write unit tests for all new code
- Aim for >90% test coverage
- Use property-based testing for complex logic
- Include integration tests for new features

## Project Structure

```
china_data/
├── utils/                    # Core utilities
│   ├── data_sources/        # Data source connectors
│   ├── economic_indicators/ # Economic calculations
│   └── processor_dataframe/ # Data processing
├── tests/                   # Test suite
├── docs/                    # Documentation
├── scripts/                 # Utility scripts
└── output/                  # Generated outputs
```

## Adding New Features

### New Data Source

1. Create module in `utils/data_sources/`
2. Implement required interface
3. Add configuration options
4. Write comprehensive tests
5. Update documentation

### New Economic Indicator

1. Add calculation in `utils/economic_indicators/`
2. Include validation logic
3. Add unit tests
4. Document methodology

### New Output Format

1. Create exporter in `utils/output/`
2. Add configuration options
3. Include format validation
4. Add integration tests

## Testing

### Running Tests

```bash
# All tests
make test-all

# Specific test types
make test-unit
make test-integration
make test-property
make test-benchmark
```

### Writing Tests

```python
import pytest
from hypothesis import given, strategies as st

def test_data_validation():
    """Test data validation logic."""
    # Test implementation
    pass

@given(st.floats(min_value=0, max_value=100))
def test_calculation_property(value):
    """Property-based test for calculations."""
    result = calculate_indicator(value)
    assert result >= 0
```

## Documentation

### Building Docs

```bash
# Serve locally
make docs-serve

# Build static site
make docs-build

# Test documentation
make docs-test
```

### Writing Documentation

- Use Markdown format
- Include code examples
- Add diagrams where helpful
- Keep language clear and concise

## Release Process

1. Update version in `VERSION.txt`
2. Update `CHANGELOG.md`
3. Create release branch
4. Run full test suite
5. Create GitHub release
6. Deploy documentation

## Getting Help

- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas
- **Email**: <fernando_duarte@brown.edu>

## Code of Conduct

Please be respectful and inclusive in all interactions. We follow the [Contributor Covenant](https://www.contributor-covenant.org/) code of conduct.
