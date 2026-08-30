from fastapi import APIRouter, Depends

from backend.api.deps import repo_dependency
from backend.database.repository import Repository
from backend.models.schemas import ClaimCreate, ClaimOut
from backend.services import claim_service

router = APIRouter(prefix="/claims", tags=["claims"])


@router.post("", response_model=ClaimOut, status_code=201)
def create_claim(payload: ClaimCreate, repo: Repository = Depends(repo_dependency)):
    return claim_service.create_claim(repo, payload)
