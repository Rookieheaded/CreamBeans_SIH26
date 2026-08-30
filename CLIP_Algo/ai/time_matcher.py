import math
from datetime import datetime, timezone
from typing import Union, Optional
from dateutil import parser as date_parser

def parse_timestamp(ts: Union[datetime, str, int, float]) -> Optional[datetime]:
    """Parse various timestamp formats into a UTC datetime object."""
    if ts is None:
        return None
    
    if isinstance(ts, datetime):
        if ts.tzinfo is None:
            return ts.replace(tzinfo=timezone.utc)
        return ts.astimezone(timezone.utc)

    if isinstance(ts, (int, float)):
        # Assume unix timestamp
        return datetime.fromtimestamp(ts, tz=timezone.utc)

    if isinstance(ts, str):
        ts_str = ts.strip()
        if not ts_str:
            return None
        try:
            # Try ISO 8601 parsing
            dt = date_parser.parse(ts_str)
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            return None

    return None

def calculate_time_similarity(
    time1: Union[datetime, str, int, float, None],
    time2: Union[datetime, str, int, float, None],
    half_decay_hours: float = 48.0
) -> float:
    """
    Calculate time similarity between lost item time and found item time.
    Uses exponential half-life decay: score = exp(-ln(2) * delta_hours / half_decay_hours)

    Default half_decay_hours = 48.0 (2 days).
    - 0 hours difference -> score 1.0
    - 24 hours difference -> score ~0.707
    - 48 hours difference -> score 0.50
    - 96 hours (4 days) -> score 0.25
    """
    dt1 = parse_timestamp(time1)
    dt2 = parse_timestamp(time2)

    if dt1 is None or dt2 is None:
        return 0.5  # Neutral score if timestamp is missing

    delta_seconds = abs((dt1 - dt2).total_seconds())
    delta_hours = delta_seconds / 3600.0

    decay_factor = math.log(2) / max(0.1, half_decay_hours)
    time_score = math.exp(-decay_factor * delta_hours)

    return max(0.0, min(1.0, float(time_score)))
