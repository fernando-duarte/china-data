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

| Symbol                          | Definition                                   | Units    | Value       | Lower Bound | Upper Bound |
| :------------------------------ | :------------------------------------------- | :------- | :---------- | :---------- | :---------- |
| $\alpha$                        | Capital share in production                  | unitless | $0.30$      | 0           | 1           |
| $\delta$                        | Depreciation rate                            | per year | $0.10$      | 0           | 1           |
| $g$                             | Baseline TFP growth rate                     | per year | $0.02$      | -1          | 1           |
| $\theta$                        | Openness contribution to TFP growth          | unitless | $0.10$      | 0           | 1           |
| $\phi$                          | FDI contribution to TFP growth               | unitless | $0.08$      | 0           | 1           |
| $K_0$                           | Initial level of physical capital (1980)     | bn USD   | $337.49$    | 0           | infinity    |
| $X_0$                           | Initial level of exports (1980)              | bn USD   | $19.41$     | 0           | infinity    |
| $M_0$                           | Initial level of imports (1980)              | bn USD   | $21.84$     | 0           | infinity    |
| $\varepsilon_x$                 | Export exchange rate elasticity              | unitless | $1.5$       | 0           | infinity    |
| $\varepsilon_m$                 | Import exchange rate elasticity              | unitless | $-1.2$      | -infinity   | 0           |
| $\mu_x$                         | Export income elasticity                     | unitless | $1.5$       | 0           | infinity    |
| $\mu_m$                         | Import income elasticity                     | unitless | $1.1$       | 0           | infinity    |


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
  $$L_t \text{ is exogenous (read from data)}$$

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

### Compute variables for t=1,2,...

1. Compute output/production:
   $$ Y_t = A_t K_t^{\alpha} (L_t\,H_t)^{1-\alpha} $$

2. Compute exports:
   $$
     X_t = X_0\Bigl(\tfrac{e_t}{e_{0}}\Bigr)^{\varepsilon_x}
       \Bigl(\tfrac{Y^*_t}{Y^*_{0}}\Bigr)^{\mu_x}
   $$

3. Compute imports:
   $$
     M_t = M_0\Bigl(\tfrac{e_t}{e_{0}}\Bigr)^{\varepsilon_m}
       \Bigl(\tfrac{Y_t}{Y_{0}}\Bigr)^{\mu_m}
   $$

4. Compute net exports:
   $$ NX_t = X_t - M_t $$

5. Compute openness ratio:
   $$
     openness_t = \frac{X_t + M_t}{Y_t}
   $$

6. Compute consumption:
   $$ C_t = (1-s_t) Y_t - G_t $$

7. Compute investment:
   $$ I_t = s_t Y_t - NX_t $$

### Compute next period's variable values

8. Compute next period's capital:
   $$ K_{t+1} = (1-\delta) K_t + I_t $$

9. Compute next period's TFP:
    $$
      A_{t+1} = A_t
        (1 + g
          + \theta\,openness_t
          + \phi\,fdi\_ratio_t
        )
    $$

## Data Notes

The exogenous variables are based on historical data from the World Bank World Development Indicators, Penn World Table 10.01, and IMF Fiscal Monitor. The foreign income index ($Y^*_t$) represents an index of world GDP growth relative to 1980. Government spending and tax revenue show China's dramatic fiscal expansion over the reform period.


## Alternative Calibration
alpha (Capital share in production): 0.3000
delta (Depreciation rate): 0.1001
g (Baseline TFP growth rate): 0.0000
theta (Openness contribution to TFP growth): 0.0039
phi (FDI contribution to TFP growth): 0.0001
epsilon_x (Export exchange rate elasticity): 1.5000
epsilon_m (Import exchange rate elasticity): -1.1999
mu_x (Export income elasticity): 1.4999
mu_m (Import income elasticity): 1.0999