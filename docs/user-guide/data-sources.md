# Data Sources

The China Economic Data Analysis package supports multiple authoritative economic data sources.

## Supported Sources

### World Bank World Development Indicators (WDI)

The World Bank's comprehensive database of development indicators.

**Key Features:**

- 1,400+ indicators
- Data from 1960 onwards
- Annual frequency
- Global coverage

**Indicators Include:**

- GDP and economic growth
- Population and demographics
- Education and health
- Environment and energy
- Infrastructure and trade

### International Monetary Fund (IMF)

IMF's economic and financial data.

**Key Features:**

- Balance of payments
- Government finance statistics
- International financial statistics
- Exchange rates

**Data Coverage:**

- Quarterly and annual data
- Historical time series
- Forecasts and projections

### Penn World Table (PWT)

Comprehensive dataset for international comparisons.

**Key Features:**

- PPP-adjusted data
- Productivity measures
- Capital stock estimates
- Price level comparisons

**Version Support:**

- PWT 10.0 (latest)
- Historical versions available

## Data Quality

### Validation Checks

- Missing value detection
- Outlier identification
- Consistency verification
- Time series continuity

### Data Cleaning

- Standardized formatting
- Unit conversions
- Currency adjustments
- Interpolation methods

## Configuration

Enable/disable sources in your `.env` file:

```bash
INCLUDE_WDI=true
INCLUDE_IMF=true
INCLUDE_PWT=true
```

## Custom Sources

The package is extensible - you can add custom data sources by:

1. Creating a new module in `utils/data_sources/`
2. Implementing the required interface
3. Registering the source in the configuration

See the [Development Guide](../development/contributing.md) for details.
