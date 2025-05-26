# Data Sources

This section documents the data source modules that handle downloading and processing data from external APIs.

## World Bank Data Source

::: utils.data_sources.world_bank
options:
show_root_heading: true
show_source: true
heading_level: 3

## Penn World Table Data Source

::: utils.data_sources.penn_world_table
options:
show_root_heading: true
show_source: true
heading_level: 3

## IMF Fiscal Monitor Data Source

::: utils.data_sources.imf_fiscal_monitor
options:
show_root_heading: true
show_source: true
heading_level: 3

## Base Data Source

::: utils.data_sources.base
options:
show_root_heading: true
show_source: true
heading_level: 3

## Usage Examples

### World Bank Data

```python
from utils.data_sources.world_bank import WorldBankDataSource

# Initialize data source
wb_source = WorldBankDataSource()

# Fetch specific indicators for China
indicators = [
    'NY.GDP.MKTP.KD',      # GDP (constant 2015 US$)
    'SP.POP.TOTL',         # Population, total
    'SL.TLF.TOTL.IN'       # Labor force, total
]

data = wb_source.fetch_data(
    indicators=indicators,
    country_code='CHN',
    start_year=1990,
    end_year=2025
)

print(f"Downloaded {len(data)} data points")
```

### Penn World Table Data

```python
from utils.data_sources.penn_world_table import PennWorldTableDataSource

# Initialize data source
pwt_source = PennWorldTableDataSource()

# Fetch capital stock and productivity data
data = pwt_source.fetch_data(
    country_code='CHN',
    variables=['ck', 'ctfp', 'hc']  # Capital stock, TFP, Human capital
)

# Display available years
print(f"Data coverage: {data.index.min()} - {data.index.max()}")
```

### IMF Fiscal Monitor Data

```python
from utils.data_sources.imf_fiscal_monitor import IMFFiscalMonitorDataSource

# Initialize data source
imf_source = IMFFiscalMonitorDataSource()

# Fetch fiscal indicators
fiscal_data = imf_source.fetch_data(
    country_code='CHN',
    indicators=['GGXWDG_NGDP', 'GGSB_NPGDP']  # Debt-to-GDP, Fiscal balance
)

print(f"Fiscal data: {fiscal_data.head()}")
```

### Custom Data Source

You can create custom data sources by extending the base class:

```python
from utils.data_sources.base import BaseDataSource
import pandas as pd

class CustomDataSource(BaseDataSource):
    """Custom data source implementation."""

    def __init__(self):
        super().__init__(source_name="Custom Source")

    def fetch_data(self, **kwargs) -> pd.DataFrame:
        """Fetch data from custom source."""
        # Implement your data fetching logic here
        data = pd.DataFrame({
            'year': range(2000, 2025),
            'custom_indicator': range(25)
        })
        data.set_index('year', inplace=True)
        return data

    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate the fetched data."""
        return not data.empty and data.index.is_monotonic_increasing

# Usage
custom_source = CustomDataSource()
data = custom_source.fetch_data()
```

## Data Source Configuration

### Caching Configuration

```python
from utils.data_sources.world_bank import WorldBankDataSource

# Configure caching
wb_source = WorldBankDataSource(
    cache_enabled=True,
    cache_expire_hours=24,
    cache_directory=".data_cache"
)

# Data will be cached for 24 hours
data = wb_source.fetch_data(['NY.GDP.MKTP.KD'])
```

### Rate Limiting

```python
from utils.data_sources.world_bank import WorldBankDataSource

# Configure rate limiting to respect API limits
wb_source = WorldBankDataSource(
    requests_per_second=5,  # Max 5 requests per second
    retry_attempts=3,       # Retry failed requests 3 times
    retry_delay=1.0        # Wait 1 second between retries
)
```

### Error Handling

```python
from utils.data_sources.world_bank import WorldBankDataSource
from utils.error_handling.exceptions import DataDownloadError

wb_source = WorldBankDataSource()

try:
    data = wb_source.fetch_data(['INVALID_INDICATOR'])
except DataDownloadError as e:
    print(f"Failed to download data: {e}")
    # Handle the error appropriately
```

## Data Quality and Validation

### Automatic Validation

All data sources implement automatic validation:

```python
from utils.data_sources.world_bank import WorldBankDataSource

wb_source = WorldBankDataSource()
data = wb_source.fetch_data(['NY.GDP.MKTP.KD'])

# Validation is performed automatically
if wb_source.validate_data(data):
    print("Data validation passed")
else:
    print("Data validation failed")
```

### Custom Validation Rules

```python
from utils.data_sources.base import BaseDataSource
import pandas as pd

class ValidatedDataSource(BaseDataSource):
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Custom validation rules."""
        # Check for minimum data coverage
        if len(data) < 10:
            return False

        # Check for reasonable value ranges
        if 'gdp' in data.columns:
            if (data['gdp'] < 0).any():
                return False

        # Check for excessive missing values
        missing_ratio = data.isnull().sum().sum() / (len(data) * len(data.columns))
        if missing_ratio > 0.5:  # More than 50% missing
            return False

        return True
```

## Performance Optimization

### Parallel Downloads

```python
from utils.data_sources.world_bank import WorldBankDataSource
import concurrent.futures

def download_indicator(indicator):
    wb_source = WorldBankDataSource()
    return wb_source.fetch_data([indicator])

indicators = ['NY.GDP.MKTP.KD', 'SP.POP.TOTL', 'SL.TLF.TOTL.IN']

# Download indicators in parallel
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(download_indicator, ind) for ind in indicators]
    results = [future.result() for future in concurrent.futures.as_completed(futures)]
```

### Batch Processing

```python
from utils.data_sources.world_bank import WorldBankDataSource

wb_source = WorldBankDataSource()

# Download multiple indicators in a single request
indicators = [
    'NY.GDP.MKTP.KD',
    'SP.POP.TOTL',
    'SL.TLF.TOTL.IN',
    'NE.EXP.GNFS.KD',
    'NE.IMP.GNFS.KD'
]

# More efficient than individual requests
data = wb_source.fetch_data(indicators, batch_size=5)
```
