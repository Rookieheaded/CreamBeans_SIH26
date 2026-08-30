"""
database/models.py
Canonical Data Structures for Cream Beans SIH 2026 Campus Lost & Found System
Person 6: Database & Data-Integration Engineer

This module provides Python dataclasses and Pydantic models mapping directly to
the Supabase SQL schema and existing AI engine contract with zero field-name mutation.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class User:
    """
    Canonical User representation matching Supabase 'users' table.
    """
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    is_admin: bool = False
    created_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            email=str(data["email"]),
            phone=data.get("phone"),
            is_admin=bool(data.get("is_admin", False)),
            created_at=str(data["created_at"]) if data.get("created_at") else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Item:
    """
    Canonical Item representation matching Supabase 'items' table
    and direct AI engine consumption contract.

    Contract Fields:
      - id
      - type ('lost' | 'found')
      - category
      - description
      - location
      - timestamp
      - image_url
      - latitude
      - longitude
      - status ('active' | 'matched' | 'returned')
      - reporter_id
      - embedding
    """
    id: str
    type: str  # 'lost' | 'found'
    category: str
    description: str
    location: str
    timestamp: str  # ISO-8601 string or datetime string representation
    image_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str = "active"  # 'active' | 'matched' | 'returned'
    reporter_id: str = ""
    embedding: Optional[List[float]] = None
    created_at: Optional[str] = None

    def __post_init__(self):
        if self.type not in ("lost", "found"):
            raise ValueError(f"Invalid item type '{self.type}'. Must be 'lost' or 'found'.")
        if self.status not in ("active", "matched", "returned"):
            raise ValueError(f"Invalid item status '{self.status}'. Must be 'active', 'matched', or 'returned'.")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Item":
        """
        Construct Item from database row or API dictionary without field-name hacks.
        """
        return cls(
            id=str(data["id"]),
            type=str(data["type"]),
            category=str(data["category"]),
            description=str(data["description"]),
            location=str(data["location"]),
            timestamp=str(data["timestamp"]),
            image_url=data.get("image_url"),
            latitude=float(data["latitude"]) if data.get("latitude") is not None else None,
            longitude=float(data["longitude"]) if data.get("longitude") is not None else None,
            status=str(data.get("status", "active")),
            reporter_id=str(data["reporter_id"]),
            embedding=list(data["embedding"]) if data.get("embedding") is not None else None,
            created_at=str(data["created_at"]) if data.get("created_at") else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Item to dictionary matching canonical AI contract exactly.
        """
        return {
            "id": self.id,
            "type": self.type,
            "category": self.category,
            "description": self.description,
            "location": self.location,
            "timestamp": self.timestamp,
            "image_url": self.image_url,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "status": self.status,
            "reporter_id": self.reporter_id,
            "embedding": self.embedding,
        }


@dataclass
class MatchResult:
    """
    Canonical Match Result returned by AI engine and stored in Supabase 'matches' table.
    """
    id: Optional[str]
    lost_item_id: str
    found_item_id: str
    image_score: float
    text_score: float
    location_score: float
    time_score: float
    final_score: float
    created_at: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MatchResult":
        return cls(
            id=str(data["id"]) if data.get("id") else None,
            lost_item_id=str(data["lost_item_id"]),
            found_item_id=str(data["found_item_id"]),
            image_score=float(data["image_score"]),
            text_score=float(data["text_score"]),
            location_score=float(data["location_score"]),
            time_score=float(data["time_score"]),
            final_score=float(data["final_score"]),
            created_at=str(data["created_at"]) if data.get("created_at") else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        res = {
            "lost_item_id": self.lost_item_id,
            "found_item_id": self.found_item_id,
            "image_score": self.image_score,
            "text_score": self.text_score,
            "location_score": self.location_score,
            "time_score": self.time_score,
            "final_score": self.final_score,
        }
        if self.id:
            res["id"] = self.id
        if self.created_at:
            res["created_at"] = self.created_at
        return res


@dataclass
class Claim:
    """
    Canonical Claim representation matching Supabase 'claims' table.
    Associates claimant, lost item, found item, optional match_id, and claim status.
    """
    id: str
    claimant_id: str
    lost_item_id: str
    found_item_id: str
    match_id: Optional[str] = None
    status: str = "pending"  # 'pending' | 'approved' | 'rejected'
    created_at: Optional[str] = None

    def __post_init__(self):
        if self.status not in ("pending", "approved", "rejected"):
            raise ValueError(f"Invalid claim status '{self.status}'. Must be 'pending', 'approved', or 'rejected'.")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Claim":
        return cls(
            id=str(data["id"]),
            claimant_id=str(data["claimant_id"]),
            lost_item_id=str(data["lost_item_id"]),
            found_item_id=str(data["found_item_id"]),
            match_id=str(data["match_id"]) if data.get("match_id") else None,
            status=str(data.get("status", "pending")),
            created_at=str(data["created_at"]) if data.get("created_at") else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MatchDetails:
    """
    Complete Match Information combining MatchResult, Found Item, Lost Item, and Reporter Contact Info.
    """
    match: MatchResult
    lost_item: Item
    found_item: Item
    found_reporter: User
