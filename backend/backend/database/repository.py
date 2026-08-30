"""
Data-access layer.

Every Supabase query the backend needs lives here, behind a small
Repository interface. `api/` and `services/` never touch the Supabase
client directly — they call `get_repository()` and use these methods.

Two implementations exist:
  - SupabaseRepository: talks to a real Supabase Postgres project.
  - InMemoryRepository (in backend/database/in_memory.py): a
    dependency-free stand-in used for local development and automated
    tests when no Supabase project is configured (USE_IN_MEMORY_DB=true).

Column names below are copied verbatim from the schema in the project
spec. Nothing is renamed.

NOTE on `claims`: the schema documented in the spec lists `users`,
`items`, and `matches` only. A `claims` table is required to satisfy the
mandated `POST /claims` endpoint but is not yet part of the documented
schema. A minimal table is assumed here:

    claims (
        id            uuid primary key,
        lost_item_id  uuid references items(id),
        found_item_id uuid references items(id),
        claimant_id   uuid references users(id),
        message       text,
        status        text default 'pending',
        created_at    timestamptz default now()
    )

Per the "CRITICAL RULES" in the backend brief, this schema addition
should be confirmed with Person 5/6 before merging — it is flagged here
rather than silently assumed.
"""

from abc import ABC, abstractmethod
from typing import Optional

from backend.config import settings

# Columns returned to the API / listing paths. Deliberately excludes
# `embedding`: CLIP vectors are large (typically 512+ floats), so pulling
# them over the wire on every item read/list is pure waste when the
# caller is just rendering a card in the frontend — nothing in ItemOut
# even has an embedding field. Anything that needs to hand a row to the
# AI engine (i.e. only match_service) must ask for the full row instead.
ITEM_DISPLAY_COLUMNS = (
    "id, reporter_id, type, category, description, image_url, location, "
    "latitude, longitude, timestamp, status, created_at"
)
ITEM_FULL_COLUMNS = ITEM_DISPLAY_COLUMNS + ", embedding"

# Hard ceiling regardless of what a caller asks for, so one query can't
# accidentally pull an unbounded number of rows (and, transitively,
# candidates into find_matches()).
MAX_LIST_LIMIT = 500


class Repository(ABC):
    # -- users ---------------------------------------------------------
    @abstractmethod
    def get_or_create_user(self, name: str, email: str, phone: Optional[str]) -> dict: ...

    @abstractmethod
    def get_user(self, user_id: str) -> Optional[dict]: ...

    @abstractmethod
    def get_users(self, user_ids: list) -> dict:
        """Batch fetch. Returns {user_id: user_row} for whichever ids exist.

        Used instead of N calls to get_user() when joining a list of
        results (e.g. finder contact info for a page of matches) against
        the users table — one round trip instead of one per row.
        """
        ...

    # -- items -----------------------------------------------------------
    @abstractmethod
    def create_item(self, item: dict) -> dict: ...

    @abstractmethod
    def get_item(self, item_id: str, include_embedding: bool = False) -> Optional[dict]: ...

    @abstractmethod
    def list_items(
        self,
        type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        include_embedding: bool = False,
    ) -> list: ...

    @abstractmethod
    def update_item_status(self, item_id: str, status: str) -> Optional[dict]: ...

    # -- matches -----------------------------------------------------------
    @abstractmethod
    def save_matches(self, lost_item_id: str, results: list) -> list: ...

    # -- claims -----------------------------------------------------------
    @abstractmethod
    def create_claim(self, claim: dict) -> dict: ...


class SupabaseRepository(Repository):
    def __init__(self):
        from backend.database.supabase_client import get_client

        self.client = get_client()

    # -- users ---------------------------------------------------------
    def get_or_create_user(self, name: str, email: str, phone: Optional[str]) -> dict:
        existing = (
            self.client.table("users").select("*").eq("email", email).limit(1).execute()
        )
        if existing.data:
            return existing.data[0]

        created = (
            self.client.table("users")
            .insert({"name": name, "email": email, "phone": phone})
            .execute()
        )
        return created.data[0]

    def get_user(self, user_id: str) -> Optional[dict]:
        res = self.client.table("users").select("*").eq("id", user_id).limit(1).execute()
        return res.data[0] if res.data else None

    def get_users(self, user_ids: list) -> dict:
        ids = list({uid for uid in user_ids if uid})
        if not ids:
            return {}
        # Single round trip via `in_` instead of N single-row lookups.
        res = self.client.table("users").select("*").in_("id", ids).execute()
        return {row["id"]: row for row in res.data}

    # -- items -----------------------------------------------------------
    def create_item(self, item: dict) -> dict:
        res = self.client.table("items").insert(item).execute()
        return res.data[0]

    def get_item(self, item_id: str, include_embedding: bool = False) -> Optional[dict]:
        cols = ITEM_FULL_COLUMNS if include_embedding else ITEM_DISPLAY_COLUMNS
        res = self.client.table("items").select(cols).eq("id", item_id).limit(1).execute()
        return res.data[0] if res.data else None

    def list_items(
        self,
        type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        include_embedding: bool = False,
    ) -> list:
        limit = min(limit, MAX_LIST_LIMIT)
        cols = ITEM_FULL_COLUMNS if include_embedding else ITEM_DISPLAY_COLUMNS
        q = self.client.table("items").select(cols)
        if type:
            q = q.eq("type", type)
        if status:
            q = q.eq("status", status)
        res = (
            q.order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return res.data

    def update_item_status(self, item_id: str, status: str) -> Optional[dict]:
        res = (
            self.client.table("items").update({"status": status}).eq("id", item_id).execute()
        )
        return res.data[0] if res.data else None

    # -- matches -----------------------------------------------------------
    def save_matches(self, lost_item_id: str, results: list) -> list:
        rows = [
            {
                "lost_item_id": lost_item_id,
                "found_item_id": r["item_id"],
                "image_score": r["image_score"],
                "text_score": r["text_score"],
                "location_score": r["location_score"],
                "time_score": r["time_score"],
                "final_score": r["final_score"],
            }
            for r in results
        ]
        if not rows:
            return []
        res = self.client.table("matches").insert(rows).execute()
        return res.data

    # -- claims -----------------------------------------------------------
    def create_claim(self, claim: dict) -> dict:
        res = self.client.table("claims").insert(claim).execute()
        return res.data[0]


def get_repository() -> Repository:
    if settings.USE_IN_MEMORY_DB:
        from backend.database.in_memory import InMemoryRepository

        return InMemoryRepository.instance()
    return SupabaseRepository()
