# AI Development Context for China Data Project

## Project Overview

This is an economic data processing pipeline for China, designed to download, process, and analyze economic
indicators from various sources like the World Bank WDI.

## Architecture Patterns

### Core Patterns Used

- **Repository Pattern**: `utils/data_sources/` - Encapsulates data access logic
- **Strategy Pattern**: `utils/extrapolation_methods/` - Different forecasting algorithms
- **Observer Pattern**: Validation events and error handling
- **Factory Pattern**: `tests/factories.py` - Test data generation

### Key Components

1. **Data Sources** (`utils/data_sources/`): Download and cache data
2. **Processors** (`utils/processor_dataframe/`): Transform and validate
3. **Economic Indicators** (`utils/economic_indicators/`): Calculate derived metrics
4. **Extrapolation** (`utils/extrapolation_methods/`): Future projections
5. **Output** (`utils/output/`): Export formatted results

## Development Guidelines

### Code Quality Standards

- **Test Coverage**: Minimum 80% (pytest + hypothesis)
- **Type Coverage**: Minimum 90% (mypy strict mode)
- **Complexity**: Maximum C rating (radon)
- **Security**: Pass all bandit checks
- **Documentation**: Minimum 80% docstring coverage

### Technology Stack

- **Python**: 3.10+ with modern features
- **Package Manager**: UV for fast dependency resolution
- **Testing**: pytest with property-based testing (hypothesis)
- **Linting**: Ruff (modern, fast linter)
- **Type Checking**: mypy with strict configuration
- **Documentation**: MkDocs with Material theme
- **CI/CD**: GitHub Actions with UV optimization

### Data Flow Understanding

1. **Download**: Fetch from World Bank WDI API with caching
2. **Process**: Clean, validate, handle missing data
3. **Calculate**: Derive TFP, capital stock, productivity metrics
4. **Extrapolate**: Project future years using ARIMA/regression
5. **Export**: Generate CSV files and markdown reports

### Key Files to Understand

- `china_data_downloader.py`: Main download orchestrator
- `china_data_processor.py`: Main processing orchestrator
- `config.py` + `config_schema.py`: Configuration management
- `utils/data_sources/wdi_downloader.py`: World Bank API client
- `utils/economic_indicators/`: Core economic calculations

### Testing Strategy

The project uses pytest for testing with the following structure:

- Unit tests for individual functions and classes
- Integration tests for data processing workflows
- Property-based testing with Hypothesis for edge cases
- Test fixtures for common data scenarios

### Error Handling Philosophy

- **Graceful Degradation**: Continue processing when possible
- **Comprehensive Logging**: Structured logs with context
- **Validation Gates**: Early data quality checks
- **Retry Logic**: Robust network error handling

### AI Assistant Guidelines

When working on this codebase:

1. **Respect Architecture**: Follow established patterns
2. **Maintain Quality**: Don't reduce test coverage or type safety
3. **Document Changes**: Update docstrings and comments
4. **Consider Performance**: This processes large economic datasets
5. **Validate Economics**: Ensure calculations are economically sound
6. **Test Thoroughly**: Add tests for new functionality
7. **Handle Errors**: Consider network failures and data issues

### Common Tasks

- Adding new data sources: Follow repository pattern in `utils/data_sources/`
- New economic indicators: Use `utils/economic_indicators/` structure
- New extrapolation methods: Implement strategy pattern in `utils/extrapolation_methods/`
- Output formats: Extend `utils/output/` with proper templates

### Dependencies to Know

- **pandas**: Primary data manipulation
- **numpy**: Numerical computations
- **requests**: HTTP API calls with caching
- **statsmodels**: ARIMA and econometric models
- **scikit-learn**: Machine learning for projections
- **jinja2**: Template rendering for outputs
- **structlog**: Structured logging
- **pydantic**: Configuration validation

This context helps AI assistants understand the project's purpose, architecture, and development practices for
more effective collaboration.
