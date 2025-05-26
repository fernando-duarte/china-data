"""Capital stock calculation and projection utilities.

This package provides functions for calculating and projecting
capital stock data for economic analysis.
"""

from utils.capital.calculation import calculate_capital_stock
from utils.capital.investment import calculate_investment
from utils.capital.projection import project_capital_stock

__all__ = [
    "calculate_capital_stock",
    "calculate_investment",
    "project_capital_stock",
]
