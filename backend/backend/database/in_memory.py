"""
In-memory stand-in for SupabaseRepository.

Used automatically (see backend/config.py: USE_IN_MEMORY_DB) when no
Supabase credentials are configured, so that:

  - `backend/` can be run and manually tested with zero external setup.
  - `tests/` can run in CI without needing a live Supabase project.

Data does NOT persist across process restarts. This is a development
convenience only and must never be used in the actual SIH demo deployment
against real data — swap in SupabaseRepository (the default once
SUPABASE_URL / SUPABASE_SERVICE_KEY are set) for that.

Implements the exact same column shapes as the real tables so that
switching between the two repositories is invisible to services/api code.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional


def _new_id() -> str:
    return str(uuid.uuid4())


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class InMemoryRepository:
    _singleton: Optional["InMemoryRepository"] = None

    def __init__(self):
        self.users = {}
        self.items = {}
        self.matches = {}
        self.claims = {}

    @classmethod
    def instance(cls) -> "InMemoryRepository":
        # A process-wide singleton so all requests within one running
        # backend instance share the same in-memory dataset.
        if cls._singleton is None:
            cls._singleton = cls()
        return cls._singleton

    @classmethod
    def reset(cls):
        """Clears all data. Handy between test cases."""
        cls._singleton = cls()

    # -- users ---------------------------------------------------------
    def get_or_create_user(self, name: str, email: str, phone: Optional[str]) -> dict:
        for u in self.users.values():
            if u["email"] == email:
                return u
        user = {
            "id": _new_id(),
            "name": name,
            "email": email,
            "phone": phone,
            "created_at": _now(),
        }
        self.users[user["id"]] = user
        return user

    def get_user(self, user_id: str) -> Optional[dict]:
        return self.users.get(user_id)

    def get_users(self, user_ids: list) -> dict:
        ids = {uid for uid in user_ids if uid}
        return {uid: self.users[uid] for uid in ids if uid in self.users}

    # -- items -----------------------------------------------------------
    def create_item(self, item: dict) -> dict:
        row = dict(item)
        row["id"] = row.get("id") or _new_id()
        row["created_at"] = _now()
        row.setdefault("status", "active")
        self.items[row["id"]] = row
        return row

    @staticmethod
    def _strip_embedding(row: dict) -> dict:
        # Mirrors SupabaseRepository's column-scoping so callers see
        # identical shapes regardless of which repository is active.
        return {k: v for k, v in row.items() if k != "embedding"}

    def get_item(self, item_id: str, include_embedding: bool = False) -> Optional[dict]:
        row = self.items.get(item_id)
        if row is None:
            return None
        return row if include_embedding else self._strip_embedding(row)

    def list_items(
        self,
        type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        include_embedding: bool = False,
    ) -> list:
        rows = list(self.items.values())
        if type:
            rows = [r for r in rows if r.get("type") == type]
        if status:
            rows = [r for r in rows if r.get("status") == status]
        rows.sort(key=lambda r: r.get("created_at", ""), reverse=True)
        page = rows[offset : offset + limit]
        return page if include_embedding else [self._strip_embedding(r) for r in page]

    def update_item_status(self, item_id: str, status: str) -> Optional[dict]:
        item = self.items.get(item_id)
        if not item:
            return None
        item["status"] = status
        return item

    # -- matches -----------------------------------------------------------
    def save_matches(self, lost_item_id: str, results: list) -> list:
        rows = []
        for r in results:
            row = {
                "id": _new_id(),
                "lost_item_id": lost_item_id,
                "found_item_id": r["item_id"],
                "image_score": r["image_score"],
                "text_score": r["text_score"],
                "location_score": r["location_score"],
                "time_score": r["time_score"],
                "final_score": r["final_score"],
                "created_at": _now(),
            }
            self.matches[row["id"]] = row
            rows.append(row)
        return rows

    # -- claims -----------------------------------------------------------
    def create_claim(self, claim: dict) -> dict:
        row = dict(claim)
        row["id"] = row.get("id") or _new_id()
        row["created_at"] = _now()
        row.setdefault("status", "pending")
        self.claims[row["id"]] = row
        return row
