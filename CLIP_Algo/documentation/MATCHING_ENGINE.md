# AI/ML MATCHING ENGINE DOCUMENTATION

> Cream Beans — SIH 2026 Campus Lost & Found Intelligence System

---

## 1. Overview & Architecture

The **Cream Beans Matching Engine** is an intelligent multi-modal candidate retrieval system designed to identify potential matches between LOST item reports and existing FOUND item reports in a campus environment.

It operates without requiring exact wording or identical images, combining **Visual**, **Textual (Semantic)**, **Geospatial**, and **Temporal** signals into a unified match score.

```
                  +-------------------------------------------------------+
                  |                      Lost Item                        |
                  |  - Category: "Bags"                                   |
                  |  - Description: "Black backpack with laptop comp..."  |
                  |  - Image: [Lost Backpack Photo]                       |
                  |  - Location: (12.9716, 77.5946) "Central Library"     |
                  |  - Timestamp: "2026-08-29T10:00:00Z"                  |
                  +---------------------------+---------------------------+
                                              |
                                              v
                              +-------------------------------+
                              |    Multi-Modal CLIP Encoder   |
                              |  (openai/clip-vit-base-32)    |
                              +---------------+---------------+
                                              |
                                              v
               +------------------------------+------------------------------+
               |                                                             |
               v                                                             v
+-------------------------------+                             +-------------------------------+
|        Identity Scoring       |                             |        Context Scoring        |
|  - Text Similarity  (50%)     |                             |  - Location Decay (60%)       |
|  - Image Similarity (50%)     |                             |  - Time Decay     (40%)       |
+--------------+----------------+                             +---------------+---------------+
               |                                                             |
               +------------------------------+------------------------------+
                                              |
                                              v
                              +-------------------------------+
                              |    Final Score Computation    |
                              |  0.7 * Identity + 0.3 * Context|
                              +---------------+---------------+
                                              |
                                              v
                              +-------------------------------+
                              |    Ranked Candidates Output   |
                              +-------------------------------+
```

---

## 2. Scoring Formulas & Weights

### Identity Score
$$\text{Identity Score} = 0.5 \times \text{Description Similarity} + 0.5 \times \text{Image Similarity}$$

- **Description Similarity**: Calculated using zero-shot CLIP text embedding cosine similarity.
- **Image Similarity**: Calculated using zero-shot CLIP image embedding cosine similarity (or cross-modal text-to-image similarity if one photo is missing).

### Context Score
$$\text{Context Score} = 0.6 \times \text{Location Similarity} + 0.4 \times \text{Time Similarity}$$

- **Location Similarity**: Calculated via Haversine distance exponential decay:
  $$\text{Score} = \exp\left(-\frac{\ln(2) \cdot d_{\text{km}}}{0.5\text{ km}}\right)$$
  *(Falls back to Levenshtein / Token Ratio text similarity if GPS coordinates are missing)*.

- **Time Similarity**: Calculated via exponential half-life decay:
  $$\text{Score} = \exp\left(-\frac{\ln(2) \cdot \Delta t_{\text{hours}}}{48.0\text{ hours}}\right)$$
  *(Defaults to 0.5 if timestamp is missing or unparseable)*.

### Final Match Score
$$\text{Final Score} = 0.7 \times \text{Identity Score} + 0.3 \times \text{Context Score}$$

All scores are strictly normalized in $[0.0, 1.0]$.

---

## 3. Signal Degradation & Edge Case Handling

| Missing Signal | Behavior & Score Adjustment |
| --- | --- |
| **Missing Lost Image** | Identity score reweights to 100% Description Similarity (or Cross-Modal text-to-image matching against found photo). |
| **Missing Found Image** | Identity score reweights to 100% Description Similarity (or Cross-Modal text-to-image matching against lost photo). |
| **Both Images Missing** | Identity score equals 100% Description Similarity. |
| **Sparse / Missing Description** | Identity score reweights to 100% Image Similarity. |
| **Missing Lat / Long Coordinates** | Location similarity falls back to text token similarity on location names. |
| **Missing Timestamp** | Time similarity defaults to neutral score of `0.50`. |

---

## 4. API & Python Integration Interface

### Function Signature

```python
from ai import find_matches

matches = find_matches(lost_item, candidate_found_items)
```

### Input Schema
`lost_item` (dict or `Item` object) & `candidate_found_items` (list of dicts or `Item` objects):

```json
{
  "id": "L101",
  "category": "Bags",
  "description": "Black backpack with laptop compartment",
  "image_url": "https://example.com/images/lost_bag.jpg",
  "location": "Central Library Reading Room",
  "latitude": 12.9716,
  "longitude": 77.5946,
  "timestamp": "2026-08-29T10:00:00Z"
}
```

### Output Schema
Returns a list of candidate dictionaries sorted by `final_score` descending:

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
    "item_id": "F005",
    "image_score": 0.0,
    "text_score": 0.8520,
    "location_score": 0.9500,
    "time_score": 0.8800,
    "final_score": 0.8114
  }
]
```

---

## 5. Verification & Testing

Run unit tests and verification checks:

```bash
# Run unit test suite
pytest tests/ -v

# Run Stage 1 experiment & generate CLIP proof report
python -m ai.stage1_experiment
```
