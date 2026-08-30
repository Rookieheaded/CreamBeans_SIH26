# AI MODULE INTERFACE CONTRACT (AI_INTERFACE.md)

> Cream Beans — SIH 2026 Campus Lost & Found Intelligence System
> Formal Integration Contract between Backend API & AI Matching Engine

---

## 1. Overview & Public Entry Point

The `ai` module exposes a clean, typed Python interface for calculating multi-modal candidate rankings between LOST and FOUND item reports.

### Python Import

```python
from ai import find_matches, MatchingEngine, Item
```

### Primary Integration Function Signature

```python
find_matches(
    lost_item: Union[Item, Dict[str, Any]],
    candidate_found_items: List[Union[Item, Dict[str, Any]]]
) -> List[Dict[str, Any]]
```

- **`lost_item`**: A single dictionary or `Item` instance representing one LOST item report.
- **`candidate_found_items`**: A list of dictionaries or `Item` instances representing candidate FOUND item reports retrieved from the database.
- **Return Value**: A list of match dictionaries sorted by `final_score` in descending order.

---

## 2. Input Item Schema (Canonical Supabase Entity)

The `lost_item` parameter and each item in `candidate_found_items` map directly to the Supabase PostgreSQL `items` table schema.

| Field Name | Type | Required / Optional | Description & Example |
| --- | --- | --- | --- |
| `id` | `str` | Required | Unique item identifier (UUID string, e.g. `"a1b2c3d4-5678-..."`). |
| `type` | `str` | Required | Item report type: `"lost"` or `"found"`. |
| `category` | `str` | Required | Item category classification (e.g. `"Bags"`, `"Electronics"`, `"Wallets"`). |
| `description` | `str` | Required | Unstructured textual description (e.g. `"Black backpack with laptop compartment"`). |
| `location` | `str` | Required | Textual location description (e.g. `"Central Library Reading Room"`). |
| `timestamp` | `str` | Required | ISO 8601 formatted datetime string (e.g. `"2026-08-29T10:00:00Z"`). |
| `image_url` | `Optional[str]` | Optional | Image URL (HTTPS Supabase Storage URL, local file path, or base64 data URI). |
| `latitude` | `Optional[float]` | Optional | Geographic latitude coordinate (e.g. `12.9716`). |
| `longitude` | `Optional[float]` | Optional | Geographic longitude coordinate (e.g. `77.5946`). |
| `status` | `str` | Optional | Item lifecycle status: `"active"`, `"matched"`, or `"returned"`. Default: `"active"`. |
| `reporter_id` | `Optional[str]` | Optional | Reporter user UUID string. |
| `embedding` | `Optional[List[float]]` | Optional | Pre-computed 512-dim embedding vector list or `None`. |

---

## 3. Output Match Schema

The `find_matches()` function returns a list of dictionaries structured as follows:

```json
[
  {
    "item_id": "F001",
    "image_score": 0.9412,
    "text_score": 0.8845,
    "location_score": 0.9230,
    "time_score": 0.8120,
    "final_score": 0.9105
  },
  {
    "item_id": "F002",
    "image_score": 0.0,
    "text_score": 0.7510,
    "location_score": 0.5000,
    "time_score": 0.8800,
    "final_score": 0.6722
  }
]
```

### Output Field Specification

| Field Name | Type | Value Range | Description |
| --- | --- | --- | --- |
| `item_id` | `str` | Unique ID | The `id` of the candidate FOUND item. |
| `image_score` | `float` | `[0.0, 1.0]` | Normalized visual similarity score. |
| `text_score` | `float` | `[0.0, 1.0]` | Normalized textual semantic similarity score. |
| `location_score` | `float` | `[0.0, 1.0]` | Normalized geospatial location similarity score. |
| `time_score` | `float` | `[0.0, 1.0]` | Normalized temporal similarity score. |
| `final_score` | `float` | `[0.0, 1.0]` | Weighted multi-modal final ranking score. |

> [!IMPORTANT]
> **Score Interpretation**: `final_score` is a relative **ranking score** designed for candidate sorting, **NOT** a calibrated statistical probability. Do not refer to it as `confidence_score` in code or API contracts. Contact details belong to the database/backend layer and are not attached to AI output.

---

## 4. Scoring Formulas & Weights

```
Identity Score = 0.5 * Description Similarity + 0.5 * Image Similarity
Context Score  = 0.6 * Location Similarity    + 0.4 * Time Similarity
Final Score    = 0.7 * Identity Score        + 0.3 * Context Score
```

### Scoring Components
1. **Description Similarity**: Zero-shot CLIP text embedding cosine similarity between lost description and found description.
2. **Image Similarity**: Zero-shot CLIP image embedding cosine similarity (or cross-modal text-image similarity if only one photo is present).
3. **Location Similarity**: Haversine physical distance exponential decay ($d_{1/2} = 500\text{m}$), with text token overlap fallback if latitude/longitude coordinates are missing.
4. **Time Similarity**: Exponential half-life decay ($t_{1/2} = 48\text{ hours}$) based on the absolute delta between lost and found timestamps.

---

## 5. Graceful Missing-Data Degradation

| Missing Field | Engine Behavior |
| --- | --- |
| `image_url` missing in Lost report | `Identity Score` reweights to 100% Description Similarity (or Cross-Modal text-to-image match against Found image). |
| `image_url` missing in Found report | `Identity Score` reweights to 100% Description Similarity (or Cross-Modal text-to-image match against Lost image). |
| Both `image_url` fields missing | `Identity Score` equals 100% Description Similarity (`text_score`). `image_score` = `0.0`. |
| `description` sparse or missing | `Identity Score` reweights to 100% Image Similarity (`image_score`). |
| `latitude`/`longitude` missing | `Location Score` falls back to string token similarity on `location` names. |
| `timestamp` missing or invalid | `Time Score` defaults to neutral baseline `0.50`. |
