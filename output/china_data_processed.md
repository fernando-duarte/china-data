# Processed China Economic Data

| year   | hc   | T_USD_bn | Openness_Ratio | NX_USD_bn | S_USD_bn | S_pub_USD_bn | S_priv_USD_bn | Saving_Rate |
| ------ | ---- | -------- | -------------- | --------- | -------- | ------------ | ------------- | ----------- |
| 2015.0 | 2.2  | nan      | nan            | nan       | nan      | nan          | nan           | nan         |
| 2016.0 | 2.25 | nan      | nan            | nan       | nan      | nan          | nan           | nan         |
| 2017.0 | 2.3  | nan      | nan            | nan       | nan      | nan          | nan           | nan         |
| 2018.0 | 2.35 | nan      | nan            | nan       | nan      | nan          | nan           | nan         |
| 2019.0 | 2.4  | nan      | nan            | nan       | nan      | nan          | nan           | nan         |
| 2020.0 | 2.45 | nan      | nan            | nan       | nan      | nan          | nan           | nan         |
| 2021.0 | 2.5  | nan      | nan            | nan       | nan      | nan          | nan           | nan         |
| 2022.0 | 2.55 | nan      | nan            | nan       | nan      | nan          | nan           | nan         |
| 2023.0 | 2.6  | nan      | nan            | nan       | nan      | nan          | nan           | nan         |
| 2024.0 | 2.65 | nan      | nan            | nan       | nan      | nan          | nan           | nan         |
| 2025.0 | 2.7  | nan      | nan            | nan       | nan      | nan          | nan           | nan         |

## Notes on Computation

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

```text
Net Exports = Exports - Imports
```

### Physical Capital

Calculated using PWT data with the following formula:

```text
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

```text
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

### Average growth rate of historical data

### Linear regression

- Human Capital (2023-2025)

Data processed with alpha=0.3333333333333333, K/Y= 3.0, source file=china_data_raw.md,
end year=2025. Generated 2025-05-26.
