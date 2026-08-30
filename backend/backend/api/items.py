from typing import Optional

from fastapi import APIRouter, Depends, Query

from backend.api.deps import repo_dependency
from backend.api.auth import get_current_auth_user
from backend.database.repository import Repository
from backend.models.schemas import ItemCreate, ItemOut, ItemStatusUpdate
from backend.services import item_service
from backend.services.match_service import get_ranked_matches

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/lost", response_model=ItemOut, status_code=201)
def report_lost_item(payload: ItemCreate, repo: Repository = Depends(repo_dependency), _auth_user: dict = Depends(get_current_auth_user)):
    """Reports a lost item. Matching is triggered separately via
    GET /items/{id}/matches (kept as its own step so the frontend can show
    the "report received" confirmation immediately, then fetch matches).
    """
    return item_service.report_item(repo, "lost", payload)


@router.post("/found", response_model=ItemOut, status_code=201)
def report_found_item(payload: ItemCreate, repo: Repository = Depends(repo_dependency), _auth_user: dict = Depends(get_current_auth_user)):
    """Reports a found item."""
    return item_service.report_item(repo, "found", payload)


@router.get("", response_model=list[ItemOut])
def list_items(
    type: Optional[str] = Query(default=None, description="'lost' or 'found'"),
    status: Optional[str] = Query(default=None, description="active | matched | returned"),
    limit: int = Query(default=50, ge=1, le=500, description="Page size, capped at 500"),
    offset: int = Query(default=0, ge=0, description="Rows to skip, for pagination"),
    repo: Repository = Depends(repo_dependency),
    _auth_user: dict = Depends(get_current_auth_user),
):
    return item_service.list_items(repo, type, status, limit=limit, offset=offset)


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: str, repo: Repository = Depends(repo_dependency), _auth_user: dict = Depends(get_current_auth_user)):
    return item_service.get_item_or_404(repo, item_id)


@router.get("/{item_id}/matches")
def get_matches(item_id: str, repo: Repository = Depends(repo_dependency), _auth_user: dict = Depends(get_current_auth_user)):
    """Runs the full match workflow: retrieve lost item, fetch candidate
    found items, call the AI engine, persist scores, join with finder
    contact details, and return the ranked list.
    """
    return get_ranked_matches(repo, item_id)


@router.patch("/{item_id}/status", response_model=ItemOut)
def update_item_status(
    item_id: str,
    payload: ItemStatusUpdate,
    repo: Repository = Depends(repo_dependency),
    _auth_user: dict = Depends(get_current_auth_user),
):
    return item_service.update_status(repo, item_id, payload.status)
