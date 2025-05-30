"""Utilities for caching downloaded data."""

from datetime import timedelta

from requests_cache import CachedSession

from config import Config


def get_cached_session() -> CachedSession:  # type: ignore[no-any-unimported]
    """Creates and returns a cached requests session."""
    cache_name_val: str = Config.CACHE_NAME
    cache_backend_val: str = Config.CACHE_BACKEND
    expire_days_val: int = Config.CACHE_EXPIRE_AFTER_DAYS

    return CachedSession(
        cache_name_val,
        backend=cache_backend_val,
        expire_after=timedelta(days=expire_days_val),
        allowable_methods=["GET", "POST"],  # Allow caching for POST if needed by sources
    )
