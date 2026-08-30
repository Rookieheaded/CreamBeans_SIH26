def test_create_claim(client, lost_item, found_item):
    payload = {
        "lost_item_id": lost_item["id"],
        "found_item_id": found_item["id"],
        "message": "This is mine, I can prove it.",
    }
    r = client.post("/claims", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "pending"
    assert body["claimant_id"] == lost_item["reporter_id"]

    # both items should have moved from active -> matched
    lost_after = client.get(f"/items/{lost_item['id']}").json()
    found_after = client.get(f"/items/{found_item['id']}").json()
    assert lost_after["status"] == "matched"
    assert found_after["status"] == "matched"


def test_create_claim_wrong_types_rejected(client, lost_item, found_item):
    # swapped ids: lost_item_id pointing at a found item
    payload = {"lost_item_id": found_item["id"], "found_item_id": lost_item["id"]}
    r = client.post("/claims", json=payload)
    assert r.status_code == 400


def test_create_claim_unknown_item(client, lost_item):
    payload = {"lost_item_id": lost_item["id"], "found_item_id": "nonexistent"}
    r = client.post("/claims", json=payload)
    assert r.status_code == 404
