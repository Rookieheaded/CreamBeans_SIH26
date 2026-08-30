import unittest
from datetime import datetime, timezone, timedelta
from ai.time_matcher import parse_timestamp, calculate_time_similarity

class TestTimeMatcher(unittest.TestCase):

    def test_parse_timestamp_iso_string(self):
        dt = parse_timestamp("2026-08-29T10:00:00Z")
        self.assertIsNotNone(dt)
        self.assertEqual(dt.year, 2026)
        self.assertEqual(dt.month, 8)
        self.assertEqual(dt.day, 29)

    def test_time_similarity_identical(self):
        t1 = "2026-08-29T10:00:00Z"
        t2 = "2026-08-29T10:00:00Z"
        score = calculate_time_similarity(t1, t2)
        self.assertAlmostEqual(score, 1.0, places=4)

    def test_time_similarity_decay_48_hours(self):
        t1 = "2026-08-29T10:00:00Z"
        t2 = "2026-08-31T10:00:00Z"  # Exactly 48h later
        score = calculate_time_similarity(t1, t2, half_decay_hours=48.0)
        self.assertAlmostEqual(score, 0.50, places=2)

    def test_time_similarity_decay_far(self):
        t1 = "2026-08-01T10:00:00Z"
        t2 = "2026-08-29T10:00:00Z"  # 28 days difference
        score = calculate_time_similarity(t1, t2)
        self.assertLess(score, 0.05)

    def test_time_similarity_missing_or_invalid(self):
        score = calculate_time_similarity(None, "2026-08-29T10:00:00Z")
        self.assertEqual(score, 0.5)

        score_invalid = calculate_time_similarity("invalid-date-string", "2026-08-29T10:00:00Z")
        self.assertEqual(score_invalid, 0.5)

if __name__ == "__main__":
    unittest.main()
