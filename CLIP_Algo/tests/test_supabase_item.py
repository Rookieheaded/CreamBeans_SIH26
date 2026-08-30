import unittest
from ai.matching_engine import Item, find_matches

class TestSupabaseItemIntegration(unittest.TestCase):

    def test_supabase_item_structure_conversion(self):
        # Exact Supabase PostgreSQL row shape
        supabase_lost_row = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "reporter_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
            "type": "lost",
            "category": "Electronics",
            "description": "Black Lenovo ThinkPad laptop with university sticker on top lid",
            "image_url": "https://xyz.supabase.co/storage/v1/object/public/item-images/lost_laptop.jpg",
            "location": "Central Library 2nd Floor Reading Room",
            "latitude": 12.971600,
            "longitude": 77.594600,
            "timestamp": "2026-08-29T10:00:00Z",
            "status": "active",
            "embedding": None
        }

        # Convert to Item dataclass
        item_obj = Item.from_dict(supabase_lost_row)

        self.assertEqual(item_obj.id, "550e8400-e29b-41d4-a716-446655440000")
        self.assertEqual(item_obj.reporter_id, "7c9e6679-7425-40de-944b-e07fc1f90ae7")
        self.assertEqual(item_obj.type, "lost")
        self.assertEqual(item_obj.category, "Electronics")
        self.assertEqual(item_obj.description, "Black Lenovo ThinkPad laptop with university sticker on top lid")
        self.assertEqual(item_obj.image_url, "https://xyz.supabase.co/storage/v1/object/public/item-images/lost_laptop.jpg")
        self.assertEqual(item_obj.location, "Central Library 2nd Floor Reading Room")
        self.assertEqual(item_obj.latitude, 12.971600)
        self.assertEqual(item_obj.longitude, 77.594600)
        self.assertEqual(item_obj.timestamp, "2026-08-29T10:00:00Z")
        self.assertEqual(item_obj.status, "active")

    def test_find_matches_with_supabase_dictionary_input(self):
        supabase_lost_row = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "reporter_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
            "type": "lost",
            "category": "Electronics",
            "description": "Black Lenovo laptop with stickers",
            "image_url": None,  # Test missing image fallback
            "location": "Central Library",
            "latitude": 12.9716,
            "longitude": 77.5946,
            "timestamp": "2026-08-29T10:00:00Z",
            "status": "active",
            "embedding": None
        }

        supabase_found_rows = [
            {
                "id": "660e8400-e29b-41d4-a716-446655441111",
                "reporter_id": "8d9e6679-7425-40de-944b-e07fc1f90ae8",
                "type": "found",
                "category": "Electronics",
                "description": "Dark ThinkPad laptop found near library entrance",
                "image_url": None,
                "location": "Library Lawn",
                "latitude": 12.9718,
                "longitude": 77.5948,
                "timestamp": "2026-08-29T10:30:00Z",
                "status": "active",
                "embedding": None
            }
        ]

        matches = find_matches(supabase_lost_row, supabase_found_rows)
        self.assertEqual(len(matches), 1)

        match = matches[0]
        self.assertEqual(match["item_id"], "660e8400-e29b-41d4-a716-446655441111")
        self.assertIn("image_score", match)
        self.assertIn("text_score", match)
        self.assertIn("location_score", match)
        self.assertIn("time_score", match)
        self.assertIn("final_score", match)
        self.assertGreaterEqual(match["final_score"], 0.70)

if __name__ == "__main__":
    unittest.main()
