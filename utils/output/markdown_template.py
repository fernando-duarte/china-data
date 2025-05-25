MARKDOWN_TEMPLATE = """
# Processed China Economic Data

|{% for h in headers %} {{ h }} |{% endfor %}
|{% for h in headers %}---|{% endfor %}
{% for row in rows %}|{% for cell in row %} {{ cell }} |{% endfor %}
{% endfor %}

# Notes on Computation

## Data Sources
The raw data in `{{ input_file }}` comes from the following sources:

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
  $GDP_{2017} \\times$ {{ capital_output_ratio }} (capital-output ratio)
- $pl\\_gdpo_t$ is the price level of GDP in year $t$ (from PWT)
- $pl\\_gdpo_{2017}$ is the price level of GDP in 2017 (from PWT)

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
- $\\alpha$ = {{ alpha }} (capital share parameter)

## Extrapolation to {{ end_year }}
Each series was extrapolated using the following methods:

### ARIMA(1,1,1) model
{% for var in extrapolation_methods['ARIMA(1,1,1)'] %}
- {{ var }}{% endfor %}

### Average growth rate of historical data
{% for var in extrapolation_methods['Average growth rate'] %}
- {{ var }}{% endfor %}

### Linear regression
{% for var in extrapolation_methods['Linear regression'] %}
- {{ var }}{% endfor %}

{% if extrapolation_methods['IMF projections'] %}
### IMF projections
{% for var in extrapolation_methods['IMF projections'] %}
- {{ var }}: Projected using official IMF Fiscal Monitor projections{% endfor %}
{% endif %}

{% if extrapolation_methods['Investment-based projection'] %}
### Investment-based projection
{% for var in extrapolation_methods['Investment-based projection'] %}
- {{ var }}: Projected using the formula $K_t = K_{t-1} \\times (1-\\delta) + I_t$, where $\\delta = 0.05$
  (5% depreciation rate) and $I_t$ is investment in year $t${% endfor %}
{% endif %}

{% if extrapolation_methods['Extrapolated'] %}
### Other methods
{% for var in extrapolation_methods['Extrapolated'] %}
- {{ var }}{% endfor %}
{% endif %}

Data processed with alpha={{ alpha }}, K/Y= {{ capital_output_ratio }}, source file={{ input_file }},
end year={{ end_year }}. Generated {{ today }}."""
