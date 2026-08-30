"""
Pydantic request/response models.

These are API-layer shapes only. They intentionally mirror the Supabase
`items` / `matches` / `users` columns without renaming anything, per the
backend brief's data-mapping rules.
"""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict

ItemType = Literal["lost", "found"]
ItemStatus = Literal["active", "matched", "returned"]


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

class ReporterIn(BaseModel):
    """Reporter contact info supplied inline with an item report.

    If a user with this email already exists, the backend reuses it
    (create-or-retrieve) instead of creating a duplicate row.
    """
    name: str
    email: EmailStr
    phone: Optional[str] = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: EmailStr
    phone: Optional[str] = None
    created_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Items
# ---------------------------------------------------------------------------

class ItemCreate(BaseModel):
    """Shared fields for reporting a lost or found item."""
    category: Optional[str] = None
    description: str
    image_url: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timestamp: Optional[datetime] = None  # defaults to "now" if omitted
    reporter: ReporterIn


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    reporter_id: str
    type: ItemType
    category: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timestamp: Optional[datetime] = None
    status: ItemStatus
    created_at: Optional[datetime] = None


class ItemStatusUpdate(BaseModel):
    status: ItemStatus


# ---------------------------------------------------------------------------
# Matches
# ---------------------------------------------------------------------------

class FinderContact(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None


class MatchResult(BaseModel):
    """A single ranked match, joining AI scores with item + finder info.

    NOTE: image_score / text_score / location_score / time_score /
    final_score are the AI engine's canonical fields and are never
    renamed or recomputed here.
    """
    item_id: str
    final_score: float
    image_score: float
    text_score: float
    location_score: float
    time_score: float

    description: Optional[str] = None
    image_url: Optional[str] = None
    location: Optional[str] = None
    timestamp: Optional[datetime] = None
    status: Optional[ItemStatus] = None

    finder: Optional[FinderContact] = None


class MatchListResponse(BaseModel):
    lost_item_id: str
    matches: List[MatchResult]


# ---------------------------------------------------------------------------
# Claims
# ---------------------------------------------------------------------------

class ClaimCreate(BaseModel):
    lost_item_id: str
    found_item_id: str
    claimant_id: Optional[str] = None  # falls back to lost item's reporter
    message: Optional[str] = Field(
        default=None, description="Optional note from claimant to admin/finder"
    )


class ClaimOut(BaseModel):
    id: str
    lost_item_id: str
    found_item_id: str
    claimant_id: str
    message: Optional[str] = None
    status: Literal["pending", "approved", "rejected"] = "pending"
    created_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------

class HealthOut(BaseModel):
    status: str = "ok"
    ai_engine: str
    database: str
