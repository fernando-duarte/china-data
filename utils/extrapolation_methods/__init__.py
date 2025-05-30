"""Extrapolation methods for time series data in the China Economic Data project.

This package contains various methods for extrapolating time series data:
- ARIMA (Auto-Regressive Integrated Moving Average)
- Linear Regression
- Average Growth Rate

Each method is implemented in its own module and can be imported separately.
"""

from .arima import extrapolate_with_arima
from .average_growth_rate import (
    AvgGrowthRateConfig,
    extrapolate_with_average_growth_rate,
)
from .linear_regression import extrapolate_with_linear_regression

__all__ = [
    "AvgGrowthRateConfig",
    "extrapolate_with_arima",
    "extrapolate_with_average_growth_rate",
    "extrapolate_with_linear_regression",
]
