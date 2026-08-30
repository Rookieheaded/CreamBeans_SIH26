import unittest
import os
import io
from unittest.mock import patch, MagicMock
from PIL import Image
import torch
from ai.clip_encoder import CLIPEncoder

class TestCLIPEncoder(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.encoder = CLIPEncoder.get_instance()
        
        # Create temporary dummy test images
        cls.img1_path = "test_img1.jpg"
        cls.img2_path = "test_img2.jpg"

        img1 = Image.new("RGB", (100, 100), color=(255, 0, 0))  # Red image
        img2 = Image.new("RGB", (100, 100), color=(250, 5, 5))  # Almost red image
        img1.save(cls.img1_path)
        img2.save(cls.img2_path)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.img1_path):
            os.remove(cls.img1_path)
        if os.path.exists(cls.img2_path):
            os.remove(cls.img2_path)

    def test_encode_text_shape_and_norm(self):
        emb = self.encoder.encode_text("Black laptop bag")
        self.assertEqual(emb.shape, (1, 512))
        norm = torch.norm(emb, p=2, dim=-1).item()
        self.assertAlmostEqual(norm, 1.0, places=4)

    def test_encode_image_shape_and_norm(self):
        emb = self.encoder.encode_image(self.img1_path)
        self.assertEqual(emb.shape, (1, 512))
        norm = torch.norm(emb, p=2, dim=-1).item()
        self.assertAlmostEqual(norm, 1.0, places=4)

    def test_text_text_semantic_similarity(self):
        # Similar items
        s_high = self.encoder.calculate_text_text_similarity(
            "Black Lenovo laptop bag", "Dark Lenovo backpack"
        )
        # Unrelated items
        s_low = self.encoder.calculate_text_text_similarity(
            "Black Lenovo laptop bag", "Keychain with 3 house keys"
        )
        self.assertGreater(s_high, s_low)
        self.assertGreaterEqual(s_high, 0.70)

    def test_text_image_cross_modal_similarity(self):
        s_match = self.encoder.calculate_text_image_similarity("Red square", self.img1_path)
        self.assertGreaterEqual(s_match, 0.50)

    @patch("urllib.request.urlopen")
    def test_http_image_url_fetching(self, mock_urlopen):
        # Create image bytes
        buf = io.BytesIO()
        Image.new("RGB", (100, 100), color=(0, 255, 0)).save(buf, format="JPEG")
        img_bytes = buf.getvalue()

        # Mock urlopen response
        mock_response = MagicMock()
        mock_response.read.return_value = img_bytes
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        # Call encode_image with HTTP URL
        http_url = "https://xyz.supabase.co/storage/v1/object/public/item-images/test_green.jpg"
        emb = self.encoder.encode_image(http_url)

        self.assertEqual(emb.shape, (1, 512))
        norm = torch.norm(emb, p=2, dim=-1).item()
        self.assertAlmostEqual(norm, 1.0, places=4)

    def test_invalid_http_url_graceful_fallback(self):
        invalid_url = "https://invalid-nonexistent-domain-12345.com/broken_photo.jpg"
        score = self.encoder.calculate_image_image_similarity(self.img1_path, invalid_url)
        # Should gracefully return 0.0 without crashing
        self.assertEqual(score, 0.0)

if __name__ == "__main__":
    unittest.main()
