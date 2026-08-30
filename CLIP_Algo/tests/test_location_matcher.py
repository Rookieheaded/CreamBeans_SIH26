import unittest
from ai.location_matcher import haversine_distance, calculate_location_similarity, calculate_string_location_similarity

class TestLocationMatcher(unittest.TestCase):

    def test_haversine_distance_zero(self):
        # Same point -> 0 km distance
        dist = haversine_distance(12.9716, 77.5946, 12.9716, 77.5946)
        self.assertAlmostEqual(dist, 0.0, places=4)

    def test_haversine_distance_known(self):
        # Distance between Bangalore Central Library (12.9716, 77.5946) and MG Road (12.9750, 77.6080) ~1.5km
        dist = haversine_distance(12.9716, 77.5946, 12.9750, 77.6080)
        self.assertGreater(dist, 1.0)
        self.assertLess(dist, 3.0)

    def test_location_similarity_coordinates_close(self):
        loc1 = {"latitude": 12.9716, "longitude": 77.5946, "location": "Library"}
        loc2 = {"latitude": 12.9720, "longitude": 77.5950, "location": "Library Lawn"}
        score = calculate_location_similarity(loc1, loc2)
        self.assertGreaterEqual(score, 0.85)

    def test_location_similarity_coordinates_far(self):
        loc1 = {"latitude": 12.9716, "longitude": 77.5946, "location": "Campus Library"}
        loc2 = {"latitude": 13.0827, "longitude": 80.2707, "location": "City Center"}  # ~290 km away
        score = calculate_location_similarity(loc1, loc2)
        self.assertLess(score, 0.05)

    def test_location_similarity_string_fallback(self):
        # Missing lat/long, relying on text location
        score_exact = calculate_location_similarity("Central Library", "Central Library")
        self.assertEqual(score_exact, 1.0)

        score_partial = calculate_location_similarity("Central Library", "Library Reading Hall")
        self.assertGreaterEqual(score_partial, 0.5)

    def test_location_similarity_missing_data(self):
        score = calculate_location_similarity({}, {})
        self.assertEqual(score, 0.5)

if __name__ == "__main__":
    unittest.main()
