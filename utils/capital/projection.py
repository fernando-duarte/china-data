"""Capital stock projection module wrapper.

This module re-exports the :func:`project_capital_stock` function from
``projection_core`` for backwards compatibility.
"""

from .projection_core import project_capital_stock

__all__ = ["project_capital_stock"]
