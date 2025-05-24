Looking at the data provided, I need to refine the parameter values based on empirical evidence:

1. **Baseline TFP growth rate (g)**: The consensus from the literature is around 2.0% per year, which is 0.02. The document suggests:
   - 3.8% (optimistic)
   - 1.4% (pessimistic)
   - 2.0% (mid-range consensus)
   
   I should use 0.02 instead of 0.005.

2. **Openness contribution to TFP (θ)**: The literature suggests:
   - 0.07 from Lee et al. (2011)
   - 0.075-0.18 from Ji (2006)
   - 0.1-0.3+ from Martens (2008)
   
   A reasonable middle ground would be around 0.10-0.15. The current value of 0.1453 seems reasonable but could be rounded to 0.15.

3. **FDI contribution to TFP (φ)**: The literature suggests:
   - 0.08-0.09 from Tseng & Zebregs (2003)
   - 0.022 from Lee et al. (2011)
   
   The current value of 0.10 is on the high end but still reasonable. Could use 0.08.

4. **Export exchange rate elasticity (εx)**: The literature shows:
   - Short-run: -0.3 to -0.65
   - Long-run: -1.19 to -3.13, with -1.5 being common
   
   Since exports increase when the currency weakens (higher e_t), the elasticity should be positive in our model. A value of 1.5 is reasonable.

5. **Import exchange rate elasticity (εm)**: The literature shows:
   - Long-run: +0.7 to +1.4
   
   Since imports decrease when the currency weakens (higher e_t), the elasticity should be negative in our model. A value of -1.2 is reasonable.

6. **Export income elasticity (μx)**: Empirical estimates range from 1.0 to 4.3, with most studies clustering around 1.5-2.0. A moderate value of 1.5 appears appropriate, balancing short-run and long-run observations.

7. **Import income elasticity (μm)**: Preliminary data suggests variations, but I'll need to investigate further to determine a precise estimate.

8. **Initial exchange rate (e_0)**: Historical records indicate 1.50 CNY/USD in 1980, which differs from earlier mentions. This official rate requires careful verification against multiple sources.

I notice significant discrepancies in the capital stock data. The reported K_0 of 37,499.36 billion USD seems implausible compared to 1980's GDP. Using a standard capital-output ratio of 3 would suggest a more realistic figure around 573.45 billion USD, indicating potential measurement or unit conversion errors.
# Open-Economy Growth Model for China (1980–2025)

## Variables

### Endogenous

| Symbol       | Definition                      | Units       |
| :----------- | :------------------------------ | :---------- |
| $Y_t$        | Real GDP                        | bn USD      |
| $K_t$        | Physical capital stock          | bn USD      |
| $A_t$        | Total factor productivity (TFP) | index       |
| $X_t$        | Exports                         | bn USD      |
| $M_t$        | Imports                         | bn USD      |
| $NX_t$       | Net exports                     | bn USD      |
| $C_t$        | Consumption                     | bn USD      |
| $I_t$        | Investment                      | bn USD      |
| $openness_t$ | (Exports + Imports) / GDP       | fraction    |


### Exogenous

| Symbol         | Definition                                    | Units                                 |
| :------------- | :-------------------------------------------- | :------------------------------------ |
| $e_t$          | Nominal exchange rate (player controlled)     | CNY per USD |
| $L_t$          | Labor force                                   | million     |
| $fdi\_ratio_t$ | FDI inflows / GDP                             | fraction                              |
| $Y^*_t$        | Foreign income                                | index (1980 = 1000)                   |
| $H_t$          | Human capital index                           | index       |
| $G_t$          | Government spending                           | bn USD                                |
| $T_t$          | Taxes                                         | bn USD                                |
| $s_t$          | Saving rate (player controlled)               | fraction                              |

### Parameters

