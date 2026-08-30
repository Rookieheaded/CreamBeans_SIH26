"""
Business logic for creating/retrieving/listing items and enforcing status
transitions. No AI or HTTP concerns live here.
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status as http_status

from backend.database.repository import Repository
from backend.models.schemas import ItemCreate

VALID_TRANSITIONS = {
    "active": {"matched"},
    "matched": {"returned", "active"},  # allow reverting a false match
    "returned": set(),
}


def report_item(repo: Repository, item_type: str, payload: ItemCreate) -> dict:
    """Creates (or reuses) the reporter, then stores the item.

    item_type must be "lost" or "found" — enforced by the API route, not
    duplicated here as a param the caller could get wrong silently.
    """
    reporter = repo.get_or_create_user(
        name=payload.reporter.name,
        email=payload.reporter.email,
        phone=payload.reporter.phone,
    )

    timestamp = payload.timestamp or datetime.now(timezone.utc)

    item_row = {
        "reporter_id": reporter["id"],
        "type": item_type,
        "category": payload.category,
        "description": payload.description,
        "image_url": payload.image_url,
        "location": payload.location,
        "latitude": payload.latitude,
        "longitude": payload.longitude,
        "timestamp": timestamp.isoformat() if hasattr(timestamp, "isoformat") else timestamp,
        "status": "active",
    }
    return repo.create_item(item_row)


def get_item_or_404(repo: Repository, item_id: str, include_embedding: bool = False) -> dict:
    item = repo.get_item(item_id, include_embedding=include_embedding)
    if not item:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


def list_items(
    repo: Repository,
    type: Optional[str],
    status_: Optional[str],
    limit: int = 50,
    offset: int = 0,
) -> list:
    if type and type not in ("lost", "found"):
        raise HTTPException(status_code=400, detail="type must be 'lost' or 'found'")
    if status_ and status_ not in ("active", "matched", "returned"):
        raise HTTPException(status_code=400, detail="invalid status filter")
    if limit < 1 or offset < 0:
        raise HTTPException(status_code=400, detail="limit must be >=1 and offset >=0")
    return repo.list_items(type=type, status=status_, limit=limit, offset=offset)


def update_status(repo: Repository, item_id: str, new_status: str) -> dict:
    item = get_item_or_404(repo, item_id)
    current = item["status"]

    if new_status == current:
        return item  # no-op, idempotent

    allowed = VALID_TRANSITIONS.get(current, set())
    if new_status not in allowed:
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail=f"Invalid status transition: {current} -> {new_status}",
        )

    updated = repo.update_item_status(item_id, new_status)
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated
