"""
AgriSmart AI — Sustainability Scoring Service (Bonus D)
Computes an indicative sustainability score from water efficiency,
resource use, and crop health with improvement suggestions.

Formula (fully reproducible, as required by Section 3.2-D of the problem statement):

  score = water_score * 0.35
        + fertilizer_score * 0.25
        + disease_score * 0.20
        + irrigation_method_score * 0.20

Each sub-score is in the range [0, 100].

Water score:
  - Reference: FAO typical water use per crop per hectare per week
  - Efficiency = min(reference_liters / actual_liters, 1.0)
  - water_score = efficiency * 100

Fertilizer score:
  - Optimal range per crop: 20-40 kg/ha/week
  - Penalty for over-use: linear deduction beyond 40 kg/ha
  - fertilizer_score = max(0, 100 - max(0, fertilizer_kg_per_hectare - 40) * 2)

Disease score:
  - disease_detected = False → 100
  - disease_detected = True → 40 (disease means some crop health loss)

Irrigation method score:
  - drip       → 100 (most efficient)
  - sprinkler  → 75
  - furrow     → 50
  - flood      → 30 (least efficient)
  - other/none → 20
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ─── Reference water use (liters per hectare per week) by crop ────────────────
REFERENCE_WATER_USE: dict[str, float] = {
    "Rice": 60_000,
    "Sugarcane": 55_000,
    "Banana": 50_000,
    "Cotton": 35_000,
    "Maize": 30_000,
    "Tomato": 28_000,
    "Wheat": 25_000,
    "Potato": 25_000,
    "Soybean": 22_000,
    "Groundnut": 20_000,
    "Onion": 20_000,
    "Chickpea": 15_000,
    "Mustard": 12_000,
    "default": 25_000,
}

IRRIGATION_METHOD_SCORES: dict[str, float] = {
    "drip": 100.0,
    "sprinkler": 75.0,
    "furrow": 50.0,
    "flood": 30.0,
}

GRADE_THRESHOLDS = [
    (90, "A"),
    (75, "B"),
    (60, "C"),
    (45, "D"),
    (0, "F"),
]


def _water_score(water_used: float, area: float, crop: str) -> float:
    """Score water usage efficiency relative to FAO reference."""
    ref = REFERENCE_WATER_USE.get(crop.strip().title(), REFERENCE_WATER_USE["default"])
    ref_total = ref * area  # scaled to actual farm size
    if water_used <= 0:
        return 100.0
    efficiency = min(ref_total / water_used, 1.0)
    return round(efficiency * 100, 1)


def _fertilizer_score(fert_kg_per_ha: float) -> float:
    """Score fertilizer use; penalise over-application."""
    optimal_max = 40.0  # kg/ha
    if fert_kg_per_ha <= optimal_max:
        return 100.0
    excess = fert_kg_per_ha - optimal_max
    score = max(0.0, 100.0 - excess * 2.0)
    return round(score, 1)


def _disease_score(disease_detected: bool) -> float:
    """Penalise if disease was detected (indicates crop health loss)."""
    return 40.0 if disease_detected else 100.0


def _irrigation_method_score(method: Optional[str]) -> float:
    """Score the irrigation method used."""
    if not method:
        return 20.0
    return IRRIGATION_METHOD_SCORES.get(method.lower().strip(), 20.0)


def _grade(score: float) -> str:
    for threshold, grade in GRADE_THRESHOLDS:
        if score >= threshold:
            return grade
    return "F"


def _improvement_suggestions(
    w_score: float,
    f_score: float,
    d_score: float,
    m_score: float,
    req,
) -> list[str]:
    suggestions = []

    if w_score < 70:
        suggestions.append(
            f"Water use efficiency is low ({w_score:.0f}/100). "
            "Switch to drip or sprinkler irrigation. "
            "Schedule irrigation in early morning to reduce evaporation."
        )

    if f_score < 70:
        suggestions.append(
            f"Fertilizer application ({req.fertilizer_kg_per_hectare} kg/ha) exceeds optimal range (20-40 kg/ha). "
            "Consider soil testing and split-application to reduce waste and runoff."
        )

    if d_score < 100:
        suggestions.append(
            "Disease was detected this week. Early treatment reduces crop loss and reduces "
            "the need for repeated pesticide applications, improving sustainability."
        )

    if m_score < 75:
        method = req.irrigation_method or "flood"
        suggestions.append(
            f"Current irrigation method ({method}) has low water efficiency. "
            "Upgrading to drip irrigation can reduce water consumption by 30-50%."
        )

    if req.pesticide_used:
        suggestions.append(
            "Pesticide use detected. Where possible, opt for IPM (Integrated Pest Management): "
            "biocontrol agents, resistant varieties, and targeted spraying reduce chemical load."
        )

    if not suggestions:
        suggestions.append("Great work! Your farm practices are sustainable. Continue monitoring disease and water use.")

    return suggestions


def compute_sustainability(req) -> dict:
    """
    Compute sustainability score for a given week of farm data.

    Args:
        req: SustainabilityRequest pydantic object

    Returns:
        Dict matching SustainabilityResponse schema
    """
    ws = _water_score(req.water_used_liters, req.area_hectares, req.crop_type)
    fs = _fertilizer_score(req.fertilizer_kg_per_hectare)
    ds = _disease_score(req.disease_detected)
    ms = _irrigation_method_score(req.irrigation_method)

    # Weighted composite score
    score = ws * 0.35 + fs * 0.25 + ds * 0.20 + ms * 0.20

    formula_breakdown = {
        "water_score": ws,
        "water_weight": 0.35,
        "fertilizer_score": fs,
        "fertilizer_weight": 0.25,
        "disease_score": ds,
        "disease_weight": 0.20,
        "irrigation_method_score": ms,
        "irrigation_method_weight": 0.20,
        "formula": "score = water*0.35 + fertilizer*0.25 + disease*0.20 + irrigation_method*0.20",
        "reference_water_liters_per_ha_per_week": REFERENCE_WATER_USE.get(
            req.crop_type.strip().title(), REFERENCE_WATER_USE["default"]
        ),
    }

    return {
        "score": round(score, 1),
        "grade": _grade(score),
        "water_efficiency_score": ws,
        "fertilizer_score": fs,
        "disease_management_score": ds,
        "irrigation_method_score": ms,
        "improvement_suggestions": _improvement_suggestions(ws, fs, ds, ms, req),
        "formula_breakdown": formula_breakdown,
    }
