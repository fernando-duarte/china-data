---
header-includes:
  - \usepackage[utf8]{inputenc}
  - \usepackage[T1]{fontenc}
  - \usepackage[margin=1in]{geometry}
  - \usepackage{pdflscape}
  - \usepackage{tabularx}
  - \usepackage{makecell}
  - \usepackage{xcolor}
  - \usepackage[colorlinks=true,
    linkcolor=blue,
    urlcolor=blue,
    citecolor=blue,
    filecolor=blue
    ]{hyperref}
---

# Parameter Estimates for China's TFP Growth Model

## Baseline Exogenous TFP Growth Rate ($g$) – China (1978–present)

```{=latex}
\begin{landscape}
\begin{table}[ht]
\centering
\caption{Baseline Exogenous TFP Growth Rate ($g$)}
\begin{tabularx}{\linewidth}{>{\raggedright\arraybackslash}p{3cm} >{\raggedright\arraybackslash}p{3cm} X X X}
\hline
Estimate & Source & Methodology & Pros & Cons \\
\hline
\makecell[l]{\textasciitilde3.8\% \\ (optimistic)} & Perkins \& Rawski (2008) & Official growth accounting & Comprehensive national coverage & May overestimate; no isolation of spillovers \\
\makecell[l]{\textasciitilde1.4\% \\ (pessimistic)} & Young (2003) & Adjusted growth accounting & Rigorous bias adjustments & Excludes agriculture; early period only \\
\makecell[l]{\textasciitilde2.0\% \\ (mid-range)} & Tian \& Yu (2012) & Meta-analysis & Consensus view; $\sim$20\% GDP via TFP & Hides variance; no time detail \\
\hline
\end{tabularx}
\end{table}
\end{landscape}
```

## Sensitivity of TFP to Trade Openness ($\theta$)

```{=latex}
\begin{landscape}
\begin{table}[ht]
\centering
\caption{Sensitivity of TFP to Trade Openness ($\theta$)}
\begin{tabularx}{\linewidth}{>{\raggedright\arraybackslash}p{3cm} >{\raggedright\arraybackslash}p{3cm} X X X}
\hline
Estimate ($\theta$) & Source & Methodology & Pros & Cons \\
\hline
\makecell[l]{0.07} & Lee et al. (2011) & Panel regression & Quantifies effect (10\% import $\rightarrow$ +0.7 pp TFP) & Modest effect; correlation only \\
0.075--0.18 & Ji (2006) & Provincial panel & Captures tech spillovers & Pre-WTO data; proxies; collinearity \\
0.1--0.3+ & Martens (2008) & Cross-country survey & Broad context; many studies & Wide range; not China-specific \\
\hline
\end{tabularx}
\end{table}
\end{landscape}
```

## Sensitivity of TFP to FDI Inflows ($\phi$)

```{=latex}
\begin{landscape}
\begin{table}[ht]
\centering
\caption{Sensitivity of TFP to FDI Inflows ($\phi$)}
\begin{tabularx}{\linewidth}{>{\raggedright\arraybackslash}p{3cm} >{\raggedright\arraybackslash}p{3cm} X X X}
\hline
Estimate ($\phi$) & Source & Methodology & Pros & Cons \\
\hline
0.08--0.09 & Tseng \& Zebregs (2003) & Cointegration analysis & Long-run elasticity & Early data; may not hold later \\
0.022 & Lee et al. (2011) & Panel regression & Broad empirical & Small magnitude; capital effects \\
Mixed & Hong \& Sun (2011); Liu (2008) & Micro panel & Micro spillovers & Mixed results; absorptive variation \\
\hline
\end{tabularx}
\end{table}
\end{landscape}
```

## Notes

- Baseline growth ($g$) ranges from about 1.4 % to 3.8 %, consensus roughly 2.0 %.
- Trade openness effect ($\theta$) is positive but modest.
- FDI sensitivity ($\phi$) is positive but small; micro studies vary.
- Estimates depend on period, data quality, and methodology.

## References

1. **Perkins, Dwight H., and Thomas G. Rawski. 2008.**
   "Forecasting China's Economic Growth to 2025." In _China's Great Economic Transformation_,
   edited by Loren Brandt and Thomas G. Rawski, 829–886. Cambridge University Press.
   [Full Text PDF](https://scholar.harvard.edu/files/dperkins/files/chapter20.pdf)

2. **Young, Alwyn. 2003.**
   "Gold into Base Metals: Productivity Growth in the People's Republic of China during the Reform Period."
   _Journal of Political Economy_ 111 (6): 1220–1261.
   [Full Text PDF](https://web.stanford.edu/~klenow/Gold%20into%20Base%20Metals.pdf)

3. **Tian, Xu, and Xiaohua Yu. 2012.**
   "The Enigmas of TFP in China: A Meta-Analysis." _China Economic Review_ 23 (2): 396–414.
   [Full Text PDF](https://www.econstor.eu/bitstream/10419/90512/1/CRC-PEG_DP_113.pdf)

4. **Samaké, Issouf, and Yongzheng Yang. 2011.**
   "Low-Income Countries' BRIC Linkage: Are There Growth Spillovers?" _IMF Working Paper_ WP/11/267.
   [Full Text PDF](https://www.imf.org/external/pubs/ft/wp/2011/wp11267.pdf)

5. **Tseng, Wanda, and Harm Zebregs. 2003.**
   "Foreign Direct Investment in China: Some Lessons for Other Countries." _IMF Policy Discussion Paper_
   PDP/02/3.
   [Full Text PDF](https://www.imf.org/external/pubs/ft/pdp/2002/pdp03.pdf)

6. **Hong, Eunsuk, and Laixiang Sun. 2011.**
   "Foreign Direct Investment and Total Factor Productivity in China: A Spatial Dynamic Panel Analysis."
   _Oxford Bulletin of Economics and Statistics_ 73 (6): 771–791.
   [Official Source](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1468-0084.2011.00672.x)
   _(Access may require subscription.)_

7. **Liu, Zhiqiang. 2008.**
   "Foreign Direct Investment and Technology Spillovers: Theory and Evidence." _Journal of Development
   Economics_ 85 (1–2): 176–193.
   [Full Text PDF](https://www.uh.edu/~bsorense/FDI_Tech_Spill_Over.pdf)
