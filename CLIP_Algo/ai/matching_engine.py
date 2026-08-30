from dataclasses import dataclass, field
from typing import List, Dict, Any, Union, Optional
import logging

from ai.clip_encoder import CLIPEncoder
from ai.location_matcher import calculate_location_similarity
from ai.time_matcher import calculate_time_similarity

logger = logging.getLogger(__name__)

@dataclass
class Item:
    """Dataclass representation of a Lost or Found item."""
    id: str
    type: str  # 'lost' or 'found'
    category: str
    description: str
    location: str
    timestamp: str
    image_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str = "active"
    reporter_id: Optional[str] = None
    embedding: Optional[List[float]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Item":
        return cls(
            id=str(data.get("id", "")),
            type=str(data.get("type", "found")),
            category=str(data.get("category", "")),
            description=str(data.get("description", "")),
            location=str(data.get("location", "")),
            timestamp=str(data.get("timestamp", "")),
            image_url=data.get("image_url") or data.get("image"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            status=data.get("status", "active"),
            reporter_id=data.get("reporter_id"),
            embedding=data.get("embedding"),
        )

class MatchingEngine:
    """
    Core AI/ML Multi-Modal Matching Engine for Cream Beans Lost & Found System.
    Computes Identity & Context scores and generates ranked match candidate results.
    """

    def __init__(self, encoder: Optional[CLIPEncoder] = None):
        self.encoder = encoder or CLIPEncoder.get_instance()

    def evaluate_pair(
        self,
        lost_item: Union[Item, Dict[str, Any]],
        found_item: Union[Item, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluate match scores between a lost item and a found item candidate.
        """
        if not isinstance(lost_item, Item):
            lost = Item.from_dict(lost_item)
        else:
            lost = lost_item

        if not isinstance(found_item, Item):
            found = Item.from_dict(found_item)
        else:
            found = found_item

        # 1. Text / Description Similarity
        text_score = self.encoder.calculate_text_text_similarity(
            lost.description, found.description
        )

        # 2. Image Similarity
        has_lost_image = bool(lost.image_url)
        has_found_image = bool(found.image_url)

        if has_lost_image and has_found_image:
            image_score = self.encoder.calculate_image_image_similarity(
                lost.image_url, found.image_url
            )
        elif has_lost_image and not has_found_image:
            image_score = self.encoder.calculate_text_image_similarity(
                found.description, lost.image_url
            )
        elif not has_lost_image and has_found_image:
            image_score = self.encoder.calculate_text_image_similarity(
                lost.description, found.image_url
            )
        else:
            image_score = 0.0

        # Identity Score calculation with graceful re-weighting
        if (has_lost_image or has_found_image) and lost.description and found.description:
            identity_score = 0.5 * text_score + 0.5 * image_score
        elif lost.description and found.description:
            identity_score = text_score  # Fallback to 100% text if images missing
        elif has_lost_image or has_found_image:
            identity_score = image_score  # Fallback to 100% image if descriptions sparse
        else:
            identity_score = 0.0

        # 3. Location Similarity
        location_score = calculate_location_similarity(
            {
                "latitude": lost.latitude,
                "longitude": lost.longitude,
                "location": lost.location
            },
            {
                "latitude": found.latitude,
                "longitude": found.longitude,
                "location": found.location
            }
        )

        # 4. Time Similarity
        time_score = calculate_time_similarity(lost.timestamp, found.timestamp)

        # Context Score calculation
        context_score = 0.6 * location_score + 0.4 * time_score

        # Final Score calculation
        final_score = 0.7 * identity_score + 0.3 * context_score

        # Normalize and round outputs
        return {
            "item_id": found.id,
            "image_score": round(max(0.0, min(1.0, float(image_score))), 4),
            "text_score": round(max(0.0, min(1.0, float(text_score))), 4),
            "location_score": round(max(0.0, min(1.0, float(location_score))), 4),
            "time_score": round(max(0.0, min(1.0, float(time_score))), 4),
            "final_score": round(max(0.0, min(1.0, float(final_score))), 4),
        }

    def rank_candidates(
        self,
        lost_item: Union[Item, Dict[str, Any]],
        candidate_found_items: List[Union[Item, Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Rank candidate found items against a lost item.
        Returns a sorted list of match evaluation dicts.
        """
        results = []
        for candidate in candidate_found_items:
            match_dict = self.evaluate_pair(lost_item, candidate)
            results.append(match_dict)

        # Sort by final_score descending
        results.sort(key=lambda x: x["final_score"], reverse=True)
        return results

def find_matches(
    lost_item: Union[Item, Dict[str, Any]],
    candidate_found_items: List[Union[Item, Dict[str, Any]]]
) -> List[Dict[str, Any]]:
    """
    Module interface function required by SIH spec.
    """
    engine = MatchingEngine()
    return engine.rank_candidates(lost_item, candidate_found_items)
