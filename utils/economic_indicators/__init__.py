"""
Economic indicators calculation package.

This package provides functions for calculating various economic indicators
including Total Factor Productivity (TFP), tax revenue, and openness ratios.
"""

from .indicators_calculator import calculate_economic_indicators
from .tfp_calculator import calculate_tfp

__all__ = ["calculate_tfp", "calculate_economic_indicators"]
