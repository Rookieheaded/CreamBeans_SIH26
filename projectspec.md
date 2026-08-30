# CREAM BEANS — SIH 2026 Project Specification

## Campus Lost & Found Intelligence System

### Core Problem
Current campus lost-and-found systems are fragmented across WhatsApp groups, noticeboards, security offices, and manual registers. They are difficult to search and depend heavily on exact descriptions.

### Core Solution
A web application where users can report lost or found items. The backend uses image, text, location, and time signals to rank potential matches.
The system does NOT require an exact image or exact wording to identify a potential match.

### Entities

#### USER
- `id`: UUID / String
- `name`: String
- `email`: String
- `phone`: String

#### ITEM
- `id`: UUID / String
- `reporter_id`: UUID / String
- `type`: `lost` | `found`
- `category`: String
- `description`: String
- `image_url`: String (optional)
- `location`: String
- `latitude`: Float (optional)
- `longitude`: Float (optional)
- `timestamp`: ISO 8601 String / Datetime
- `status`: `active` | `matched` | `returned`
- `embedding`: Vector / Array of Float (optional)

#### MATCH
- `id`: UUID / String
- `lost_item_id`: UUID / String
- `found_item_id`: UUID / String
- `image_score`: Float (0-1)
- `text_score`: Float (0-1)
- `location_score`: Float (0-1)
- `time_score`: Float (0-1)
- `final_score`: Float (0-1)

---

### Canonical Field Names

The following names are the shared data contract across the database, backend, and AI matching engine. They must not be renamed without coordination with the relevant owner and the tech lead.

#### ITEM
```text
id
reporter_id
type
category
description
image_url
location
latitude
longitude
timestamp
status
embedding
```

#### MATCH
```text
id
lost_item_id
found_item_id
image_score
text_score
location_score
time_score
final_score
```

Do not introduce alternative internal names such as `item_id`, `image`, `lat`, `lng`, `time`, or `user_id` for these canonical fields.

---

### Core API Endpoints
- `POST /items/lost`: Create lost item report
- `POST /items/found`: Create found item report
- `GET /items/{id}`: Get item by ID
- `GET /items/{id}/matches`: Get ranked candidate matches for item
- `GET /items`: List items
- `POST /claims`: Submit item ownership claim
- `PATCH /items/{id}/status`: Update item status

### API / AI Integration Contract

The existing AI/ML matching engine exposes the following primary interface:

```python
find_matches(lost_item, candidate_found_items)
```

Input:
- `lost_item`: one ITEM object/dictionary
- `candidate_found_items`: list of ITEM objects/dictionaries representing found-item candidates

Output:
- a list of MATCH results sorted by `final_score` descending

Each AI result contains exactly:

```text
item_id
image_score
text_score
location_score
time_score
final_score
```

All scores are normalized to `[0.0, 1.0]`.

`final_score` is a ranking score. It must not be described as a calibrated probability or renamed to `confidence`, `confidence_score`, or `match_percentage`.

The AI module is responsible for multimodal similarity and ranking. The backend is responsible for database access, API routing, and joining match results with item and reporter/contact information.

---

### Matching Formula & Scoring Rules

Identity Score = 0.5 * Description Similarity + 0.5 * Image Similarity
Context Score  = 0.6 * Location Similarity    + 0.4 * Time Similarity
Final Score    = 0.7 * Identity Score        + 0.3 * Context Score

Scores are strictly normalized to [0.0, 1.0].

#### Graceful Signal Degradation
- **Missing Image**: Identity score uses 100% Description Similarity.
- **Sparse Description**: Identity score uses 100% Image Similarity.
- **Missing Location Coordinates**: Falls back to string text similarity on location name.
- **Missing Timestamp**: Defaults to neutral time similarity baseline (0.5).

---

### Claims Workflow

Claims are intentionally lightweight for the SIH MVP. No challenge-question or separate verification system is required.

```text
Lost user
    ↓
Views potential match
    ↓
Submits claim
    ↓
Claim is recorded
    ↓
Admin/security can manage the case
    ↓
Item can be marked returned
```

A claim should associate the claimant, lost item, and found item and maintain a claim status and creation timestamp.

---

### Module Ownership

- **Person 1 — Tech Lead / Integration / Deployment**
- **Person 2 — User Frontend**
- **Person 3 — Admin/Security Frontend**
- **Person 4 — FastAPI Backend**
- **Person 5 — AI/ML Matching Engine**
- **Person 6 — Supabase Database / Testing**

Each person owns their assigned module. Shared contracts must not be changed independently.

---

### Architecture Principle

```text
User Frontend
      ↓
FastAPI Backend
      ↓
Supabase Database / Storage
      ↓
Existing AI Matching Engine
      ↓
Ranked Match Results
      ↓
FastAPI Backend
      ↓
User / Admin Frontend
```

The AI engine must remain a modular component. The backend must not duplicate its scoring logic, and the frontend must not call the AI engine directly.
