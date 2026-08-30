# Cream Beans — Backend (Person 4: Backend/API Engineer)

FastAPI backend for the SIH 2026 Campus Lost & Found Intelligence System.
Bridges: **Frontend → FastAPI → Supabase → AI matching engine → Supabase → Frontend**.

## What's here

```
backend/
├── main.py               # FastAPI app, wires routers together
├── config.py              # env-driven settings
├── api/                   # HTTP routes only — no business logic
│   ├── health.py
│   ├── items.py
│   └── claims.py
├── services/               # business logic
│   ├── item_service.py     # create/get/list items, status transitions
│   ├── match_service.py    # THE bridge to find_matches()
│   └── claim_service.py    # minimal claim workflow
├── models/
│   └── schemas.py          # Pydantic request/response models
├── database/
│   ├── repository.py       # Repository interface + SupabaseRepository
│   ├── in_memory.py         # in-memory stand-in for local dev/tests
│   └── supabase_client.py   # Supabase client bootstrap
└── utils/
    └── mapping.py           # DB row <-> AI Item field mapping (1:1, no renames)

ai/                          # PLACEHOLDER for the real AI package (see below)
tests/                       # pytest suite, runs against the in-memory DB
```

## Running it

```bash
pip install -r backend/requirements.txt
cp .env.example .env          # leave SUPABASE_* blank to use the in-memory dev DB
uvicorn backend.main:app --reload
```

Open http://127.0.0.1:8000/docs for interactive API docs.

## Running the tests

```bash
pip install -r backend/requirements.txt
pytest tests/ -v
```

The test suite runs entirely against an in-process in-memory database
(`USE_IN_MEMORY_DB=true`), so it needs no live Supabase project or network
access. 21 tests cover: the AI contract shape, item CRUD, the full match
workflow, status-transition rules, and the claims workflow.

## ⚠️ About the `ai/` folder in this deliverable

The engineering brief states the AI/ML matching engine **already exists**
in the real repository and exposes:

```python
from ai import find_matches, MatchingEngine, Item
```

That real package was **not included** in what was handed to me for this
backend task — only the interface contract was. So `ai/` here is a
**placeholder implementation of that exact contract** (same function
name, same `Item` fields, same five output score fields, same 0.0–1.0
range, same descending sort by `final_score`), built so the backend is
runnable and independently testable right now, per the brief's own
"Development Strategy" section:

> Initially implement the backend with mock AI results if necessary. Then
> replace the mock implementation with `from ai import find_matches`.

**To integrate the real engine:** delete/replace the `ai/` directory here
with the real one from the main repo. **No backend code needs to
change** — `backend/services/match_service.py` only ever imports
`find_matches` from `ai`, exactly as specified. That's the whole point of
the black-box boundary.

Do not mistake `ai/engine.py`'s heuristics (word overlap, haversine
distance, time decay) for real matching logic — they exist only to
produce plausible-shaped scores for local testing.

## Performance optimizations applied

1. **Fixed N+1 query in the match workflow.** `GET /items/{id}/matches`
   previously called `get_user()` once per match result to fetch finder
   contact info. It now calls a new `Repository.get_users(ids)` batch
   method once, via a single `WHERE id IN (...)` query
   (`backend/services/match_service.py`). A regression test
   (`test_matches_uses_batched_finder_lookup`) asserts `get_user()` is
   never called on this path.
2. **Column-scoped reads.** `GET /items` and `GET /items/{id}` no longer
   pull the `embedding` column — CLIP vectors are large and nothing in
   the API response (`ItemOut`) uses them. Only `match_service.py`, which
   actually hands rows to `find_matches()`, requests the full row via
   `include_embedding=True`. Implemented as an explicit repository
   parameter rather than a global default, so it's obvious at each call
   site whether the embedding is needed.
3. **Pagination on `GET /items`.** Added `limit`/`offset` query params
   (default 50, hard cap 500) instead of an unbounded/fixed-100 fetch, so
   response size stays predictable as the items table grows.
4. **Suggested indexes** for the schema owner in
   `database/suggested_indexes.sql` — matching the actual query patterns
   above (`(type, status)`, `created_at desc`, `email`, foreign keys on
   `matches`/`claims`). Not applied automatically; schema changes still
   need Person 5/6 sign-off per the project rules.

## Design decisions worth flagging to the tech lead

1. **`claims` table**: the documented schema (`users`, `items`,
   `matches`) doesn't include a `claims` table, but `POST /claims` is a
   required endpoint. I added a minimal `claims` table assumption
   (documented in `backend/database/repository.py`) — this needs a
   migration and sign-off from Person 5/6 before merging, per the "STOP
   and coordinate" rule in the brief.
2. **Claim → status side effect**: creating a claim also bumps both the
   lost and found item from `active` to `matched` (using the same status
   machine as `PATCH /items/{id}/status`, not a second one). Flagging in
   case the intended demo flow expects claims to be purely informational
   until an admin acts.
3. **In-memory DB for dev/test**: `USE_IN_MEMORY_DB` (auto-on when
   Supabase credentials are absent) lets this be developed and tested
   without a live Supabase project. It is a straight swap for
   `SupabaseRepository` — same `Repository` interface — once real
   credentials are supplied.

## API surface

| Method | Path                     | Notes                                     |
|--------|--------------------------|--------------------------------------------|
| POST   | `/auth/login` | Supabase Auth email/password login |
| GET    | `/health`                | Reports AI/DB reachability                 |
| POST   | `/items/lost`            | Create-or-reuse reporter, store lost item  |
| POST   | `/items/found`           | Create-or-reuse reporter, store found item |
| GET    | `/items`                 | Filter by `type` / `status`                |
| GET    | `/items/{id}`            | 404 if not found                           |
| GET    | `/items/{id}/matches`    | Runs `find_matches()`, persists, joins finder info |
| PATCH  | `/items/{id}/status`     | Enforces `active → matched → returned`     |
| POST   | `/claims`                | Minimal claim record, no verification step |


## Supabase/Auth integration

When `USE_IN_MEMORY_DB=false`, `/auth/login` delegates email/password
authentication to Supabase Auth and returns its access token. The item and
matching routes require `Authorization: Bearer <access_token>` and validate
the token through Supabase Auth before executing the existing repository /
AI workflow.

The AI boundary is unchanged: `backend/services/match_service.py` still
does only `from ai import find_matches` and passes mapped item records to it.
Auth/contact details never enter the AI module.

For the live integration test, configure `SUPABASE_URL`,
`SUPABASE_SERVICE_KEY`, and a Supabase Auth test user's credentials in the
environment. Do not commit credentials.


## Live Supabase integration test

Start FastAPI with `USE_IN_MEMORY_DB=false` and the Supabase URL/service key,
then set `SUPABASE_TEST_EMAIL` and `SUPABASE_TEST_PASSWORD` for a temporary
test account. Run:

```bash
python scripts/integration_test_supabase.py
```

The script does not create/delete data. It authenticates the test user,
retrieves seeded active lost/found records, invokes `GET /items/{id}/matches`,
and verifies the returned finder contact join. A non-zero exit means the live
integration could not be completed.


## Registration fix
The registration endpoint safely reuses or updates a public `users` profile when a Supabase trigger has already created it, avoiding false duplicate-email errors.
