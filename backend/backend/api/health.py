from fastapi import APIRouter

from backend.config import settings
from backend.models.schemas import HealthOut

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthOut)
def health():
    try:
        import ai  # noqa: F401

        ai_engine = "reachable"
    except Exception as exc:  # pragma: no cover
        ai_engine = f"unreachable: {exc}"

    database = "in-memory (dev)" if settings.USE_IN_MEMORY_DB else "supabase"

    return HealthOut(status="ok", ai_engine=ai_engine, database=database)
