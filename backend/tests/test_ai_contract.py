"""
Verifies the (placeholder) ai package honors the contract the backend
relies on. When the real ai package replaces this one, these same tests
should still pass unchanged against it.
"""

from ai import find_matches, Item


def test_find_matches_accepts_dicts():
    lost = {"id": "L1", "type": "lost", "description": "black wallet", "location": "Gate 2"}
    found = [{"id": "F1", "type": "found", "description": "black leather wallet", "location": "Gate 2"}]
    results = find_matches(lost, found)
    assert isinstance(results, list)
    assert results[0]["item_id"] == "F1"


def test_find_matches_accepts_item_objects():
    lost = Item(id="L1", type="lost", description="black wallet")
    found = [Item(id="F1", type="found", description="black wallet")]
    results = find_matches(lost, found)
    assert results[0]["item_id"] == "F1"


def test_result_shape_and_score_range():
    lost = {"id": "L1", "type": "lost", "description": "red umbrella", "location": "Block A"}
    found = [{"id": "F1", "type": "found", "description": "red umbrella", "location": "Block A"}]
    result = find_matches(lost, found)[0]

    for key in ("item_id", "image_score", "text_score", "location_score", "time_score", "final_score"):
        assert key in result

    for key in ("image_score", "text_score", "location_score", "time_score", "final_score"):
        assert 0.0 <= result[key] <= 1.0


def test_results_sorted_descending_by_final_score():
    lost = {"id": "L1", "type": "lost", "description": "blue notebook with dog sticker"}
    found = [
        {"id": "F1", "type": "found", "description": "completely unrelated red shoe"},
        {"id": "F2", "type": "found", "description": "blue notebook with dog sticker"},
    ]
    results = find_matches(lost, found)
    scores = [r["final_score"] for r in results]
    assert scores == sorted(scores, reverse=True)
    assert results[0]["item_id"] == "F2"


def test_empty_candidates_returns_empty_list():
    lost = {"id": "L1", "type": "lost", "description": "x"}
    assert find_matches(lost, []) == []
