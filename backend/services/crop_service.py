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
    "Apple": {
        "pH": (5.5, 6.8), "temp": (5, 22), "humidity": (50, 75),
        "rainfall": (800, 1400), "soil": ["Loamy", "Sandy", "Clay"],
        "seasons": ["Rabi", "Winter"], "water": ["moderate"],
        "description": "Temperate fruit requiring winter chilling; ideal for Himalayan cold agro-zones.",
    },
    "Pearl Millet": {
        "pH": (6.0, 8.0), "temp": (24, 38), "humidity": (30, 65),
        "rainfall": (350, 600), "soil": ["Sandy", "Loamy"],
        "seasons": ["Kharif", "Summer"], "water": ["low"],
        "description": "Extremely drought-hardy nutritious millet; excels in arid and semi-arid tracts.",
    },
}

# ─── Agro-Climatic Zones & Regional Affinity ──────────────────────────────────
# Maps regions / states / districts to their agro-climatic profile and primary crops
AGRO_ZONES: dict[str, dict] = {
    "gujarat": {
        "name": "Gujarat / Western Semi-Arid & Coastal Zone",
        "keywords": [
            "gujarat", "surat", "ahmedabad", "rajkot", "vadodara", "bhavnagar",
            "jamnagar", "junagadh", "anand", "mehsana", "kutch", "saurashtra",
            "gandhinagar", "bharuch", "navsari", "valsad", "amreli", "morbi",
            "patan", "porbandar", "surendranagar", "botad", "sarkhej"
        ],
        "lat_range": (20.1, 24.7),
        "lon_range": (68.1, 74.5),
        "favored_crops": ["Cotton", "Groundnut", "Wheat", "Chickpea", "Onion", "Banana", "Pearl Millet", "Mustard", "Tomato"],
        "disfavored_crops": ["Apple", "Jute"],
        "zone_note": "Western semi-arid and coastal plains with fertile black and loamy soils, renowned for high cash-crop and pulse productivity.",
    },
    "maharashtra": {
        "name": "Maharashtra / Western Deccan Plateau",
        "keywords": [
            "maharashtra", "nashik", "pune", "nagpur", "jalgaon", "aurangabad",
            "chhatrapati sambhajinagar", "kolhapur", "solapur", "ahmednagar",
            "satara", "sangli", "amravati", "akola", "latur", "vidarbha",
            "marathwada", "mumbai", "thane", "palghar", "dhule", "nanded"
        ],
        "lat_range": (15.6, 22.1),
        "lon_range": (72.6, 80.9),
        "favored_crops": ["Onion", "Tomato", "Soybean", "Cotton", "Sugarcane", "Chickpea", "Wheat", "Maize", "Groundnut"],
        "disfavored_crops": ["Apple"],
        "zone_note": "Deccan basaltic trap and fertile river basins ideal for intensive horticulture, pulses, and oilseeds.",
    },
    "punjab_haryana": {
        "name": "Indo-Gangetic Plains (Punjab & Haryana)",
        "keywords": [
            "punjab", "haryana", "ludhiana", "amritsar", "jalandhar", "patiala",
            "bathinda", "karnal", "hisar", "ambala", "rohtak", "sirsa", "panipat",
            "sonipat", "kurukshetra", "mohali", "chandigarh", "faridabad", "gurugram"
        ],
        "lat_range": (27.6, 32.5),
        "lon_range": (73.8, 77.8),
        "favored_crops": ["Wheat", "Rice", "Mustard", "Potato", "Maize", "Sugarcane", "Cotton"],
        "disfavored_crops": ["Banana", "Apple", "Mango"],
        "zone_note": "Alluvial fertile canal-irrigated green revolution belt with superior cereal and tuber productivity.",
    },
    "uttar_pradesh_bihar": {
        "name": "Gangetic Alluvial Basin (UP & Bihar)",
        "keywords": [
            "uttar pradesh", "bihar", "lucknow", "kanpur", "varanasi", "agra",
            "meerut", "prayagraj", "patna", "gaya", "muzaffarpur", "bhagalpur",
            "gorakhpur", "bareilly", "aligarh", "moradabad"
        ],
        "lat_range": (23.8, 30.5),
        "lon_range": (77.0, 88.3),
        "favored_crops": ["Wheat", "Rice", "Sugarcane", "Potato", "Mustard", "Maize", "Chickpea"],
        "disfavored_crops": ["Apple", "Cotton"],
        "zone_note": "Deep alluvial silt deposited by the Ganges system, supporting high-density multi-cropping.",
    },
    "madhya_pradesh": {
        "name": "Central Plateau & Malwa (Madhya Pradesh)",
        "keywords": [
            "madhya pradesh", "indore", "bhopal", "ujjain", "jabalpur", "gwalior",
            "sagar", "rewa", "satna", "dewas", "ratlam", "khargone", "khandwa",
            "malwa"
        ],
        "lat_range": (21.1, 26.9),
        "lon_range": (74.0, 82.8),
        "favored_crops": ["Soybean", "Wheat", "Chickpea", "Mustard", "Maize", "Cotton", "Groundnut", "Onion"],
        "disfavored_crops": ["Apple", "Rice"],
        "zone_note": "Central India black soil plateau; national leader in soybean and organic pulse rotation.",
    },
    "rajasthan": {
        "name": "Western Arid & Semi-Arid (Rajasthan)",
        "keywords": [
            "rajasthan", "jaipur", "jodhpur", "bikaner", "kota", "udaipur",
            "sri ganganagar", "alwar", "ajmer", "bhilwara", "sikar", "pali", "barmer", "jaisalmer"
        ],
        "lat_range": (23.3, 30.2),
        "lon_range": (69.5, 78.3),
        "favored_crops": ["Mustard", "Pearl Millet", "Chickpea", "Groundnut", "Wheat", "Onion"],
        "disfavored_crops": ["Rice", "Sugarcane", "Banana", "Apple"],
        "zone_note": "Drought-resilient cropping zone with high solar radiation and quick-maturing oilseed/pulse cultivars.",
    },
    "south_india": {
        "name": "Southern Plateau & Coastal Zone",
        "keywords": [
            "karnataka", "tamil nadu", "andhra pradesh", "telangana", "kerala",
            "bengaluru", "mysuru", "hyderabad", "warangal", "guntur", "vijayawada",
            "coimbatore", "madurai", "salem", "thanjavur", "chennai", "kochi",
            "visakhapatnam", "tirupati", "hubli", "belagavi"
        ],
        "lat_range": (8.0, 19.9),
        "lon_range": (74.0, 85.0),
        "favored_crops": ["Rice", "Maize", "Groundnut", "Cotton", "Sugarcane", "Banana", "Tomato", "Mango"],
        "disfavored_crops": ["Apple", "Wheat"],
        "zone_note": "Tropical agro-climate with red loamy and coastal deltaic soils supporting year-round cropping.",
    },
    "eastern_india": {
        "name": "Eastern Delta & Humid Plains",
        "keywords": [
            "west bengal", "odisha", "assam", "kolkata", "bhubaneswar", "cuttack",
            "guwahati", "siliguri", "howrah", "asansol", "durgapur", "rourkela"
        ],
        "lat_range": (19.0, 28.0),
        "lon_range": (81.0, 96.0),
        "favored_crops": ["Rice", "Potato", "Maize", "Mustard", "Banana", "Tomato"],
        "disfavored_crops": ["Apple", "Cotton"],
        "zone_note": "High rainfall deltaic environment with rich alluvial soil, prime for paddy and vegetable cultivation.",
    },
    "himalayan": {
        "name": "Western Himalayan Temperate Zone",
        "keywords": [
            "himachal", "himachal pradesh", "uttarakhand", "kashmir", "jammu",
            "shimla", "manali", "dehradun", "nainital", "srinagar", "solan", "kullu"
        ],
        "lat_range": (28.7, 37.1),
        "lon_range": (73.5, 81.0),
        "favored_crops": ["Apple", "Potato", "Maize", "Wheat"],
        "disfavored_crops": ["Rice", "Cotton", "Sugarcane", "Banana", "Mango"],
        "zone_note": "High-altitude temperate climate with chilling hour requirements for pome fruits and seed tubers.",
    },
}

