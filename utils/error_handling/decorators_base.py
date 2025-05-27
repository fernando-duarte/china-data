"""Base utilities for error handling decorators."""

from collections.abc import Callable
from typing import Any, TypeVar
import logging

try:
    from utils.logging_config import get_logger

    logger = get_logger(__name__)
except ImportError:  # pragma: no cover - fallback for environments without utils
    logger = logging.getLogger(__name__)

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])

from .exceptions import ChinaDataError

__all__ = ["logger", "T", "F", "ChinaDataError"]
