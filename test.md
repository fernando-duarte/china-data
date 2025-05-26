# Processed China Economic Data

| Year | GDP      | Population |
| ---- | -------- | ---------- |
| 2020 | 14722.73 | 1411.1     |
| 2021 | 17744.64 | 1412.36    |
| 2022 | 17886.33 | 1425.89    |

# Notes on Computation

## Data Sources

The raw data in `china_data_raw.md` comes from the following sources:

- **World Bank World Development Indicators (WDI)** for GDP components, FDI, population, and labor force
- **Penn World Table (PWT) version 10.01** for human capital index and capital stock related variables
- **International Monetary Fund (IMF) Fiscal Monitor** for tax revenue data

This processed dataset was created by applying the following transformations to the raw data:

## Unit Conversions

- GDP and its components (Consumption, Government, Investment, Exports, Imports) were converted from USD to billions USD
- Population and Labor Force were converted from people to millions of people

## Derived Variables

### Net Exports

Calculated as Exports - Imports (in billions USD)

```
Net Exports = Exports - Imports
```

### Physical Capital

Calculated using PWT data with the following formula:

```
K_t = (rkna_t / rkna_2017) × K_2017 × (pl_gdpo_t / pl_gdpo_2017)
```

Where:

- $K_t$ is the capital stock in year $t$ (billions USD)
- $rkna_t$ is the real capital stock index in year $t$ (from PWT)
- $rkna_{2017}$ is the real capital stock index in 2017 (from PWT)
- $K_{2017}$ is the nominal capital stock in 2017, estimated as
  $GDP_{2017} \times$ 3.0 (capital-output ratio)
- $pl\_gdpo_t$ is the price level of GDP in year $t$ (from PWT)
- $pl\_gdpo_{2017}$ is the price level of GDP in 2017 (from PWT)

### TFP (Total Factor Productivity)

Calculated using the Cobb-Douglas production function:

```
TFP_t = Y_t / (K_t^α × (L_t × H_t)^(1-α))
```

Where:

- $Y_t$ is GDP in year $t$ (billions USD)
- $K_t$ is Physical Capital in year $t$ (billions USD)
- $L_t$ is Labor Force in year $t$ (millions of people)
- $H_t$ is Human Capital index in year $t$
- $\alpha$ = 0.3333333333333333 (capital share parameter)

## Extrapolation to 2025

Each series was extrapolated using the following methods:

### ARIMA(1,1,1) model

- GDP (2023-2025)

### Average growth rate of historical data

### Linear regression

Data processed with alpha=0.3333333333333333, K/Y= 3.0, source file=china_data_raw.md,
end year=2025. Generated 2025-05-26.
