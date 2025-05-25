import requests_cache
from datetime import timedelta
from config import Config

def get_cached_session() -> requests_cache.CachedSession:
    """Creates and returns a cached requests session."""
    session = requests_cache.CachedSession(
        Config.CACHE_NAME,
        backend=Config.CACHE_BACKEND,
        expire_after=timedelta(days=Config.CACHE_EXPIRE_AFTER_DAYS),
        allowable_methods=['GET', 'POST'] # Allow caching for POST if needed by sources
    )
    return session 