"""
Database-row <-> AI-Item field mapping.

Per the backend brief, these field names are copied 1:1 between Supabase
and the AI module. This module exists as the SINGLE place that mapping
happens, so it's obvious nothing gets renamed anywhere else in the
codebase.

    Supabase column -> AI field
    id              -> id
    type            -> type
    category        -> category
    description     -> description
    location        -> location
    timestamp       -> timestamp
    image_url       -> image_url
    latitude        -> latitude
    longitude       -> longitude
    status          -> status
    reporter_id     -> reporter_id
    embedding       -> embedding
"""

AI_ITEM_FIELDS = (
    "id",
    "type",
    "category",
    "description",
    "location",
    "timestamp",
    "image_url",
    "latitude",
    "longitude",
    "status",
    "reporter_id",
    "embedding",
)


def db_row_to_ai_item(row: dict) -> dict:
    """Converts a Supabase `items` row into the dict shape find_matches()
    expects. No field is renamed; unknown/extra DB columns (e.g.
    created_at) are simply dropped since the AI contract doesn't use them.
    """
    out = {field: row.get(field) for field in AI_ITEM_FIELDS}
    # timestamp may be a datetime object (from Pydantic) rather than a str;
    # normalize to ISO-8601 string since that's what the AI engine expects.
    ts = out.get("timestamp")
    if hasattr(ts, "isoformat"):
        out["timestamp"] = ts.isoformat()
    return out
