"""Live Supabase -> FastAPI -> AI -> matches integration test.

Run with:
  SUPABASE_URL=... SUPABASE_SERVICE_KEY=... \
  SUPABASE_TEST_EMAIL=... SUPABASE_TEST_PASSWORD=... \
  python scripts/integration_test_supabase.py

The script deliberately does not create or delete database rows. It authenticates
the configured test user, retrieves one active lost item, fetches active found
candidates, invokes the FastAPI matching endpoint, and verifies that a persisted
match contains finder contact information.

The backend must be running at API_BASE_URL (default http://127.0.0.1:8000).
"""

import os
import sys

import requests


BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
EMAIL = os.getenv("SUPABASE_TEST_EMAIL")
PASSWORD = os.getenv("SUPABASE_TEST_PASSWORD")


def fail(message: str):
    print(f"BLOCKED: {message}")
    raise SystemExit(2)


def main():
    required = ["SUPABASE_URL", "SUPABASE_SERVICE_KEY", "SUPABASE_TEST_EMAIL", "SUPABASE_TEST_PASSWORD"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        fail("missing environment variables: " + ", ".join(missing))

    print("1. Authenticating test user through FastAPI/Supabase Auth...")
    login = requests.post(
        f"{BASE}/auth/login",
        json={"email": EMAIL, "password": PASSWORD},
        timeout=20,
    )
    login.raise_for_status()
    auth = login.json()
    token = auth["access_token"]
    print(f"   OK: authenticated {auth['email']} ({auth['user_id']})")

    headers = {"Authorization": f"Bearer {token}"}

    print("2. Retrieving an active lost item...")
    lost = requests.get(
        f"{BASE}/items",
        params={"type": "lost", "status": "active", "limit": 1},
        headers=headers,
        timeout=20,
    )
    lost.raise_for_status()
    lost_items = lost.json()
    if not lost_items:
        fail("no active lost item exists in Supabase; seed the demo data first")
    lost_item = lost_items[0]
    print(f"   OK: lost item {lost_item['id']}")

    print("3. Retrieving active FOUND items...")
    found = requests.get(
        f"{BASE}/items",
        params={"type": "found", "status": "active", "limit": 500},
        headers=headers,
        timeout=20,
    )
    found.raise_for_status()
    found_items = found.json()
    if not found_items:
        fail("no active found items exist in Supabase; seed the demo data first")
    print(f"   OK: retrieved {len(found_items)} active found item(s)")

    print("4-6. Mapping rows -> AI, calling find_matches(), and persisting matches...")
    matches = requests.get(
        f"{BASE}/items/{lost_item['id']}/matches",
        headers=headers,
        timeout=60,
    )
    matches.raise_for_status()
    body = matches.json()
    ranked = body["matches"]
    if not ranked:
        fail("AI returned zero matches for the seeded lost item")
    top = ranked[0]
    print(f"   OK: top match {top['item_id']} final_score={top['final_score']}")

    print("7-8. Verifying found-item -> users join and contact details...")
    finder = top.get("finder")
    if not finder or not finder.get("name") or not finder.get("email"):
        fail("top match has no finder name/email; reporter_id -> users join failed")
    print(f"   OK: finder={finder['name']} email={finder['email']} phone={finder.get('phone')}")

    print("\nPASS: FastAPI -> Supabase -> AI -> matches -> users flow completed.")
    print({
        "lost_item_id": body["lost_item_id"],
        "found_item_id": top["item_id"],
        "final_score": top["final_score"],
        "finder": finder,
    })


if __name__ == "__main__":
    main()
