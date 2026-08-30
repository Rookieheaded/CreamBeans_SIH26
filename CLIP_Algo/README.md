# CLIP_Algo — Cream Beans AI/ML Matching Engine

> Multi-Modal Candidate Retrieval Engine for SIH 2026 Campus Lost & Found Intelligence System

## 1. Module Overview
`CLIP_Algo` provides zero-shot multi-modal similarity ranking between LOST item reports and FOUND candidate items using Hugging Face Transformers pre-trained **CLIP** (`openai/clip-vit-base-patch32`), geospatial Haversine distance decay, and temporal decay functions.

## 2. Installation

```bash
pip install -r requirements.txt
```

## 3. How to Import and Call `find_matches()`

```python
from ai import find_matches

lost_report = {
    "id": "L101",
    "type": "lost",
    "category": "Bags",
    "description": "Black Lenovo laptop backpack",
    "image_url": "https://xyz.supabase.co/storage/v1/object/public/item-images/lost_bag.jpg",
    "location": "Central Library Reading Room",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "timestamp": "2026-08-29T10:00:00Z"
}

found_candidates = [
    {
        "id": "F001",
        "type": "found",
        "category": "Bags",
        "description": "Dark Lenovo bag",
        "image_url": "https://xyz.supabase.co/storage/v1/object/public/item-images/found_bag.jpg",
        "location": "Library Lawn",
        "latitude": 12.9720,
        "longitude": 77.5950,
        "timestamp": "2026-08-29T11:00:00Z"
    }
]

matches = find_matches(lost_report, found_candidates)
print(matches)
```

## 4. Expected Input Item Fields
Matches canonical Supabase PostgreSQL `items` table:
- `id` (str)
- `type` (str: 'lost' | 'found')
- `category` (str)
- `description` (str)
- `location` (str)
- `timestamp` (str: ISO 8601)
- `image_url` (Optional[str]: HTTPS Supabase URL, local path, base64 data URI)
- `latitude` (Optional[float])
- `longitude` (Optional[float])
- `status` (str)
- `reporter_id` (Optional[str])
- `embedding` (Optional[list of float])

## 5. Expected Output Format
Returns candidate match dicts sorted by `final_score` descending:

```json
[
  {
    "item_id": "F001",
    "image_score": 0.9412,
    "text_score": 0.8845,
    "location_score": 0.9230,
    "time_score": 0.8120,
    "final_score": 0.9105
  }
]
```

## 6. Running Tests

```bash
pytest tests/ -v
```

## 7. Documentation Links
- **[documentation/AI_INTERFACE.md](documentation/AI_INTERFACE.md)**: Formal integration contract for Backend API.
- **[documentation/MATCHING_ENGINE.md](documentation/MATCHING_ENGINE.md)**: Engine architecture, formulas & weights.
- **[documentation/stage1_clip_proof.md](documentation/stage1_clip_proof.md)**: Stage 1 CLIP benchmarks & zero-shot validation.
