import io
import base64
import logging
import urllib.request
from typing import Union, List, Optional
from PIL import Image
import torch
import torch.nn.functional as F
from transformers import CLIPProcessor, CLIPModel

logger = logging.getLogger(__name__)

class CLIPEncoder:
    """
    Multi-modal encoder using Hugging Face Transformers pre-trained CLIP.
    Computes normalized embeddings and similarity scores for text and images.
    """
    _instance: Optional["CLIPEncoder"] = None

    def __init__(self, model_name: str = "openai/clip-vit-base-patch32", device: Optional[str] = None):
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        logger.info(f"Loading CLIP model '{model_name}' on device: {self.device}")
        self.model_name = model_name
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.model.eval()

    @classmethod
    def get_instance(cls, model_name: str = "openai/clip-vit-base-patch32") -> "CLIPEncoder":
        """Singleton helper to avoid re-loading weights repeatedly."""
        if cls._instance is None:
            cls._instance = cls(model_name=model_name)
        return cls._instance

    def _prepare_image(self, image_input: Union[str, Image.Image, bytes]) -> Image.Image:
        """Helper to convert various image input formats into a RGB PIL Image."""
        if isinstance(image_input, Image.Image):
            return image_input.convert("RGB")
        
        if isinstance(image_input, bytes):
            return Image.open(io.BytesIO(image_input)).convert("RGB")
        
        if isinstance(image_input, str):
            # Check if base64 data URI or raw base64
            if image_input.startswith("data:image"):
                base64_data = image_input.split(",")[1]
                image_bytes = base64.b64decode(base64_data)
                return Image.open(io.BytesIO(image_bytes)).convert("RGB")
            
            # Check if HTTP/HTTPS URL
            if image_input.startswith(("http://", "https://")):
                try:
                    req = urllib.request.Request(
                        image_input,
                        headers={"User-Agent": "CreamBeans-AI/1.0"}
                    )
                    with urllib.request.urlopen(req, timeout=10.0) as response:
                        img_bytes = response.read()
                        return Image.open(io.BytesIO(img_bytes)).convert("RGB")
                except Exception as e:
                    logger.warning(f"Failed to fetch image from HTTP/HTTPS URL '{image_input}': {e}")
                    raise ValueError(f"Could not load image from URL: {image_input}") from e

            # Check if file path
            try:
                return Image.open(image_input).convert("RGB")
            except Exception as e:
                raise ValueError(f"Could not load image from string/path: {image_input[:50]}...") from e

        raise TypeError(f"Unsupported image input type: {type(image_input)}")

    def encode_text(self, text: Union[str, List[str]]) -> torch.Tensor:
        """
        Encode text string(s) into L2-normalized 512-dim embedding tensor(s).
        """
        if isinstance(text, str):
            texts = [text]
        else:
            texts = text

        if not texts or all(not t.strip() for t in texts):
            dim = self.model.config.projection_dim if hasattr(self.model.config, "projection_dim") else 512
            return torch.zeros((len(texts), dim), device=self.device)

        inputs = self.processor(text=texts, return_tensors="pt", padding=True, truncation=True).to(self.device)
        with torch.no_grad():
            outputs = self.model.get_text_features(**inputs)
            if not isinstance(outputs, torch.Tensor):
                if hasattr(outputs, "text_embeds"):
                    text_features = outputs.text_embeds
                elif hasattr(outputs, "pooler_output"):
                    text_features = outputs.pooler_output
                else:
                    text_features = outputs[0]
            else:
                text_features = outputs
            
            text_features = F.normalize(text_features, p=2, dim=-1)
        return text_features

    def encode_image(self, image_input: Union[str, Image.Image, bytes, List[Union[str, Image.Image, bytes]]]) -> torch.Tensor:
        """
        Encode PIL image(s) or image path(s) into L2-normalized embedding tensor(s).
        """
        if not isinstance(image_input, list):
            inputs_list = [image_input]
        else:
            inputs_list = image_input

        pil_images = [self._prepare_image(img) for img in inputs_list]
        inputs = self.processor(images=pil_images, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model.get_image_features(**inputs)
            if not isinstance(outputs, torch.Tensor):
                if hasattr(outputs, "image_embeds"):
                    image_features = outputs.image_embeds
                elif hasattr(outputs, "pooler_output"):
                    image_features = outputs.pooler_output
                else:
                    image_features = outputs[0]
            else:
                image_features = outputs

            image_features = F.normalize(image_features, p=2, dim=-1)
        return image_features

    @staticmethod
    def compute_cosine_similarity(vec1: torch.Tensor, vec2: torch.Tensor) -> float:
        """
        Computes cosine similarity between two normalized vectors and maps to [0.0, 1.0].
        """
        if vec1 is None or vec2 is None:
            return 0.0
        
        if vec1.ndim == 1:
            vec1 = vec1.unsqueeze(0)
        if vec2.ndim == 1:
            vec2 = vec2.unsqueeze(0)

        # Dot product of normalized vectors = Cosine Similarity (-1.0 to 1.0)
        raw_cos = torch.mm(vec1, vec2.T).item()
        
        # Rescale raw cosine similarity [-1, 1] -> [0, 1]
        normalized_score = (raw_cos + 1.0) / 2.0
        return max(0.0, min(1.0, float(normalized_score)))

    def calculate_text_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity score [0.0, 1.0] between two texts."""
        if not text1 or not text2:
            return 0.0
        try:
            t1_emb = self.encode_text(text1)
            t2_emb = self.encode_text(text2)
            return self.compute_cosine_similarity(t1_emb, t2_emb)
        except Exception as e:
            logger.warning(f"Text similarity calculation failed: {e}")
            return 0.0

    def calculate_image_image_similarity(self, img1: Union[str, Image.Image, bytes], img2: Union[str, Image.Image, bytes]) -> float:
        """Calculate visual similarity score [0.0, 1.0] between two images."""
        if img1 is None or img2 is None:
            return 0.0
        try:
            i1_emb = self.encode_image(img1)
            i2_emb = self.encode_image(img2)
            return self.compute_cosine_similarity(i1_emb, i2_emb)
        except Exception as e:
            logger.warning(f"Image-image similarity calculation failed: {e}")
            return 0.0

    def calculate_text_image_similarity(self, text: str, img: Union[str, Image.Image, bytes]) -> float:
        """Calculate cross-modal similarity score [0.0, 1.0] between text and image."""
        if not text or img is None:
            return 0.0
        try:
            t_emb = self.encode_text(text)
            i_emb = self.encode_image(img)
            return self.compute_cosine_similarity(t_emb, i_emb)
        except Exception as e:
            logger.warning(f"Text-image similarity calculation failed: {e}")
            return 0.0