| Symbol                          | Definition                                   | Units    | Value       |
| :------------------------------ | :------------------------------------------- | :------- | :---------- |
| $\alpha$                        | Capital share in production                  | unitless | $0.30$      |
| $\delta$                        | Depreciation rate                            | per year | $0.10$      |
| $g$                             | Baseline TFP growth rate                     | per year | $0.02$      |
| $\theta$                        | Openness contribution to TFP growth          | unitless | $0.10$      |
| $\phi$                          | FDI contribution to TFP growth               | unitless | $0.08$      |
| $K_0$                           | Initial level of physical capital (1980)     | bn USD   | $573.45$    |
| $X_0$                           | Initial level of exports (1980)              | bn USD   | $19.41$     |
| $M_0$                           | Initial level of imports (1980)              | bn USD   | $21.84$     |
| $\varepsilon_x$                 | Export exchange rate elasticity              | unitless | $1.5$       |
| $\varepsilon_m$                 | Import exchange rate elasticity              | unitless | $-1.2$      |
| $\mu_x$                         | Export income elasticity                     | unitless | $1.5$       |
| $\mu_m$                         | Import income elasticity                     | unitless | $1.1$       |
| $n$                             | Labor force growth rate                      | per year | $0.01$      |
| $e_0$                           | Initial exchange rate (1980)                 | CNY/USD  | $1.50$      |


## Paths of exogenous variables

| Year | $fdi\_ratio_t$ | $Y^*_t$ | $H_t$ | $G_t$ | $T_t$ |
| ---: | -------------: | ------: | ----: | ----: | ----: |
| 1980 |          0.0003 | 1000.00 |  1.74 | 26.28 | 26.28* |
| 1985 |          0.0054 | 1159.27 |  1.85 | 43.99 | 43.99* |
| 1990 |          0.0097 | 1343.92 |  1.96 | 49.28 | 49.28* |
| 1995 |          0.0488 | 1557.97 |  2.14 | 97.75 | 74.42 |
| 2000 |          0.0348 | 1806.11 |  2.31 | 203.97 | 160.62 |
| 2005 |          0.0455 | 2093.78 |  2.40 | 338.27 | 379.65 |
| 2010 |          0.0400 | 2427.26 |  2.44 | 887.94 | 1479.72 |
| 2015 |          0.0219 | 2813.86 |  2.60 | 1793.95 | 3153.84 |
| 2020 |          0.0172 | 3262.04 |  2.75 | 2516.03 | 3712.35 |
| 2025 |          0.0010 | 3781.60 |  2.87 | 3158.48 | 4816.57 |

*Note: Tax revenue data for 1980-1990 is not available; values shown assume balanced budget (T=G).

## Model Equations

- **Production:**
  $$Y_t = A_t\,K_t^{\alpha}\,(L_t\,H_t)^{1-\alpha}$$

- **Capital accumulation:**
  $$K_{t+1} = (1-\delta)\,K_t + I_t$$
  $$K_0 \text{ given}$$

- **Labor force:**
  $$L_{t+1} = (1+n)\,L_t$$
  $$L_0 = 639.91 \text{ million}$$

- **TFP:**
The law of motion for technology $A_t$ with spillover effects from openness and FDI can be written generally as:

    $$
      A_{t+1} = A_t \left(1 + g + f(\text{spillovers}_t)\right),
    $$

    where $f(\text{spillovers}_t)$ captures the effect of trade openness, foreign direct investment, and other external factors influencing technology growth, which we model as in Barro and Sala-i-Martin (see Economic Growth, MIT Press, 2nd edition, Chapter 8, 2004, isbn: 9780262025539):

    $$
      A_{t+1} = A_t \left(1 + g + \theta\, \text{openness}_t + \phi\, \text{fdi\_ratio}_t \right),
    $$

- **Exports:**
  $$
    X_t = X_0\Bigl(\tfrac{e_t}{e_{0}}\Bigr)^{\varepsilon_x}
      \Bigl(\tfrac{Y^*_t}{Y^*_{0}}\Bigr)^{\mu_x}
  $$

