"""
Thin wrapper around the Supabase Python client.

Kept in its own module so every other file imports `get_client()` rather
than constructing a client itself — makes it trivial to mock in tests.
"""

from functools import lru_cache

from backend.config import settings


@lru_cache
def get_client():
    """Returns a cached Supabase client instance.

    Raises RuntimeError with a clear message if SUPABASE_URL /
    SUPABASE_SERVICE_KEY are not configured, so misconfiguration fails
    loudly instead of silently returning None.
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set (see .env.example). "
            "For local/demo testing without a live Supabase project, set "
            "USE_IN_MEMORY_DB=true instead."
        )

    from supabase import create_client  # imported lazily so the package is
    # only required when actually talking to a real Supabase project.

    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
