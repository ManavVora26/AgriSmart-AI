"""
AgriSmart AI — Disease Detection Service
Handles model loading and inference for crop disease classification.

Two modes (set via MODEL_MODE env var):
  - "mock" : Returns realistic-looking dummy predictions (no GPU/model needed)
  - "real" : Loads EfficientNet-B0 (timm) from MODEL_WEIGHTS_PATH and runs actual inference

Member 3 (ML) should drop the trained .pt weights file into model_weights/
and set MODEL_MODE=real in .env to activate real inference.
"""

import os
import io
import random
import logging
from pathlib import Path

from PIL import Image
import numpy as np
from dotenv import load_dotenv

from utils.label_map import INDEX_TO_LABEL, get_label_info, NUM_CLASSES

load_dotenv()

logger = logging.getLogger(__name__)

MODEL_MODE = os.getenv("MODEL_MODE", "mock").lower()
MODEL_WEIGHTS_PATH = os.getenv("MODEL_WEIGHTS_PATH", "model_weights/disease_model.pt")

# Global model holder
_model = None
_transform = None


def _load_real_model():
    """Load EfficientNet-B0 with trained weights from disk."""
    global _model, _transform
    try:
        import torch
        import timm
        from torchvision import transforms

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        weights_path = Path(MODEL_WEIGHTS_PATH)

        if not weights_path.exists():
            raise FileNotFoundError(
                f"Model weights not found at '{weights_path}'. "
                "Set MODEL_MODE=mock in .env or place weights file at the expected path."
            )

        logger.info(f"Loading real model from {weights_path} on {device}...")
        model = timm.create_model("efficientnet_b0", pretrained=False, num_classes=NUM_CLASSES)
        checkpoint = torch.load(weights_path, map_location=device)

        # Support both raw state_dict and {model_state_dict: ...} checkpoint formats
        state_dict = checkpoint.get("model_state_dict", checkpoint)
        model.load_state_dict(state_dict)
        model.to(device)
        model.eval()

        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
        ])

        _model = (model, device)
        _transform = transform
        logger.info("Real model loaded successfully.")

    except ImportError as e:
        logger.error(f"torch/timm not installed: {e}. Falling back to mock mode.")
        return False
    return True


def load_model():
    """Initialize the model at server startup."""
    global _model
    if MODEL_MODE == "real":
        success = _load_real_model()
        if not success:
            logger.warning("Falling back to mock model.")
    else:
        logger.info("Running in MOCK mode — no model weights needed.")


def _mock_predict(image_bytes: bytes) -> dict:
    """
    Stub prediction: returns a deterministic-ish result seeded by image content.
    Uses image pixel statistics for reproducibility (same image → same result).
    """
    # Use image statistics as a pseudo-seed for determinism
    try:
        if image_bytes and len(image_bytes) > 0:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((64, 64))
            arr = np.array(img)
            seed = int(arr.mean() * 1000) % (NUM_CLASSES * 100)
        else:
            seed = 42
    except Exception:
        seed = sum(image_bytes) if image_bytes else 42

    rng = random.Random(seed)
    class_idx = rng.randint(0, NUM_CLASSES - 1)
    label = INDEX_TO_LABEL[class_idx]

    # Build a realistic softmax-like confidence distribution
    raw = [rng.random() for _ in range(NUM_CLASSES)]
    raw[class_idx] *= 5  # boost chosen class
    total = sum(raw)
    probs = [r / total for r in raw]
    confidence = probs[class_idx]

    return {
        "label": label,
        "confidence": round(confidence, 4),
        "all_probabilities": {INDEX_TO_LABEL[i]: round(probs[i], 4) for i in range(NUM_CLASSES)},
    }


def _real_predict(image_bytes: bytes) -> dict:
    """Run actual EfficientNet-B0 inference on the uploaded image bytes."""
    import torch
    import torch.nn.functional as F

    model, device = _model
    transform = _transform

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    tensor = transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(tensor)
        probs = F.softmax(logits, dim=1)[0]
        confidence, class_idx = probs.max(dim=0)

    label = INDEX_TO_LABEL[int(class_idx)]
    return {
        "label": label,
        "confidence": round(float(confidence), 4),
        "all_probabilities": {INDEX_TO_LABEL[i]: round(float(probs[i]), 4) for i in range(NUM_CLASSES)},
    }


def predict_disease(image_bytes: bytes) -> dict:
    """
    Main entry point for disease prediction.
    Returns: {label, confidence, display_name, precaution, is_healthy}
    """
    if MODEL_MODE == "real" and _model is not None:
        raw = _real_predict(image_bytes)
    else:
        raw = _mock_predict(image_bytes)

    info = get_label_info(raw["label"])
    return {
        "label": raw["label"],
        "display_name": info["display_name"],
        "confidence": raw["confidence"],
        "is_healthy": info["is_healthy"],
        "precaution": info["precaution"],
        "model_mode": MODEL_MODE if (MODEL_MODE == "real" and _model) else "mock",
    }
