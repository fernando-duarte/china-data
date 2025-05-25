"""
Output processing utilities for China data processor.

This package provides functionality for formatting data and generating 
various output formats (markdown, CSV, etc.).
"""

from .formatters import format_data_for_output
from .markdown_generator import create_markdown_table

__all__ = ["format_data_for_output", "create_markdown_table"]
