"""
Minimal claim workflow, per the brief:

    Lost user -> views potential match -> initiates claim -> claim recorded
    -> admin/security sees claim -> item can eventually be marked returned.

No verification/challenge-question system is implemented (explicitly out
of scope for the SIH demo per the brief).

Design decision (documented, not silently assumed): creating a claim also
transitions BOTH the lost item and the found item from "active" to
"matched" if they're currently active, since a claim in flight means the
item is no longer just "available" — an admin/security user still makes
the final call by transitioning to "returned" via PATCH /items/{id}/status.
This reuses the exact same status machine already defined in
item_service.VALID_TRANSITIONS rather than introducing a second one.
"""

from fastapi import HTTPException

from backend.database.repository import Repository
from backend.models.schemas import ClaimCreate
from backend.services.item_service import get_item_or_404, update_status


def create_claim(repo: Repository, payload: ClaimCreate) -> dict:
    lost_item = get_item_or_404(repo, payload.lost_item_id)
    found_item = get_item_or_404(repo, payload.found_item_id)

    if lost_item["type"] != "lost":
        raise HTTPException(400, detail="lost_item_id does not refer to a lost item")
    if found_item["type"] != "found":
        raise HTTPException(400, detail="found_item_id does not refer to a found item")

    claimant_id = payload.claimant_id or lost_item["reporter_id"]
    if not repo.get_user(claimant_id):
        raise HTTPException(404, detail="claimant_id does not match any known user")

    claim_row = repo.create_claim(
        {
            "lost_item_id": payload.lost_item_id,
            "found_item_id": payload.found_item_id,
            "claimant_id": claimant_id,
            "message": payload.message,
            "status": "pending",
        }
    )

    # Best-effort status bump; a claim on an already-matched/returned item
    # (e.g. a second claimant) shouldn't block claim creation itself.
    for item_id in (payload.lost_item_id, payload.found_item_id):
        item = repo.get_item(item_id)
        if item and item["status"] == "active":
            update_status(repo, item_id, "matched")

    return claim_row
