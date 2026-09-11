"""
AgriSmart AI — Crop Recommendation Service (Bonus A)
Recommends suitable crops from soil type, pH, temperature, humidity,
rainfall, season, location, and previous crop data.

Uses a rule-based expert system layered with a simple scoring model.
In a real deployment, Member 3 can swap this with a trained scikit-learn classifier.
"""

from __future__ import annotations
import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ─── Crop Knowledge Base ─────────────────────────────────────────────────────
# Each crop has: optimal pH range, temp range (°C), humidity range (%),
# rainfall range (mm/year), suitable soil types, seasons, region hints
CROP_DB: dict[str, dict] = {
    "Rice": {
        "pH": (5.0, 7.0), "temp": (22, 35), "humidity": (70, 100),
        "rainfall": (1000, 2500), "soil": ["Clay", "Silty", "Loamy"],
        "seasons": ["Kharif"], "water": ["high"],
        "description": "Staple grain requiring high water and warm temperatures.",
    },
    "Wheat": {
        "pH": (6.0, 7.5), "temp": (10, 25), "humidity": (30, 60),
        "rainfall": (300, 800), "soil": ["Loamy", "Clay", "Silty"],
        "seasons": ["Rabi", "Winter"], "water": ["moderate"],
        "description": "Cool-season cereal grown in winter months.",
    },
    "Maize": {
        "pH": (5.8, 7.0), "temp": (18, 32), "humidity": (50, 80),
        "rainfall": (500, 1000), "soil": ["Loamy", "Sandy", "Silty"],
        "seasons": ["Kharif", "Zaid", "Summer"], "water": ["moderate"],
        "description": "Warm-season grain adaptable to many conditions.",
    },
    "Tomato": {
        "pH": (6.0, 7.0), "temp": (18, 30), "humidity": (50, 75),
        "rainfall": (400, 800), "soil": ["Loamy", "Sandy"],
        "seasons": ["Rabi", "Zaid", "Winter", "Summer"], "water": ["moderate"],
        "description": "Warm-season vegetable requiring well-drained fertile soil.",
    },
    "Potato": {
        "pH": (5.0, 6.5), "temp": (15, 25), "humidity": (60, 80),
        "rainfall": (400, 700), "soil": ["Loamy", "Sandy"],
        "seasons": ["Rabi", "Winter"], "water": ["moderate"],
        "description": "Cool-season tuber crop; sensitive to waterlogging.",
    },
    "Cotton": {
        "pH": (5.8, 8.0), "temp": (20, 38), "humidity": (40, 70),
        "rainfall": (500, 1000), "soil": ["Clay", "Loamy", "Black"],
        "seasons": ["Kharif"], "water": ["moderate"],
        "description": "Fiber crop requiring long frost-free season.",
    },
    "Groundnut": {
        "pH": (6.0, 7.0), "temp": (25, 35), "humidity": (50, 75),
        "rainfall": (500, 1000), "soil": ["Sandy", "Loamy"],
        "seasons": ["Kharif", "Summer"], "water": ["moderate", "low"],
        "description": "Legume crop with nitrogen-fixing capability.",
    },
    "Sugarcane": {
        "pH": (6.0, 8.0), "temp": (24, 38), "humidity": (60, 85),
        "rainfall": (1000, 2000), "soil": ["Loamy", "Clay", "Silty"],
        "seasons": ["Kharif", "Zaid"], "water": ["high"],
        "description": "Long-duration tropical cash crop requiring high water.",
    },
    "Soybean": {
        "pH": (6.0, 7.0), "temp": (20, 30), "humidity": (55, 80),
        "rainfall": (500, 1000), "soil": ["Loamy", "Silty", "Clay"],
        "seasons": ["Kharif"], "water": ["moderate"],
        "description": "Protein-rich legume; improves soil nitrogen.",
    },
    "Chickpea": {
        "pH": (6.0, 9.0), "temp": (15, 30), "humidity": (30, 60),
        "rainfall": (300, 700), "soil": ["Loamy", "Sandy", "Clay"],
        "seasons": ["Rabi", "Winter"], "water": ["low", "moderate"],
        "description": "Drought-tolerant legume grown in cool dry conditions.",
    },
    "Mustard": {
        "pH": (6.0, 7.5), "temp": (10, 25), "humidity": (35, 65),
        "rainfall": (250, 600), "soil": ["Loamy", "Sandy"],
        "seasons": ["Rabi", "Winter"], "water": ["low", "moderate"],
        "description": "Cool-season oilseed crop; drought tolerant.",
    },
    "Onion": {
        "pH": (6.0, 7.5), "temp": (13, 28), "humidity": (50, 75),
        "rainfall": (350, 700), "soil": ["Loamy", "Silty"],
        "seasons": ["Rabi", "Kharif"], "water": ["moderate"],
        "description": "Bulb vegetable requiring well-drained, fertile soil.",
    },
    "Banana": {
        "pH": (5.5, 7.0), "temp": (25, 40), "humidity": (70, 90),
        "rainfall": (1500, 2500), "soil": ["Loamy", "Silty", "Clay"],
        "seasons": ["Kharif", "Zaid"], "water": ["high"],
        "description": "Tropical fruit requiring high temperatures and rainfall.",
    },
    "Mango": {
        "pH": (5.5, 7.5), "temp": (24, 40), "humidity": (50, 80),
        "rainfall": (700, 1200), "soil": ["Loamy", "Sandy", "Clay"],
        "seasons": ["Kharif"], "water": ["moderate"],
        "description": "Tropical fruit tree; prefers well-drained soil.",
    },
}

