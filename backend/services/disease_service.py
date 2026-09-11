"""
AgriSmart AI — Disease Detection Service
Handles PyTorch EfficientNet-B0 model loading and real inference for crop disease classification.

Supports 38 crop-pathology classes from PlantVillage.
Weights loaded from: model/best_agri_model.pth
"""

import os
import io
import random
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from PIL import Image
import numpy as np
from dotenv import load_dotenv

from utils.label_map import INDEX_TO_LABEL, LABEL_TO_INDEX, get_label_info, NUM_CLASSES

load_dotenv()

logger = logging.getLogger(__name__)

MODEL_MODE = os.getenv("MODEL_MODE", "real").lower()
MODEL_WEIGHTS_PATH = os.getenv("MODEL_WEIGHTS_PATH", "../model/best_agri_model.pth")

# Global model holder
_model = None
_transform = None
_device = None
_loaded_path = None


def _find_weights_file() -> Optional[Path]:
    """Search candidate paths for the model weights file."""
    candidates = [
        Path(MODEL_WEIGHTS_PATH),
        Path("../model/best_agri_model.pth"),
        Path("model/best_agri_model.pth"),
        Path(__file__).resolve().parent.parent.parent / "model" / "best_agri_model.pth",
        Path("model_weights/best_agri_model.pth"),
        Path("model_weights/disease_model.pt"),
    ]
    for p in candidates:
        if p.exists() and p.is_file():
            return p.resolve()
    return None


def _load_real_model() -> bool:
    """Load EfficientNet-B0 with trained weights from disk using PyTorch & Torchvision."""
    global _model, _transform, _device, _loaded_path
    try:
        import torch
        import torch.nn as nn
        import torchvision.models as models
        from torchvision import transforms

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        weights_path = _find_weights_file()

        if not weights_path:
            logger.warning(
                f"Model weights not found at any candidate path. "
                "Set MODEL_MODE=mock or ensure model/best_agri_model.pth exists."
            )
            return False

        logger.info(f"Loading real EfficientNet-B0 model from {weights_path} on {device}...")

        # Construct EfficientNet-B0 with 38 classes
        model = models.efficientnet_b0(weights=None)
        in_features = model.classifier[1].in_features  # 1280
        model.classifier[1] = nn.Linear(in_features, NUM_CLASSES)

        checkpoint = torch.load(weights_path, map_location=device)
        state_dict = checkpoint.get("model_state_dict", checkpoint)

        # Load weights
        model.load_state_dict(state_dict, strict=True)
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

        _model = model
        _device = device
        _transform = transform
        _loaded_path = str(weights_path)
        logger.info(f"Real model successfully loaded from {_loaded_path} ({NUM_CLASSES} classes).")
        return True

    except Exception as e:
        logger.error(f"Failed to load real model: {e}. Falling back to mock mode.", exc_info=True)
        _model = None
        return False


def load_model():
    """Initialize the model at server startup."""
    global _model
    if MODEL_MODE == "real":
        success = _load_real_model()
        if not success:
            logger.warning("Real model load failed — falling back to mock mode.")
    else:
        logger.info("Running in MOCK mode — no model weights needed.")


def _mock_predict(image_bytes: bytes) -> dict:
    """Stub prediction: returns a deterministic-ish result seeded by image content."""
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

    raw = [rng.random() for _ in range(NUM_CLASSES)]
    raw[class_idx] *= 6
    total = sum(raw)
    probs = [r / total for r in raw]
    confidence = probs[class_idx]

    sorted_indices = sorted(range(NUM_CLASSES), key=lambda i: probs[i], reverse=True)
    top_3 = [
        {
            "label": INDEX_TO_LABEL[i],
            "display_name": get_label_info(INDEX_TO_LABEL[i])["display_name"],
            "confidence": round(probs[i] * 100, 1),
        }
        for i in sorted_indices[:3]
    ]

    return {
        "label": label,
        "confidence": round(confidence, 4),
        "top_3": top_3,
        "all_probabilities": {INDEX_TO_LABEL[i]: round(probs[i], 4) for i in range(NUM_CLASSES)},
    }


def _real_predict(image_bytes: bytes) -> dict:
    """Run actual EfficientNet-B0 inference on the uploaded image bytes."""
    import torch
    import torch.nn.functional as F

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    tensor = _transform(img).unsqueeze(0).to(_device)

    with torch.no_grad():
        logits = _model(tensor)
        probs = F.softmax(logits, dim=1)[0]
        confidence, class_idx = probs.max(dim=0)

    topk = torch.topk(probs, k=min(3, NUM_CLASSES))
    top_3 = [
        {
            "label": INDEX_TO_LABEL[int(topk.indices[i])],
            "display_name": get_label_info(INDEX_TO_LABEL[int(topk.indices[i])])["display_name"],
            "confidence": round(float(topk.values[i]) * 100, 1),
        }
        for i in range(len(topk.indices))
    ]

    label = INDEX_TO_LABEL[int(class_idx)]
    return {
        "label": label,
        "confidence": round(float(confidence), 4),
        "top_3": top_3,
        "all_probabilities": {INDEX_TO_LABEL[i]: round(float(probs[i]), 4) for i in range(NUM_CLASSES)},
    }


def predict_disease(image_bytes: bytes) -> dict:
    """
    Main entry point for disease prediction.
    Accepts raw image bytes, runs real ML or deterministic mock, and returns full agronomic diagnosis.
    """
    is_real = (_model is not None)
    if not is_real and MODEL_MODE == "real":
        # Attempt just-in-time loading if not loaded yet
        is_real = _load_real_model()

    if is_real and image_bytes and len(image_bytes) > 0:
        try:
            raw = _real_predict(image_bytes)
            active_mode = "real"
        except Exception as e:
            logger.error(f"Inference error with real model: {e}. Falling back to mock.", exc_info=True)
            raw = _mock_predict(image_bytes)
            active_mode = "mock"
    else:
        raw = _mock_predict(image_bytes)
        active_mode = "mock"

    info = get_label_info(raw["label"])
    return {
        "label": raw["label"],
        "crop": info.get("crop", "Unknown Crop"),
        "display_name": info["display_name"],
        "confidence": raw["confidence"],
        "is_healthy": info["is_healthy"],
        "precaution": info["precaution"],
        "precautions": info.get("precautions", {}),
        "summary": info.get("summary", ""),
        "top_3": raw.get("top_3", []),
        "model_mode": active_mode,
        "model_path": _loaded_path if active_mode == "real" else None,
    }
