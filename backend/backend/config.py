"""
Centralized configuration loaded from environment variables.

See .env.example at the repo root for the full list of variables.
"""

import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # python-dotenv is optional; in prod, env vars are usually injected
    # by the platform (Render, Railway, Docker, etc.) directly.
    pass


class Settings:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    SUPABASE_STORAGE_BUCKET: str = os.getenv("SUPABASE_STORAGE_BUCKET", "item-images")

    # Max number of active found/lost items considered as match candidates.
    # Keeps the AI call bounded for the demo; the real system may later
    # add pre-filtering (geohash bucket, category filter, etc.) upstream
    # of find_matches() without changing the AI contract itself.
    MAX_MATCH_CANDIDATES: int = int(os.getenv("MAX_MATCH_CANDIDATES", "200"))

    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")

    ENV: str = os.getenv("ENV", "development")

    # When true, uses an in-process in-memory repository instead of a real
    # Supabase project. Intended for local development and automated tests
    # only (see backend/database/in_memory.py). Defaults to true whenever
    # Supabase credentials are absent, so the backend is runnable/testable
    # out of the box; set explicitly to "false" once real credentials are
    # provided to make sure a misconfigured env doesn't silently fall back.
    USE_IN_MEMORY_DB: bool = os.getenv(
        "USE_IN_MEMORY_DB",
        "true" if not (os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_KEY")) else "false",
    ).lower() == "true"


settings = Settings()
