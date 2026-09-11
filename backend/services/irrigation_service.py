"""
AgriSmart AI — Irrigation Prediction Service (Bonus B)
Determines whether irrigation is required based on soil moisture,
weather forecast, crop type, and growth stage.

Logic:
  1. Fetch 24-hour rain probability from Open-Meteo via weather_service
  2. Look up crop's minimum soil moisture threshold for its growth stage
  3. Apply decision rules:
     - If rain ≥ 70% → do NOT irrigate (rain incoming)
     - If soil moisture < threshold AND rain < 40% → irrigate
     - Intermediate ranges → moderate or delay recommendation
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ─── Crop Soil Moisture Thresholds (%) by growth stage ────────────────────────
# Below these values, the crop experiences water stress
# Values based on FAO-56 Paper crop coefficients and common extension guidance
MOISTURE_THRESHOLDS: dict[str, dict[str, float]] = {
    "Tomato": {
        "Seedling": 55.0, "Vegetative": 50.0, "Flowering": 60.0,
        "Fruiting": 55.0, "Maturity": 40.0, "default": 50.0,
    },
    "Potato": {
        "Seedling": 60.0, "Vegetative": 55.0, "Flowering": 65.0,
        "Tuber Formation": 70.0, "Maturity": 45.0, "default": 60.0,
    },
    "Wheat": {
        "Germination": 65.0, "Tillering": 55.0, "Jointing": 60.0,
        "Heading": 65.0, "Grain Fill": 55.0, "Maturity": 40.0, "default": 55.0,
    },
    "Rice": {
        "Seedling": 70.0, "Vegetative": 70.0, "Flowering": 75.0,
        "Grain Fill": 65.0, "Maturity": 40.0, "default": 70.0,
    },
    "Maize": {
        "Seedling": 55.0, "Vegetative": 50.0, "Tasseling": 65.0,
        "Silking": 70.0, "Grain Fill": 55.0, "Maturity": 40.0, "default": 55.0,
    },
    "Cotton": {
        "Seedling": 50.0, "Vegetative": 45.0, "Flowering": 60.0,
        "Boll Formation": 65.0, "Maturity": 35.0, "default": 50.0,
    },
    "default": {
        "Seedling": 55.0, "Vegetative": 50.0, "Flowering": 60.0,
        "Fruiting": 55.0, "Maturity": 40.0, "default": 50.0,
    },
}


def _get_threshold(crop_type: str, growth_stage: str) -> float:
    """Return soil moisture threshold % for a given crop and growth stage."""
    crop_key = crop_type.strip().title()
    crop_thresholds = MOISTURE_THRESHOLDS.get(crop_key, MOISTURE_THRESHOLDS["default"])
    stage_key = growth_stage.strip().title()
    return crop_thresholds.get(stage_key, crop_thresholds.get("default", 50.0))


def _water_stress_level(moisture: float, threshold: float) -> str:
    """Classify water stress level based on deficit from threshold."""
    deficit = threshold - moisture
    if deficit <= 0:
        return "none"
    elif deficit <= 5:
        return "low"
    elif deficit <= 15:
        return "moderate"
    elif deficit <= 25:
        return "high"
    else:
        return "critical"


def decide_irrigation(
    soil_moisture: float,
    crop_type: str,
    growth_stage: str,
    weather: dict,
) -> dict:
    """
    Main irrigation decision function.

    Args:
        soil_moisture: Current soil moisture %
        crop_type: e.g. "Tomato"
        growth_stage: e.g. "Flowering"
        weather: Dict from weather_service.get_weather()

    Returns:
        Dict with irrigate (bool), recommendation, reasoning, water_stress_level
    """
    threshold = _get_threshold(crop_type, growth_stage)
    rain_prob = weather.get("precipitation_probability_24h", 0.0)
    temp = weather.get("temperature", 25.0)
    stress = _water_stress_level(soil_moisture, threshold)

    irrigate = False
    recommendation = ""
    reasoning_parts = []

    reasoning_parts.append(
        f"Crop: {crop_type} | Stage: {growth_stage} | "
        f"Min moisture threshold: {threshold:.0f}%"
    )
    reasoning_parts.append(
        f"Current soil moisture: {soil_moisture:.1f}% | "
        f"24h rain probability: {rain_prob:.0f}%"
    )

    # ── Decision rules (in priority order) ────────────────────────────────
    if rain_prob >= 70:
        irrigate = False
        recommendation = f"Delay irrigation — rainfall likely in next 24 h ({rain_prob:.0f}% probability)."
        reasoning_parts.append("Rule: Rain probability ≥ 70% → skip irrigation, let rain do the work.")

    elif soil_moisture >= threshold:
        irrigate = False
        recommendation = "No irrigation needed — soil moisture is adequate."
        reasoning_parts.append(
            f"Rule: Soil moisture ({soil_moisture:.1f}%) ≥ threshold ({threshold:.0f}%) → skip irrigation."
        )

    elif soil_moisture < threshold and rain_prob < 40:
        irrigate = True
        deficit = threshold - soil_moisture
        recommendation = (
            f"Irrigate now — soil moisture is {deficit:.1f}% below the {growth_stage.lower()} "
            f"stage threshold for {crop_type}."
        )
        reasoning_parts.append(
            f"Rule: Soil moisture ({soil_moisture:.1f}%) < threshold ({threshold:.0f}%) "
            f"AND rain probability ({rain_prob:.0f}%) < 40% → irrigate."
        )

    elif rain_prob >= 40:
        irrigate = False
        recommendation = (
            f"Wait 12–24 h before irrigating — moderate rain possible ({rain_prob:.0f}% probability)."
        )
        reasoning_parts.append(
            f"Rule: Moderate rain probability ({rain_prob:.0f}%) → delay decision."
        )

    # ── Temperature modifiers ──────────────────────────────────────────────
    if temp > 35 and not irrigate and rain_prob < 50:
        irrigate = True
        recommendation += f" High temperature ({temp}°C) increases evapotranspiration — irrigate lightly."
        reasoning_parts.append(f"Override: Temperature {temp}°C > 35°C increases crop water demand.")

    return {
        "irrigate": irrigate,
        "recommendation": recommendation,
        "reasoning": " | ".join(reasoning_parts),
        "soil_moisture": soil_moisture,
        "rain_probability_24h": rain_prob,
        "temperature": temp,
        "moisture_threshold": threshold,
        "water_stress_level": stress,
    }
