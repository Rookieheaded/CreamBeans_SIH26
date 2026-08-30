"""
The bridge to the AI matching engine.

This module is the ONLY place `find_matches` is called from. Everything
else in the backend deals with database rows / API schemas; this file's
job is purely: fetch candidates -> map to AI shape -> call the AI ->
persist -> join with DB info for the response.

Per the brief: the AI engine is a black box. This file must never:
  - recompute or override final_score
  - rename any of the five score fields
  - implement a second scoring algorithm
"""

from fastapi import HTTPException

from ai import find_matches

from backend.config import settings
from backend.database.repository import Repository
from backend.services.item_service import get_item_or_404
from backend.utils.mapping import db_row_to_ai_item


def get_ranked_matches(repo: Repository, lost_item_id: str) -> dict:
    """Implements the GET /items/{lost_item_id}/matches workflow:

    1. Retrieve the lost item.
    2. Verify it is actually a lost item.
    3. Retrieve relevant active found items (candidates).
    4. Call find_matches().
    5. Store the resulting scores in `matches`.
    6. Join with found-item info + finder contact details.
    7. Return ranked results.
    """
    # include_embedding=True: this is the one path in the backend that
    # actually needs the CLIP vector, since it's handed to find_matches().
    # Every other read path (GET /items, GET /items/{id}) explicitly
    # leaves it out to avoid shipping large vectors for no reason.
    lost_row = get_item_or_404(repo, lost_item_id, include_embedding=True)

    if lost_row["type"] != "lost":
        raise HTTPException(
            status_code=400,
            detail=f"Item {lost_item_id} is not a lost item (type={lost_row['type']!r})",
        )

    candidate_rows = repo.list_items(
        type="found",
        status="active",
        limit=settings.MAX_MATCH_CANDIDATES,
        include_embedding=True,
    )

    if not candidate_rows:
        return {"lost_item_id": lost_item_id, "matches": []}

    lost_ai_item = db_row_to_ai_item(lost_row)
    candidate_ai_items = [db_row_to_ai_item(r) for r in candidate_rows]

    # --- black-box AI call -------------------------------------------------
    ai_results = find_matches(lost_ai_item, candidate_ai_items)
    # ------------------------------------------------------------------------

    # Persist the canonical scores exactly as returned by the AI.
    repo.save_matches(lost_item_id, ai_results)

    # Join with found-item + finder details for the API response.
    candidates_by_id = {r["id"]: r for r in candidate_rows}

    # Batch-fetch every finder in ONE query instead of one query per match
    # result (was previously N queries for N results — the classic N+1
    # pattern, and the only place in the backend it was happening).
    reporter_ids = [
        candidates_by_id[result["item_id"]]["reporter_id"]
        for result in ai_results
        if result["item_id"] in candidates_by_id
    ]
    finders_by_id = repo.get_users(reporter_ids)

    enriched = []
    for result in ai_results:
        found_row = candidates_by_id.get(result["item_id"])
        if not found_row:
            # Shouldn't happen since results come from the same candidate
            # set, but guard against it rather than crashing the endpoint.
            continue

        finder = finders_by_id.get(found_row["reporter_id"])

        enriched.append(
            {
                "item_id": result["item_id"],
                "final_score": result["final_score"],
                "image_score": result["image_score"],
                "text_score": result["text_score"],
                "location_score": result["location_score"],
                "time_score": result["time_score"],
                "description": found_row.get("description"),
                "image_url": found_row.get("image_url"),
                "location": found_row.get("location"),
                "timestamp": found_row.get("timestamp"),
                "status": found_row.get("status"),
                "finder": (
                    {
                        "name": finder["name"],
                        "email": finder["email"],
                        "phone": finder.get("phone"),
                    }
                    if finder
                    else None
                ),
            }
        )

    return {"lost_item_id": lost_item_id, "matches": enriched}
