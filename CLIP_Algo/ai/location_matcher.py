import math
import difflib
from typing import Optional, Union, Dict, Any

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on the earth in kilometers.
    """
    R = 6371.0  # Earth radius in kilometers

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def calculate_string_location_similarity(loc1_name: str, loc2_name: str) -> float:
    """
    Fallback location matching based on textual location names (e.g. 'Central Library' vs 'Library').
    """
    if not loc1_name or not loc2_name:
        return 0.5  # Neutral fallback score if one or both location strings are missing
    
    l1 = loc1_name.strip().lower()
    l2 = loc2_name.strip().lower()

    if l1 == l2:
        return 1.0

    # Sequence matcher ratio
    seq_score = difflib.SequenceMatcher(None, l1, l2).ratio()

    # Word set token containment & Jaccard similarity
    words1 = set(l1.split())
    words2 = set(l2.split())
    if words1 and words2:
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        jaccard_score = len(intersection) / len(union)
        
        # Token subset overlap (e.g. 'library' shared between 'central library' and 'library hall')
        min_len = min(len(words1), len(words2))
        token_overlap = len(intersection) / min_len if min_len > 0 else 0.0
        token_set_score = token_overlap
    else:
        jaccard_score = 0.0
        token_set_score = 0.0

    return max(seq_score, jaccard_score, token_set_score)

def calculate_location_similarity(
    loc1: Union[Dict[str, Any], str],
    loc2: Union[Dict[str, Any], str],
    half_decay_distance_km: float = 0.5
) -> float:
    """
    Calculate location similarity between two items.
    Accepts dictionaries containing 'latitude', 'longitude', 'location' or direct string location names.

    Formula when lat/lon available: score = exp(-distance_km / decay_param)
    """
    lat1, lon1, name1 = _extract_location_info(loc1)
    lat2, lon2, name2 = _extract_location_info(loc2)

    # Check if geographic coordinates are valid for both
    if lat1 is not None and lon1 is not None and lat2 is not None and lon2 is not None:
        try:
            distance_km = haversine_distance(float(lat1), float(lon1), float(lat2), float(lon2))
            decay_factor = math.log(2) / max(0.01, half_decay_distance_km)
            coord_score = math.exp(-decay_factor * distance_km)
            return max(0.0, min(1.0, float(coord_score)))
        except (ValueError, TypeError):
            pass

    # Fallback to string similarity if coordinates missing or invalid
    return calculate_string_location_similarity(name1, name2)

def _extract_location_info(loc: Union[Dict[str, Any], str]) -> tuple[Optional[float], Optional[float], str]:
    if isinstance(loc, str):
        return None, None, loc
    if isinstance(loc, dict):
        lat = loc.get("latitude")
        lon = loc.get("longitude")
        name = loc.get("location", loc.get("name", ""))
        return lat, lon, str(name)
    return None, None, ""
