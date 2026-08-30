"""
Placeholder matching engine.

Implements simple, deterministic, dependency-free heuristics so the backend
can be developed and tested end-to-end before the real CLIP-based engine is
wired in. The scoring here is intentionally crude (word overlap for text,
naive distance/time decay) — it exists only to produce values in the
correct shape and range, NOT to be a real matcher.

Contract (must match the real ai package exactly):

    find_matches(lost_item, candidate_found_items) -> list[dict]

    Each result dict contains:
        item_id, image_score, text_score, location_score, time_score,
        final_score

    All scores in [0.0, 1.0]. Results sorted by final_score descending.

    Accepts either `Item` objects or plain dicts for both the lost item and
    each candidate.
"""

from dataclasses import dataclass, field
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
from typing import Any, Optional, Union


@dataclass
class Item:
    id: str
    type: str
    category: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    timestamp: Optional[str] = None
    image_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: Optional[str] = None
    reporter_id: Optional[str] = None
    embedding: Optional[list] = field(default=None)


def _as_item(obj: Union[Item, dict]) -> Item:
    if isinstance(obj, Item):
        return obj
    if isinstance(obj, dict):
        known = {f: obj.get(f) for f in Item.__dataclass_fields__.keys()}
        return Item(**known)
    raise TypeError(f"Expected Item or dict, got {type(obj)!r}")


def _text_score(a: Optional[str], b: Optional[str]) -> float:
    if not a or not b:
        return 0.0
    wa = set(w.lower().strip(".,!?") for w in a.split())
    wb = set(w.lower().strip(".,!?") for w in b.split())
    if not wa or not wb:
        return 0.0
    overlap = len(wa & wb)
    union = len(wa | wb)
    return round(overlap / union, 4) if union else 0.0


def _haversine_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def _location_score(lost: Item, found: Item) -> float:
    if (
        lost.latitude is not None
        and lost.longitude is not None
        and found.latitude is not None
        and found.longitude is not None
    ):
        dist_km = _haversine_km(lost.latitude, lost.longitude, found.latitude, found.longitude)
        # decay: 0km -> 1.0, 5km+ -> ~0
        return round(max(0.0, 1.0 - min(dist_km / 5.0, 1.0)), 4)
    if lost.location and found.location:
        return 1.0 if lost.location.strip().lower() == found.location.strip().lower() else 0.3
    return 0.0


def _parse_ts(ts: Optional[str]) -> Optional[datetime]:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def _time_score(lost: Item, found: Item) -> float:
    t1, t2 = _parse_ts(lost.timestamp), _parse_ts(found.timestamp)
    if not t1 or not t2:
        return 0.0
    hours = abs((t1 - t2).total_seconds()) / 3600.0
    # decay: 0h -> 1.0, 72h+ -> ~0
    return round(max(0.0, 1.0 - min(hours / 72.0, 1.0)), 4)


def _image_score(lost: Item, found: Item) -> float:
    # Placeholder: no real embedding comparison available yet.
    # If both embeddings are present and same length, do naive cosine-ish
    # overlap; otherwise fall back to a neutral placeholder value.
    e1, e2 = lost.embedding, found.embedding
    if e1 and e2 and len(e1) == len(e2):
        dot = sum(a * b for a, b in zip(e1, e2))
        n1 = sqrt(sum(a * a for a in e1)) or 1.0
        n2 = sqrt(sum(b * b for b in e2)) or 1.0
        cos_sim = dot / (n1 * n2)
        return round(max(0.0, min(1.0, (cos_sim + 1) / 2)), 4)
    return 0.5


class MatchingEngine:
    """Placeholder engine object, mirrors the expected real-engine shape."""

    def score_pair(self, lost: Item, found: Item) -> dict:
        image_score = _image_score(lost, found)
        text_score = _text_score(lost.description, found.description)
        location_score = _location_score(lost, found)
        time_score = _time_score(lost, found)

        identity_score = 0.5 * text_score + 0.5 * image_score
        context_score = 0.6 * location_score + 0.4 * time_score
        final_score = round(0.7 * identity_score + 0.3 * context_score, 4)

        return {
            "item_id": found.id,
            "image_score": image_score,
            "text_score": text_score,
            "location_score": location_score,
            "time_score": time_score,
            "final_score": final_score,
        }

    def find_matches(self, lost_item: Union[Item, dict], candidate_found_items: list) -> list:
        lost = _as_item(lost_item)
        results = [self.score_pair(lost, _as_item(c)) for c in candidate_found_items]
        results.sort(key=lambda r: r["final_score"], reverse=True)
        return results


_default_engine = MatchingEngine()


def find_matches(lost_item: Union[Item, dict], candidate_found_items: list) -> list:
    """Module-level convenience function matching the required import:

        from ai import find_matches
    """
    return _default_engine.find_matches(lost_item, candidate_found_items)
