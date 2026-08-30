-- SUGGESTED indexes for the existing schema.
--
-- These are NOT applied automatically by the backend — per the project
-- rules, schema changes need Person 5/6 sign-off. This file is a proposal
-- to hand them, not a migration that runs.
--
-- Why these specifically: they match the query patterns the backend
-- actually issues (see backend/database/repository.py).

-- users.email is looked up on every POST /items/lost|found (get_or_create_user)
create unique index if not exists idx_users_email on users (email);

-- items are filtered by (type, status) together on:
--   - GET /items?type=&status=
--   - the found-item candidate fetch inside GET /items/{id}/matches
create index if not exists idx_items_type_status on items (type, status);

-- items are always ordered by created_at desc for listing/pagination
create index if not exists idx_items_created_at on items (created_at desc);

-- matches are looked up by lost_item_id (e.g. "show past match history
-- for this lost item", if that's ever added as an endpoint)
create index if not exists idx_matches_lost_item_id on matches (lost_item_id);
create index if not exists idx_matches_found_item_id on matches (found_item_id);

-- claims (proposed table, see repository.py docstring) is looked up by
-- both item ids from the admin/security side
create index if not exists idx_claims_lost_item_id on claims (lost_item_id);
create index if not exists idx_claims_found_item_id on claims (found_item_id);