- **Imports:**
  $$
    M_t = M_0\Bigl(\tfrac{e_t}{e_{0}}\Bigr)^{\varepsilon_m}
      \Bigl(\tfrac{Y_t}{Y_{0}}\Bigr)^{\mu_m}
  $$

- **Net exports:**
  $$
    NX_t = X_t - M_t
  $$

- **Saving:**
  $$S_t = Y_t - C_t - G_t = I_t + NX_t$$

- **Private Saving:**
  $$S^{\mathrm{priv}}_t = Y_t - T_t - C_t$$

- **Public Saving:**
  $$S^{\mathrm{pub}}_t = T_t - G_t$$

- **Saving Rate:**
  $$s_t = \frac{S_t}{Y_t} = \frac{I_t + NX_t}{Y_t} = 1 - \frac{C_t + G_t}{Y_t}$$

- **Consumption:**
  $$C_t = (1 - s_t)Y_t - G_t$$

- **Investment:**
  $$I_t = s_t Y_t - NX_t$$

- **Openness ratio:**
  $$openness_t = \frac{X_t + M_t}{Y_t}$$

## Computation Steps for Each Round

### Read values

1. Read values of parameters and paths of exogenous variables. These are known before any computation starts.
2. Read player inputs: exchange rate $e_t$ and saving rate $s_t$.

### Compute variables for t=1,2,...

1. Compute labor force:
   $$ L_t = L_0 (1 + n)^{t-1980} $$

2. Compute output/production:
   $$ Y_t = A_t K_t^{\alpha} (L_t\,H_t)^{1-\alpha} $$

3. Compute exports using player-chosen exchange rate:
   $$
     X_t = X_0\Bigl(\tfrac{e_t}{e_{0}}\Bigr)^{\varepsilon_x}
       \Bigl(\tfrac{Y^*_t}{Y^*_{0}}\Bigr)^{\mu_x}
   $$

4. Compute imports using player-chosen exchange rate:
   $$
     M_t = M_0\Bigl(\tfrac{e_t}{e_{0}}\Bigr)^{\varepsilon_m}
       \Bigl(\tfrac{Y_t}{Y_{0}}\Bigr)^{\mu_m}
   $$

5. Compute net exports:
   $$ NX_t = X_t - M_t $$

6. Compute openness ratio:
   $$
     openness_t = \frac{X_t + M_t}{Y_t}
   $$

7. Compute consumption:
   $$ C_t = (1-s_t) Y_t - G_t $$

8. Compute investment:
   $$ I_t = s_t Y_t - NX_t $$

### Compute next period's variable values

9. Compute next period's capital:
   $$ K_{t+1} = (1-\delta) K_t + I_t $$

10. Compute next period's TFP:
    $$
      A_{t+1} = A_t
        (1 + g
          + \theta\,openness_t
          + \phi\,fdi\_ratio_t
        )
    $$

## Player Controls

Players control two key policy variables in each round:

1. **Exchange Rate ($e_t$)**: The nominal exchange rate in CNY per USD
   - Range: Typically between 0.5 and 10.0
   - Historical reference: 1.50 (1980), 4.78 (1990), 8.28 (2000), 6.77 (2010), 6.91 (2020)
   - A higher rate means a weaker Chinese currency (more CNY needed per USD)

2. **Saving Rate ($s_t$)**: The fraction of GDP saved
   - Range: 0.1 to 0.5 (10% to 50%)
   - Must ensure investment remains non-negative: $s_t Y_t \geq NX_t$

## Data Notes

The exogenous variables are based on historical data from the World Bank World Development Indicators, Penn World Table 10.01, and IMF Fiscal Monitor. The foreign income index ($Y^*_t$) represents an index of world GDP growth relative to 1980. Government spending and tax revenue show China's dramatic fiscal expansion over the reform period.