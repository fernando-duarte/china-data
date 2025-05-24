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
| $e_t$        | Nominal exchange rate           | CNY per USD |
| $L_t$        | Labor force                     | million     |
| $fdi\_ratio_t$ | FDI inflows \/ GDP                            | fraction                              |
| $Y^*_t$        | Foreign income                                | index (1980 = 1000)                   |
| $H_t$          | Human capital index                           | index (2015 = Penn World Table value) |
| $G_t$          | Government spending                           | bn USD                                |
| $T_t$          | Taxes                           | bn USD                                |
| $s_t$          | Saving rate                           | fraction                                |

### Parameters

| Symbol                          | Definition                                   | Units    | Value       |
| :------------------------------ | :------------------------------------------- | :------- | :---------- |
| $\alpha$                        | Capital share in production                  | unitless | $0.30$      |
| $\delta$                        | Depreciation rate                            | per year | $0.10$      |
| $g$                             | Baseline TFP growth rate                     | per year | $0.005$     |
| $\theta$                        | Openness contribution to TFP growth          | unitless | $0.1453$    |
| $\phi$                          | FDI contribution to TFP growth               | unitless | $0.10$      |
| $K_0$                           | Initial level of physical capital (1980)     | bn USD   | $337.49$   |
| $X_0$                           | Initial level of exports (1980)              | bn USD   | $19.41$     |
| $M_0$                           | Initial level of imports (1980)              | bn USD   | $21.84$     |
| $\varepsilon_x,\ \varepsilon_m$ | Exchange‐rate elasticities (exports/imports) | unitless | $1.5,\ 1.2$ |
| $\mu_x,\ \mu_m$                 | Income elasticities (exports/imports)        | unitless | $1.0,\ 1.0$ |


## Paths of exogenous variables

| Year | $\tilde e_t$ | $fdi\_ratio_t$ | $Y^*_t$ | $H_t$ |
| ---: | -----------: | -------------: | ------: | ----: |
| 1980 |         0.78 |          0.001 | 1000.00 |  1.58 |
| 1985 |         1.53 |          0.001 | 1159.27 |  1.77 |
| 1990 |         2.48 |           0.02 | 1343.92 |  1.80 |
| 1995 |         4.34 |           0.02 | 1557.97 |  2.02 |
| 2000 |         5.23 |           0.02 | 1806.11 |  2.24 |
| 2005 |         4.75 |           0.02 | 2093.78 |  2.43 |
| 2010 |         5.61 |           0.02 | 2427.26 |  2.61 |
| 2015 |         7.27 |           0.02 | 2813.86 |  2.60 |
| 2020 |         7.00 |           0.02 | 3262.04 |  6.71 |
| 2025 |         6.41 |           0.02 | 3781.60 |  6.49 |

## Model Equations

- **Production:**
  $$Y_t = A_t\,K_t^{\alpha}\,(L_t\,H_t)^{1-\alpha}$$

- **Capital accumulation:**
  $$K_{t+1} = (1-\delta)\,K_t + I_t$$
  $$K_0 \text{ given}$$

- **Labor force:**
  $$L_{t+1} = (1+n) L_t$$

- **TFP:**
The law of motion for technology \(A_t\) with spillover effects from openness and FDI can be written generally as:

    $$
      A_{t+1} = A_t \left(1 + g + f(\text{spillovers}_t)\right),
    $$

    where $f(\text{spillovers}_t)$ captures the effect of trade openness, foreign direct investment, and other external factors influencing technology growth, which we model as in in Barro and Sala-i-Martin (see Economic Growth, MIT Press, 2nd edition, Chapter 8, 2004, isbn: 9780262025539):

    $$
      A_{t+1} = A_t \left(1 + g + \theta\, \text{openness}_t + \phi\, \text{fdi\_ratio}_t \right),
    $$

- **Exports:**
  $$
    X_t = X_0\Bigl(\tfrac{e_t}{e_{1980}}\Bigr)^{\varepsilon_x}
      \Bigl(\tfrac{Y^*_t}{Y^*_{1980}}\Bigr)^{\mu_x}
  $$

- **Imports:**
  $$
    M_t = M_0\Bigl(\tfrac{e_t}{e_{1980}}\Bigr)^{-\varepsilon_m}
      \Bigl(\tfrac{Y_t}{Y_{1980}}\Bigr)^{\mu_m}
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

### Initial Setup

1. **Read parameters:** $\alpha = 0.30$, $\delta = 0.10$, $g = 0.005$, $\theta = 0.1453$, $\phi = 0.10$, $\varepsilon_x = 1.5$, $\varepsilon_m = 1.2$, $\mu_x = 1.0$, $\mu_m = 1.0$

2. **Read initial values (t=0, year 1980):**
   - $K_0 = 337.49$ bn USD
   - $X_0 = 19.41$ bn USD  
   - $M_0 = 21.84$ bn USD
   - $A_0 = 1.0$ (normalized)
   - $L_0$ (to be specified)
   - $e_0 = 0.78$ CNY/USD
   - $Y^*_0 = 1000.00$

3. **Read paths of exogenous variables** for each year t: $L_t$, $e_t$, $fdi\_ratio_t$, $Y^*_t$, $H_t$, $G_t$, $T_t$, $s_t$

### Compute Variables for t = 0

4. **Compute initial output:**
   $$Y_0 = A_0 K_0^{\alpha} (L_0 H_0)^{1-\alpha}$$

5. **Compute initial openness ratio:**
   $$openness_0 = \frac{X_0 + M_0}{Y_0}$$

### Compute Variables for t = 1, 2, 3, ...

6. **Update TFP using previous period's openness:**
   $$A_t = A_{t-1} \left(1 + g + \theta \cdot openness_{t-1} + \phi \cdot fdi\_ratio_{t-1}\right)$$

7. **Compute output:**
   $$Y_t = A_t K_t^{\alpha} (L_t H_t)^{1-\alpha}$$

8. **Compute exports:**
   $$X_t = X_0 \left(\frac{e_t}{e_0}\right)^{\varepsilon_x} \left(\frac{Y^*_t}{Y^*_0}\right)^{\mu_x}$$

9. **Compute imports:**
   $$M_t = M_0 \left(\frac{e_t}{e_0}\right)^{-\varepsilon_m} \left(\frac{Y_t}{Y_0}\right)^{\mu_m}$$

10. **Compute net exports:**
    $$NX_t = X_t - M_t$$

11. **Compute openness ratio:**
    $$openness_t = \frac{X_t + M_t}{Y_t}$$

12. **Compute consumption:**
    $$C_t = (1 - s_t) Y_t - G_t$$

13. **Compute investment:**
    $$I_t = s_t Y_t - NX_t$$

14. **Update capital stock for next period:**
    $$K_{t+1} = (1 - \delta) K_t + I_t$$

### Notes

- Steps 6-14 are repeated for each time period
- The labor force $L_t$ is exogenous and read from data for each period
- The nominal exchange rate $e_t$ is given exogenously in the table
- All monetary values are in billions of 2015 USD


