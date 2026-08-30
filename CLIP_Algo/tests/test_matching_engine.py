import unittest
import os
from PIL import Image

from ai.matching_engine import MatchingEngine, find_matches, Item

class TestMatchingEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create test sample images
        cls.img_bag1 = "test_bag1.jpg"
        cls.img_bag2 = "test_bag2.jpg"
        cls.img_wallet = "test_wallet.jpg"

        Image.new("RGB", (200, 200), color=(40, 40, 40)).save(cls.img_bag1)    # Black bag
        Image.new("RGB", (200, 200), color=(50, 50, 55)).save(cls.img_bag2)    # Dark grey bag
        Image.new("RGB", (200, 200), color=(140, 70, 30)).save(cls.img_wallet) # Brown wallet

    @classmethod
    def tearDownClass(cls):
        for f in [cls.img_bag1, cls.img_bag2, cls.img_wallet]:
            if os.path.exists(f):
                os.remove(f)

    def test_all_sih_test_cases(self):
        engine = MatchingEngine()

        lost_backpack = {
            "id": "L001",
            "category": "Bags",
            "description": "Black backpack with laptop compartment",
            "image_url": self.img_bag1,
            "location": "Central Library Reading Hall",
            "latitude": 12.9716,
            "longitude": 77.5946,
            "timestamp": "2026-08-29T10:00:00Z"
        }

        candidates = [
            # 1. Obvious Match (F001)
            {
                "id": "F001_ObviousMatch",
                "category": "Bags",
                "description": "Dark Lenovo bag",
                "image_url": self.img_bag2,
                "location": "Library Lawn near main door",
                "latitude": 12.9720,
                "longitude": 77.5950,
                "timestamp": "2026-08-29T11:00:00Z"
            },
            # 2. Similar Item but Wrong Location (F002)
            {
                "id": "F002_WrongLocation",
                "category": "Bags",
                "description": "Black laptop backpack",
                "image_url": self.img_bag2,
                "location": "Off-Campus Railway Station",
                "latitude": 13.0827,
                "longitude": 80.2707,  # Far city (~290 km)
                "timestamp": "2026-08-29T10:30:00Z"
            },
            # 3. Similar Description but Different Object (F003)
            {
                "id": "F003_DifferentObject",
                "category": "Bags",
                "description": "Black bag item",
                "image_url": self.img_wallet,  # Wallet image instead of bag
                "location": "Central Library Reading Hall",
                "latitude": 12.9716,
                "longitude": 77.5946,
                "timestamp": "2026-08-29T10:15:00Z"
            },
            # 4. Completely Unrelated Item (F004)
            {
                "id": "F004_UnrelatedItem",
                "category": "Wallets",
                "description": "Brown leather wallet with currency notes",
                "image_url": self.img_wallet,
                "location": "Sports Complex Gymnasium",
                "latitude": 12.9800,
                "longitude": 77.6100,
                "timestamp": "2026-08-25T10:00:00Z"
            },
            # 5. Missing Image candidate (F005)
            {
                "id": "F005_MissingImage",
                "category": "Bags",
                "description": "Black Lenovo backpack with padded straps",
                "image_url": None,
                "location": "Library",
                "latitude": 12.9718,
                "longitude": 77.5948,
                "timestamp": "2026-08-29T10:45:00Z"
            },
            # 6. Sparse Description candidate (F006)
            {
                "id": "F006_SparseDescription",
                "category": "Bags",
                "description": "Bag",
                "image_url": self.img_bag2,
                "location": "Library",
                "latitude": 12.9716,
                "longitude": 77.5946,
                "timestamp": "2026-08-29T10:05:00Z"
            }
        ]

        matches = find_matches(lost_backpack, candidates)
        self.assertEqual(len(matches), len(candidates))

        match_by_id = {m["item_id"]: m for m in matches}

        # Verify all fields exist and are within [0.0, 1.0]
        for m in matches:
            self.assertIn("item_id", m)
            self.assertIn("image_score", m)
            self.assertIn("text_score", m)
            self.assertIn("location_score", m)
            self.assertIn("time_score", m)
            self.assertIn("final_score", m)

            for key in ["image_score", "text_score", "location_score", "time_score", "final_score"]:
                self.assertGreaterEqual(m[key], 0.0)
                self.assertLessEqual(m[key], 1.0)

        # Assertion 1: Obvious match (F001) / top candidates should be top ranked
        top_match = matches[0]
        self.assertIn(top_match["item_id"], ["F001_ObviousMatch", "F005_MissingImage", "F006_SparseDescription"])
        self.assertGreaterEqual(match_by_id["F001_ObviousMatch"]["final_score"], 0.70)

        # Assertion 2: Wrong location (F002) should have high identity score but low location score
        wrong_loc = match_by_id["F002_WrongLocation"]
        self.assertLess(wrong_loc["location_score"], 0.10)
        self.assertGreater(wrong_loc["final_score"], 0.30)

        # Assertion 3: Completely unrelated item (F004) should have lower final score
        unrelated = match_by_id["F004_UnrelatedItem"]
        self.assertLess(unrelated["final_score"], match_by_id["F001_ObviousMatch"]["final_score"])

        # Assertion 4: Missing image (F005) handles scoring gracefully without failing
        missing_img = match_by_id["F005_MissingImage"]
        self.assertGreaterEqual(missing_img["text_score"], 0.70)
        self.assertGreaterEqual(missing_img["final_score"], 0.60)

if __name__ == "__main__":
    unittest.main()
