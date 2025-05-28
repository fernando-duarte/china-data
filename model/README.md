# China Growth Model Implementation

This package contains the implementation of the China open-economy growth model equations as described in `china_growth_model.md`.

## Overview

The China Growth Model is an open-economy growth model for China (1980–2025) that includes:

- Production function with capital, labor, and human capital
- Capital accumulation with depreciation
- TFP growth with spillover effects from trade openness and FDI
- Export and import equations with exchange rate and income elasticities
- Consumption and investment from saving identities

## Package Structure

```text
model/
├── __init__.py                    # Package initialization
├── china_growth_model.md          # Complete model specification
├── parameters_info/               # Parameter documentation and research
│   ├── tfp.md                    # TFP parameter documentation
│   ├── tfp.pdf                   # TFP parameter research
│   ├── trade_elasticities.md     # Trade elasticity documentation
│   └── trade_elasticities.pdf    # Trade elasticity research
├── utils/                         # Core calculation utilities
│   ├── __init__.py               # Utils initialization
│   ├── exports.py                # Export equation implementation
│   ├── imports.py                # Import equation implementation
│   ├── tfp_growth.py             # TFP growth with spillovers
│   ├── consumption.py            # Consumption equation
│   └── investment_from_saving.py # Investment from saving identity
├── test_model_equations.py       # Test script for all equations
├── README.md                     # This file
└── IMPLEMENTATION_SUMMARY.md     # Implementation summary
```

## Implemented Equations

### 1. Export Equation (`exports.py`)

```text
X_t = X_0 * (e_t/e_0)^ε_x * (Y*_t/Y*_0)^μ_x
```

**Parameters:**

- `X_0`: Initial exports (base period)
- `e_t`, `e_0`: Current and initial exchange rates (CNY per USD)
- `Y*_t`, `Y*_0`: Current and initial foreign income
- `ε_x`: Export exchange rate elasticity (default: 1.5)
- `μ_x`: Export income elasticity (default: 1.5)

### 2. Import Equation (`imports.py`)

```text
M_t = M_0 * (e_t/e_0)^ε_m * (Y_t/Y_0)^μ_m
```

**Parameters:**

- `M_0`: Initial imports (base period)
- `e_t`, `e_0`: Current and initial exchange rates (CNY per USD)
- `Y_t`, `Y_0`: Current and initial domestic income (GDP)
- `ε_m`: Import exchange rate elasticity (default: -1.2, typically negative)
- `μ_m`: Import income elasticity (default: 1.1)

### 3. TFP Growth with Spillovers (`tfp_growth.py`)

```text
A_{t+1} = A_t * (1 + g + θ * openness_t + φ * fdi_ratio_t)
```

**Parameters:**

- `A_t`: Current TFP
- `g`: Baseline TFP growth rate (default: 0.02)
- `θ`: Openness contribution to TFP growth (default: 0.10)
- `φ`: FDI contribution to TFP growth (default: 0.08)
- `openness_t`: Trade openness ratio ((X+M)/Y)
- `fdi_ratio_t`: FDI inflows as ratio of GDP

### 4. Consumption (`consumption.py`)

```text
C_t = (1 - s_t) * Y_t - G_t
```

**Parameters:**

- `s_t`: Saving rate (player controlled, 0-1)
- `Y_t`: GDP
- `G_t`: Government spending

### 5. Investment from Saving (`investment_from_saving.py`)

```text
I_t = s_t * Y_t - NX_t
```

**Parameters:**

- `s_t`: Saving rate (player controlled, 0-1)
- `Y_t`: GDP
- `NX_t`: Net exports (X_t - M_t)

## Usage Examples

### Basic Usage

```python
from model.utils.exports import calculate_exports
from model.utils.imports import calculate_imports

# Calculate exports
exports = calculate_exports(
    exchange_rate=8.0,
    foreign_income=1200.0,
    x_0=19.41,
    e_0=1.5,
    y_star_0=1000.0
)

# Calculate imports
imports = calculate_imports(
    exchange_rate=8.0,
    domestic_income=500.0,
    m_0=21.84,
    e_0=1.5,
    y_0=300.0
)
```

### DataFrame Usage

```python
import pandas as pd
from model.utils.exports import calculate_exports_dataframe

df = pd.DataFrame({
    'exchange_rate': [1.5, 3.2, 4.8],
    'Y_star': [1000.0, 1159.27, 1343.92]
})

df = calculate_exports_dataframe(
    df,
    x_0=19.41,
    e_0=1.5,
    y_star_0=1000.0
)
```

## Testing

Run the test script to verify all equations work correctly:

```bash
python model/test_model_equations.py
```

## Model Parameters

Default parameter values from `china_growth_model.md`:

| Parameter | Description                         | Default Value |
| --------- | ----------------------------------- | ------------- |
| α         | Capital share in production         | 0.30          |
| δ         | Depreciation rate                   | 0.10          |
| g         | Baseline TFP growth rate            | 0.02          |
| θ         | Openness contribution to TFP growth | 0.10          |
| φ         | FDI contribution to TFP growth      | 0.08          |
| ε_x       | Export exchange rate elasticity     | 1.5           |
| ε_m       | Import exchange rate elasticity     | -1.2          |
| μ_x       | Export income elasticity            | 1.5           |
| μ_m       | Import income elasticity            | 1.1           |

## Notes

- All functions handle both scalar and pandas Series inputs
- Input validation and error handling are included
- Negative values are handled appropriately (clipped or warned)
- Logging is implemented for debugging and monitoring
- Functions include comprehensive docstrings with examples