# Good crop rotation pairs (avoid repeating same family)
ROTATION_AVOID = {
    "Tomato": ["Potato", "Pepper", "Tomato"],
    "Potato": ["Tomato", "Pepper", "Potato"],
    "Wheat": ["Wheat"],
    "Rice": ["Rice"],
    "Cotton": ["Cotton"],
    "Soybean": ["Groundnut"],  # same legume family
    "Groundnut": ["Soybean"],
}


def _score_crop(crop_name: str, crop: dict, req) -> float:
    """
    Score a crop from 0.0 to 1.0 based on how well it matches the request.
    """
    score = 0.0
    factors = 0

    def check_range(val, lo, hi):
        if lo <= val <= hi:
            return 1.0
        dist = min(abs(val - lo), abs(val - hi))
        return max(0.0, 1.0 - dist / max(hi - lo, 1))

    # pH suitability (weight 2)
    score += 2 * check_range(req.pH, *crop["pH"])
    factors += 2

    # Temperature suitability (weight 2)
    score += 2 * check_range(req.temperature, *crop["temp"])
    factors += 2

    # Humidity suitability (weight 1)
    score += 1 * check_range(req.humidity, *crop["humidity"])
    factors += 1

    # Rainfall suitability (weight 1)
    score += 1 * check_range(req.rainfall, *crop["rainfall"])
    factors += 1

    # Soil type match (weight 2)
    soil_norm = req.soil_type.strip().title()
    if any(s.lower() in soil_norm.lower() or soil_norm.lower() in s.lower() for s in crop["soil"]):
        score += 2
    factors += 2

    # Season match (weight 2)
    if req.season.strip().title() in crop["seasons"] or any(
        req.season.lower() in s.lower() for s in crop["seasons"]
    ):
        score += 2
    factors += 2

    # Water availability match (weight 1)
    if req.water_availability and req.water_availability.lower() in crop["water"]:
        score += 1
    factors += 1

    return score / factors if factors > 0 else 0.0


def recommend_crop(req) -> dict:
    """
    Main crop recommendation function.
    Returns recommended crop, confidence, reasoning, and alternatives.
    """
    scores: dict[str, float] = {}
    for name, info in CROP_DB.items():
        scores[name] = _score_crop(name, info, req)

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_crop, top_score = ranked[0]
    alternatives = [c for c, s in ranked[1:4] if s > 0.3]

    reasoning = (
        f"{top_crop} scores highest ({top_score:.2f}/1.00) for your conditions: "
        f"soil={req.soil_type}, pH={req.pH}, temp={req.temperature}°C, "
        f"humidity={req.humidity}%, rainfall={req.rainfall}mm, season={req.season}. "
        f"{CROP_DB[top_crop]['description']}"
    )

    # Rotation note
    rotation_note = None
    if req.previous_crop:
        avoid = ROTATION_AVOID.get(req.previous_crop, [])
        if top_crop in avoid:
            alt = alternatives[0] if alternatives else "a different crop"
            rotation_note = (
                f"Caution: {top_crop} follows {req.previous_crop} in the same plant family. "
                f"Consider {alt} instead to break disease cycles and improve soil health."
            )

    return {
        "recommended_crop": top_crop,
        "confidence": round(top_score, 3),
        "reasoning": reasoning,
        "alternative_crops": alternatives,
        "rotation_note": rotation_note,
    }
