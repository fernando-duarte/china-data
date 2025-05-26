"""Extrapolation methods for time series data in the China Economic Data project.

This package contains various methods for extrapolating time series data:
- ARIMA (Auto-Regressive Integrated Moving Average)
- Linear Regression
- Average Growth Rate

Each method is implemented in its own module and can be imported separately.
"""

from utils.extrapolation_methods.arima import extrapolate_with_arima
from utils.extrapolation_methods.average_growth_rate import extrapolate_with_average_growth_rate
from utils.extrapolation_methods.linear_regression import extrapolate_with_linear_regression

__all__ = ["extrapolate_with_arima", "extrapolate_with_average_growth_rate", "extrapolate_with_linear_regression"]