def detect_agro_zone(location_str: Optional[str] = None, lat: Optional[float] = None, lon: Optional[float] = None) -> tuple[str, dict]:
    """
    Detects the agricultural zone from user location string or coordinates.
    Returns (zone_key, zone_dict).
    """
    loc_lower = (location_str or "").lower().strip()

    # 1. Direct keyword match
    if loc_lower:
        for z_key, z_data in AGRO_ZONES.items():
            if any(kw in loc_lower for kw in z_data["keywords"]):
                return z_key, z_data

    # 2. Coordinate boundary match if available
    if lat is not None and lon is not None:
        for z_key, z_data in AGRO_ZONES.items():
            min_lat, max_lat = z_data["lat_range"]
            min_lon, max_lon = z_data["lon_range"]
            if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                return z_key, z_data

    # Default: General Indian Agro-Climatic Zone
    return "general", {
        "name": "General Agro-Ecological Zone",
        "keywords": [],
        "lat_range": (8.0, 37.0),
        "lon_range": (68.0, 97.0),
        "favored_crops": ["Wheat", "Chickpea", "Maize", "Tomato", "Mustard", "Onion", "Cotton"],
        "disfavored_crops": [],
        "zone_note": "Multi-region adaptable agronomic framework balancing soil telemetry and seasonal indicators.",
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


def _score_crop(crop_name: str, crop: dict, req, zone_data: dict) -> tuple[float, bool]:
    """
    Score a crop from 0.0 to 1.0 based on soil, climate, and regional location suitability.
    Returns (score, is_regionally_favored).
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

    # Location & Regional Agro-Climatic Zone Match (weight 3.0)
    is_favored = crop_name in zone_data.get("favored_crops", [])
    is_disfavored = crop_name in zone_data.get("disfavored_crops", [])

    if is_favored:
        score += 3.0 * 1.0
    elif is_disfavored:
        score += 3.0 * 0.15
    else:
        score += 3.0 * 0.70
    factors += 3

    final_score = score / factors if factors > 0 else 0.0
    return final_score, is_favored


def recommend_crop(req) -> dict:
    """
    Main crop recommendation function.
    Evaluates soil, seasonal climate, and regional location suitability.
    Returns recommended crop, confidence, reasoning, and alternatives.
    """
    # Detect Agro-climatic zone from location or coordinates
    req_lat = getattr(req, "latitude", None)
    req_lon = getattr(req, "longitude", None)
    zone_key, zone_data = detect_agro_zone(getattr(req, "location", None), req_lat, req_lon)

    scores: dict[str, float] = {}
    favored_map: dict[str, bool] = {}

    for name, info in CROP_DB.items():
        sc, is_fav = _score_crop(name, info, req, zone_data)
        scores[name] = sc
        favored_map[name] = is_fav

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_crop, top_score = ranked[0]
    alternatives = [c for c, s in ranked[1:5] if s > 0.35][:3]

    loc_name = getattr(req, "location", None) or zone_data["name"]

    regional_clause = (
        f"Selected/Current Location ({loc_name}) matches the {zone_data['name']}. "
        f"{top_crop} is a proven high-performance cultivar for this agro-ecological tract. "
    )

    reasoning = (
        f"{top_crop} ranks #1 with {round(top_score * 100, 1)}% suitability for {loc_name}. "
        f"{regional_clause}"
        f"Soil match: {req.soil_type} at pH {req.pH}, temperature {req.temperature}°C, "
        f"humidity {req.humidity}%, and rainfall {req.rainfall}mm ({req.season} season). "
        f"{CROP_DB[top_crop]['description']}"
    )

    # Rotation note
    rotation_note = None
    if getattr(req, "previous_crop", None):
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
        "zone_key": zone_key,
        "zone_name": zone_data["name"],
        "zone_note": zone_data["zone_note"],
        "location_analyzed": loc_name,
        "favored_crops": zone_data["favored_crops"],
    }
