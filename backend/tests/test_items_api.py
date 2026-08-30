def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_report_lost_item(client):
    payload = {
        "category": "electronics",
        "description": "silver iPhone with cracked screen",
        "location": "Canteen",
        "reporter": {"name": "Dev", "email": "dev@example.com"},
    }
    r = client.post("/items/lost", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["type"] == "lost"
    assert body["status"] == "active"
    assert body["description"] == payload["description"]


def test_report_reuses_existing_user(client):
    payload = {
        "description": "item one",
        "reporter": {"name": "Dev", "email": "dev@example.com"},
    }
    r1 = client.post("/items/lost", json=payload)
    payload2 = dict(payload, description="item two")
    r2 = client.post("/items/lost", json=payload2)
    assert r1.json()["reporter_id"] == r2.json()["reporter_id"]


def test_get_item_404(client):
    r = client.get("/items/does-not-exist")
    assert r.status_code == 404


def test_get_item(client, lost_item):
    r = client.get(f"/items/{lost_item['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == lost_item["id"]


def test_list_items_filters(client, lost_item, found_item):
    r = client.get("/items", params={"type": "lost"})
    ids = [i["id"] for i in r.json()]
    assert lost_item["id"] in ids
    assert found_item["id"] not in ids


def test_list_items_invalid_type(client):
    r = client.get("/items", params={"type": "bogus"})
    assert r.status_code == 400


def test_matches_endpoint_returns_ranked_list(client, lost_item, found_item):
    r = client.get(f"/items/{lost_item['id']}/matches")
    assert r.status_code == 200
    body = r.json()
    assert body["lost_item_id"] == lost_item["id"]
    assert len(body["matches"]) == 1
    match = body["matches"][0]
    assert match["item_id"] == found_item["id"]
    assert "final_score" in match
    assert match["finder"]["email"] == "rahul@example.com"


def test_matches_endpoint_rejects_found_item(client, found_item):
    r = client.get(f"/items/{found_item['id']}/matches")
    assert r.status_code == 400


def test_matches_endpoint_404_for_unknown_item(client):
    r = client.get("/items/unknown-id/matches")
    assert r.status_code == 404


def test_status_transition_valid(client, lost_item):
    r = client.patch(f"/items/{lost_item['id']}/status", json={"status": "matched"})
    assert r.status_code == 200
    assert r.json()["status"] == "matched"


def test_status_transition_invalid(client, lost_item):
    # active -> returned directly is not allowed
    r = client.patch(f"/items/{lost_item['id']}/status", json={"status": "returned"})
    assert r.status_code == 409


def test_status_transition_idempotent(client, lost_item):
    r = client.patch(f"/items/{lost_item['id']}/status", json={"status": "active"})
    assert r.status_code == 200
    assert r.json()["status"] == "active"


def test_list_items_pagination(client):
    for i in range(5):
        client.post(
            "/items/lost",
            json={
                "description": f"item {i}",
                "reporter": {"name": "P", "email": f"p{i}@example.com"},
            },
        )
    page1 = client.get("/items", params={"limit": 2, "offset": 0}).json()
    page2 = client.get("/items", params={"limit": 2, "offset": 2}).json()
    assert len(page1) == 2
    assert len(page2) == 2
    assert {p["id"] for p in page1}.isdisjoint({p["id"] for p in page2})


def test_list_items_rejects_bad_pagination(client):
    r = client.get("/items", params={"limit": 0})
    assert r.status_code == 422  # FastAPI's own ge=1 validation


def test_matches_uses_batched_finder_lookup(client, lost_item, found_item, monkeypatch):
    """Guards against regressing back to N+1: get_user() must not be
    called during the match workflow, only the batched get_users()."""
    from backend.database.in_memory import InMemoryRepository

    repo = InMemoryRepository.instance()
    calls = {"get_user": 0, "get_users": 0}

    orig_get_user = repo.get_user
    orig_get_users = repo.get_users

    def counting_get_user(*a, **kw):
        calls["get_user"] += 1
        return orig_get_user(*a, **kw)

    def counting_get_users(*a, **kw):
        calls["get_users"] += 1
        return orig_get_users(*a, **kw)

    monkeypatch.setattr(repo, "get_user", counting_get_user)
    monkeypatch.setattr(repo, "get_users", counting_get_users)

    r = client.get(f"/items/{lost_item['id']}/matches")
    assert r.status_code == 200
    assert calls["get_user"] == 0
    assert calls["get_users"] == 1


def test_display_endpoints_exclude_embedding(client):
    from backend.database.in_memory import InMemoryRepository

    repo = InMemoryRepository.instance()
    row = repo.create_item(
        {
            "reporter_id": "r1",
            "type": "lost",
            "description": "x",
            "embedding": [0.1, 0.2, 0.3],
        }
    )
    fetched = repo.get_item(row["id"])
    assert "embedding" not in fetched
    fetched_full = repo.get_item(row["id"], include_embedding=True)
    assert fetched_full["embedding"] == [0.1, 0.2, 0.3]
