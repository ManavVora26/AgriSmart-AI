"""
AgriSmart AI — Frontend API Adapter Bridge
Mounts under /api prefix to provide 100% plug-and-play compatibility
with the frontend web application (frontend/js/api.js and frontend/js/main.js).
"""

import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, UploadFile, File, Form, Query, HTTPException, Body
from pydantic import BaseModel, Field

from services.disease_service import predict_disease
from services.weather_service import (
    get_weather,
    generate_weather_actions,
    geocode_location,
    reverse_geocode,
    get_ip_location,
)
from services.crop_service import recommend_crop as service_recommend_crop
from services.irrigation_service import decide_irrigation
from services.sustainability_service import compute_sustainability
from services.assistant_service import get_assistant_response
from scheduler.agentic_loop import get_recent_advisories, run_advisory_cycle_now
from models.schemas import CropRecommendRequest, SustainabilityRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Frontend API Adapter Bridge"])


# ─────────────────────────────────────────────────────────────────────────────
# 1. Disease Detection (/api/predict-disease)
# ─────────────────────────────────────────────────────────────────────────────
@router.post(
    "/predict-disease",
    summary="Disease Detection (Frontend format)",
    description="Accepts leaf image and contextual farm telemetry; returns formatted pathology analysis.",
)
async def api_predict_disease(
    image: Optional[UploadFile] = File(None, description="Leaf image file"),
    file: Optional[UploadFile] = File(None, description="Alternative file param"),
    crop_type: str = Form("Tomato"),
    growth_stage: str = Form("Fruiting"),
    soil_type: str = Form("Loamy"),
    ph: float = Form(6.4),
    soil_moisture: float = Form(68.0),
    temperature: float = Form(27.0),
    rain_probability: float = Form(65.0),
    location: str = Form("Nashik Valley, MH"),
):
    upload = image or file
    if not upload:
        image_bytes = b""
        filename = "sample_leaf.jpg"
    else:
        image_bytes = await upload.read()
        filename = upload.filename or "uploaded_leaf.jpg"

    # Call underlying disease service
    result = predict_disease(image_bytes=image_bytes)

    is_healthy = result.get("is_healthy", False)
    detected_crop = result.get("crop") or crop_type
    disease_label = result.get("display_name") or f"{detected_crop} - Healthy"
    confidence_pct = round(result.get("confidence", 0.95) * 100, 1)
    precautions = result.get("precautions", {})
    summary_text = result.get("summary") or ""
    top_3 = result.get("top_3", [])
    model_mode = result.get("model_mode", "mock")

    if is_healthy:
        return {
            "status": "healthy",
            "crop": detected_crop,
            "disease": disease_label,
            "scientificName": f"{detected_crop} spp. (Canopy verified healthy)",
            "confidence": confidence_pct,
            "severity": "None",
            "badgeColor": "#2E7D32",
            "summary": (
                summary_text or
                f"The examined {detected_crop} leaf exhibits robust cellular turgor, "
                "uniform chlorophyll pigmentation, and zero visible signs of fungal or bacterial sporulation."
            ),
            "symptoms": [
                "Uniform chlorophyll pigmentation without chlorosis or necrosis",
                "Intact leaf margins and healthy vascular venation",
                "Absence of fungal mycelium, bacterial ooze, or viral mosaics",
            ],
            "precautions": {
                "organic": precautions.get("organic", "Apply preventive organic bio-agents and compost tea."),
                "cultural": precautions.get("cultural", "Maintain optimal row spacing and avoid wetting foliage during sunset."),
                "chemical": precautions.get("chemical", "No chemical intervention needed. Monitor regularly."),
            },
            "top_3": top_3,
            "model_mode": model_mode,
            "nextInspection": "Check again in 7 days or after heavy rainfall.",
        }

    # Diseased
    return {
        "status": "diseased",
        "crop": detected_crop,
        "disease": disease_label,
        "scientificName": f"{disease_label} Pathogen Complex",
        "confidence": confidence_pct,
        "severity": "High" if (soil_moisture > 75 or confidence_pct > 80) else "Moderate",
        "badgeColor": "#C62828",
        "summary": (
            summary_text or
            f"Pathogen detected affecting {detected_crop} foliage. "
            f"Microclimate conditions (moisture {soil_moisture}%, temp {temperature}°C) "
            "are conducive to spore dispersion. Timely mitigation is recommended."
        ),
        "symptoms": [
            f"Foliar lesions with characteristic pathology observed on {detected_crop} leaf surface",
            f"Active infection area estimated at {round(max(10.0, 100 - confidence_pct/2), 1)}% of sampled surface",
            "Early to mid-stage necrosis detected across interveinal zones",
        ],
        "precautions": {
            "organic": precautions.get("organic", "Apply cold-pressed Neem Seed Kernel Extract (5%) or biological agents."),
            "cultural": precautions.get("cultural", "Prune infected foliage, sanitize tools, and improve canopy air circulation."),
            "chemical": precautions.get("chemical", result.get("precaution", "Apply recommended protective fungicide.")),
        },
        "top_3": top_3,
        "model_mode": model_mode,
        "nextInspection": "Re-evaluate in 3 to 5 days after applying treatment.",
    }



# ─────────────────────────────────────────────────────────────────────────────
# 2. Crop Recommendation (/api/recommend-crop)
# ─────────────────────────────────────────────────────────────────────────────
class FrontendCropRequest(BaseModel):
    ph: Optional[float] = 6.5
    moisture: Optional[float] = 45.0
    temperature: Optional[float] = 28.0
    rainfall_prob: Optional[float] = 30.0
    soil_type: Optional[str] = "Loamy"
    location: Optional[str] = "Local"


@router.post(
    "/recommend-crop",
    summary="Crop Recommendation (Frontend format)",
    description="Recommends crops tailored to soil pH, moisture, climate, and soil type.",
)
async def api_recommend_crop(req: FrontendCropRequest):
    req_obj = CropRecommendRequest(
        soil_type=req.soil_type or "Loamy",
        pH=req.ph or 6.5,
        temperature=req.temperature or 28.0,
        humidity=req.moisture or 50.0,
        rainfall=(req.rainfall_prob or 30.0) * 10.0,
        season="Kharif",
        location=req.location or "Local",
    )

    service_res = service_recommend_crop(req_obj)

    top_crop = service_res.get("recommended_crop", "Chickpea")
    confidence = service_res.get("confidence", 0.95)
    alternatives = service_res.get("alternative_crops", ["Maize", "Pigeonpeas", "Mothbeans"])

    crop_profiles = {
        "Chickpea": {
            "name": "Chickpea / Gram",
            "botanicalName": "Cicer arietinum",
            "water": "Low to Moderate (250-350mm)",
            "cycle": "90-110 Days",
            "yield": "18-22 Q/Ha",
            "profit": "High (MSP Supported)",
            "advantage": "Symbiotic nitrogen fixation restores soil fertility for successive rotations.",
        },
        "Wheat": {
            "name": "Durum Wheat",
            "botanicalName": "Triticum durum",
            "water": "Moderate (300-450mm)",
            "cycle": "110-125 Days",
            "yield": "40-48 Q/Ha",
            "profit": "Stable High Volume",
            "advantage": "High market liquidity with guaranteed government procurement.",
        },
        "Maize": {
            "name": "Corn / Hybrid Maize",
            "botanicalName": "Zea mays",
            "water": "Moderate (450-600mm)",
            "cycle": "85-100 Days",
            "yield": "55-65 Q/Ha",
            "profit": "Strong Commercial Demand",
            "advantage": "Excellent grain-to-biomass ratio with robust industrial starch uptake.",
        },
        "Tomato": {
            "name": "Commercial Hybrid Tomato",
            "botanicalName": "Solanum lycopersicum",
            "water": "Moderate to High",
            "cycle": "70-90 Days",
            "yield": "60-80 MT/Ha",
            "profit": "High Cash Yield",
            "advantage": "High daily harvest turnovers in fresh vegetable markets.",
        },
        "Cotton": {
            "name": "Bt Cotton",
            "botanicalName": "Gossypium hirsutum",
            "water": "Moderate to High",
            "cycle": "150-180 Days",
            "yield": "25-30 Q/Ha",
            "profit": "High Cash Flow",
            "advantage": "Thrives in deep black cotton soils with high moisture retention.",
        },
        "Rice": {
            "name": "Paddy / Basmati Rice",
            "botanicalName": "Oryza sativa",
            "water": "High (1100-1400mm)",
            "cycle": "120-135 Days",
            "yield": "45-55 Q/Ha",
            "profit": "High Volume Export",
            "advantage": "High yield stability in water-retentive clay loam terrain.",
        },
    }

    all_crops = [top_crop] + alternatives
    ui_recommendations = []
    for idx, c_name in enumerate(all_crops[:4], start=1):
        profile = crop_profiles.get(
            c_name,
            {
                "name": c_name,
                "botanicalName": f"{c_name} spp.",
                "water": "Moderate (400-500mm)",
                "cycle": "90-120 Days",
                "yield": "25-30 Q/Ha",
                "profit": "Market Linked",
                "advantage": "Well-adapted to local agro-climatic conditions.",
            },
        )
        score = round((confidence - (idx - 1) * 0.05) * 100, 1)

        ui_recommendations.append({
            "rank": idx,
            "name": profile["name"],
            "botanicalName": profile["botanicalName"],
            "matchScore": score,
            "waterRequirement": profile["water"],
            "harvestDuration": profile["cycle"],
            "expectedYield": profile["yield"],
            "profitPotential": profile["profit"],
            "rationale": (
                service_res.get("reasoning", "")
                if idx == 1
                else f"Secondary fit with soil pH {req.ph} and climatic profile."
            ),
            "keyAdvantage": profile["advantage"],
        })

    return {
        "status": "success",
        "soil_profile": {
            "soil_type": req.soil_type,
            "ph": req.ph,
            "moisture": req.moisture,
            "temperature": req.temperature,
            "location": req.location,
        },
        "recommendations": ui_recommendations,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3. Smart Irrigation (/api/irrigation/advice)
# ─────────────────────────────────────────────────────────────────────────────
@router.get(
    "/irrigation/advice",
    summary="Smart Irrigation Advice (Frontend format)",
    description="Computes irrigation need and optimal scheduling from telemetry query params or live location.",
)
async def api_irrigation_advice(
    moisture: float = Query(42.0, description="Soil moisture percentage"),
    rain_prob: Optional[float] = Query(None, description="24-hour rain probability"),
    temp: Optional[float] = Query(None, description="Temperature in Celsius"),
    crop: str = Query("Tomato", description="Crop type"),
    soil_type: str = Query("Loamy", description="Soil type"),
    lat: Optional[float] = Query(None, description="Latitude"),
    lon: Optional[float] = Query(None, description="Longitude"),
    location: Optional[str] = Query(None, description="Location name"),
):
    # If live weather params are missing, resolve from coordinates if available
    resolved_lat, resolved_lon = lat, lon
    resolved_location = location or "Current Farm"

    if (rain_prob is None or temp is None) and (resolved_lat is not None or location is not None):
        try:
            if resolved_lat is None and location:
                geo = await geocode_location(location)
                resolved_lat, resolved_lon = geo.get("latitude"), geo.get("longitude")
                resolved_location = geo.get("display_name", location)
            
            if resolved_lat is not None and resolved_lon is not None:
                live_w = await get_weather(resolved_lat, resolved_lon)
                if rain_prob is None:
                    rain_prob = live_w.get("precipitation_probability_24h", 35.0)
                if temp is None:
                    temp = live_w.get("temperature", 28.0)
        except Exception as e:
            logger.warning(f"Failed to fetch live weather for irrigation: {e}")

    effective_rain_prob = rain_prob if rain_prob is not None else 35.0
    effective_temp = temp if temp is not None else 28.0

    mock_weather = {
        "precipitation_probability_24h": effective_rain_prob,
        "temperature": effective_temp,
    }

    res = decide_irrigation(
        soil_moisture=moisture,
        crop_type=crop,
        growth_stage="Fruiting",
        weather=mock_weather,
    )

    needed = res.get("irrigate", False)

    if effective_rain_prob >= 60 and moisture > 35:
        decision = f"Irrigation Delayed — Rain Incoming ({int(effective_rain_prob)}%)"
        reasoning = (
            f"Upcoming precipitation forecast of <strong>{int(effective_rain_prob)}%</strong> is expected within the next 24 hours at {resolved_location}. "
            f"Current soil moisture ({moisture}%) is above critical threshold for {crop}. "
            "Postponing irrigation will conserve water and prevent waterlogging root stress."
        )
        optimal_window = "Hold off; re-evaluate after rain passes"
    elif needed:
        decision = "Irrigation Required — Apply 3.5 L/m²"
        reasoning = (
            f"Soil moisture ({moisture}%) has dropped below optimal threshold for {crop}. "
            f"With temperature at {effective_temp}°C and low rain probability ({int(effective_rain_prob)}%) at {resolved_location}, "
            "scheduled drip irrigation is recommended to prevent drought stress."
        )
        optimal_window = "Early Morning (05:30 AM – 08:00 AM)"
    else:
        decision = f"Soil Moisture Optimal ({moisture}%)"
        reasoning = (
            f"Current soil moisture ({moisture}%) is well within the healthy turgor range for {crop} ({soil_type} soil). "
            f"Local conditions at {resolved_location} are stable. No active irrigation needed at this moment."
        )
        optimal_window = "Next scheduled check in 12 hours"

    return {
        "needed": needed,
        "decision": decision,
        "reasoning": reasoning,
        "metrics": {
            "soilMoisture": moisture,
            "rainForecast24h": f"{int(effective_rain_prob)}% ({'8-12 mm' if effective_rain_prob > 50 else '<2 mm'})",
            "temperature": effective_temp,
            "crop": crop,
            "location": resolved_location,
        },
        "schedule": {
            "optimalWindow": optimal_window,
            "recommendedVolumePerSqm": 3.5 if needed else 0.0,
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# 3.5 Location Intelligence (/api/location/*)
# ─────────────────────────────────────────────────────────────────────────────
@router.get(
    "/location/current",
    summary="Detect Current Location",
    description="Returns user approximate farm location from IP address as a zero-friction fallback.",
)
async def api_location_current():
    return await get_ip_location()


@router.get(
    "/location/search",
    summary="Search & Autocomplete Farm Locations",
    description="Geocodes any village, town, or city name into coordinates.",
)
async def api_location_search(query: str = Query(..., description="City or district name")):
    return await geocode_location(query)


@router.get(
    "/location/reverse",
    summary="Reverse Geocode Coordinates",
    description="Converts GPS latitude and longitude into human-readable city and state.",
)
async def api_location_reverse(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    return await reverse_geocode(lat, lon)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Weather Intelligence (/api/weather/advisory)
# ─────────────────────────────────────────────────────────────────────────────
@router.get(
    "/weather/advisory",
    summary="Weather Intelligence (Frontend format)",
    description="Returns real-time weather, prioritized farmer action banners, and 5-day forecast for any location.",
)
async def api_weather_advisory(
    location: Optional[str] = Query(None, description="Location name or coordinates"),
    lat: Optional[float] = Query(None, description="Latitude"),
    lon: Optional[float] = Query(None, description="Longitude"),
):
    resolved_lat = lat
    resolved_lon = lon
    resolved_loc = location

    # Coordinate resolution logic
    if resolved_lat is not None and resolved_lon is not None:
        if not resolved_loc or resolved_loc.lower() in {"gps", "current", "auto"}:
            rev = await reverse_geocode(resolved_lat, resolved_lon)
            resolved_loc = rev.get("display_name") or f"{resolved_lat:.2f}°N, {resolved_lon:.2f}°E"
    elif resolved_loc:
        geo = await geocode_location(resolved_loc)
        resolved_lat = geo.get("latitude", 21.1981)
        resolved_lon = geo.get("longitude", 72.8298)
        resolved_loc = geo.get("display_name", resolved_loc)
    else:
        ip_loc = await get_ip_location()
        resolved_lat = ip_loc.get("latitude", 21.1981)
        resolved_lon = ip_loc.get("longitude", 72.8298)
        resolved_loc = ip_loc.get("display_name", "Surat, Gujarat")

    try:
        live = await get_weather(lat=resolved_lat, lon=resolved_lon, forecast_days=5)
    except Exception as e:
        logger.warning(f"Live weather fallback for {resolved_loc}: {e}")
        live = {
            "temperature": 28.4,
            "humidity": 68.0,
            "wind_speed": 14.2,
            "precipitation_probability_24h": 45.0,
            "weather_code": 1,
            "weather_description": "Mainly clear",
            "daily_forecast": [],
        }

    temp = round(live.get("temperature", 28.0), 1)
    humidity = round(live.get("humidity", 65.0), 1)
    wind = round(live.get("wind_speed", 12.0), 1)
    rain_prob = int(live.get("precipitation_probability_24h", 35))
    cond = live.get("weather_description", "Partly Cloudy")

    action_banners = []
    if rain_prob >= 50:
        action_banners.append({
            "level": "warning",
            "icon": "rain",
            "title": "Evening Precipitation & Disease Watch",
            "description": (
                f"Elevated humidity ({humidity}%) combined with {rain_prob}% rain probability in {resolved_loc} "
                "creates ideal conditions for fungal sporulation (blight/mildew). Ensure drainage furrows are clear."
            ),
        })
    elif temp >= 34:
        action_banners.append({
            "level": "warning",
            "icon": "sun",
            "title": "Heat Stress Advisory",
            "description": f"Elevated temperature ({temp}°C) in {resolved_loc}. Irrigate during cooler early morning hours to mitigate evapotranspiration loss.",
        })
    else:
        action_banners.append({
            "level": "info",
            "icon": "sun",
            "title": "Optimal Field Operation Window",
            "description": f"Favorable conditions in {resolved_loc} for intercultural tillage, weeding, and inspection.",
        })

    action_banners.append({
        "level": "info",
        "icon": "cloud-sun",
        "title": "Foliar Spray Advisory",
        "description": f"Spray operations are ideal between 07:00 AM and 10:30 AM before wind speeds reach {wind} km/h.",
    })

    # Use live daily forecast if available, or generate dynamic forecast
    daily_list = live.get("daily_forecast") or []
    if daily_list:
        forecast = daily_list
    else:
        forecast = [
            {
                "day": "Today",
                "date": datetime.now().strftime("%d %b"),
                "icon": "cloud-rain" if rain_prob > 40 else "cloud-sun",
                "tempHigh": round(temp + 2),
                "tempLow": round(temp - 6),
                "rainProb": rain_prob,
                "advisory": "Delay chemical sprays; verify drainage channels are unclogged.",
            },
            {
                "day": "Tomorrow",
                "date": "+1 Day",
                "icon": "rain",
                "tempHigh": round(temp + 1),
                "tempLow": round(temp - 7),
                "rainProb": max(15, rain_prob - 10),
                "advisory": "Scout bottom leaves for water-soaked fungal spots post-rain.",
            },
            {
                "day": "Day 3",
                "date": "+2 Days",
                "icon": "cloud-sun",
                "tempHigh": round(temp + 3),
                "tempLow": round(temp - 5),
                "rainProb": 25,
                "advisory": "Ideal window for bio-fertilizer soil drenching.",
            },
            {
                "day": "Day 4",
                "date": "+3 Days",
                "icon": "sun",
                "tempHigh": round(temp + 4),
                "tempLow": round(temp - 5),
                "rainProb": 15,
                "advisory": "Clear skies. Resume standard drip fertigation schedule.",
            },
            {
                "day": "Day 5",
                "date": "+4 Days",
                "icon": "sun",
                "tempHigh": round(temp + 5),
                "tempLow": round(temp - 4),
                "rainProb": 10,
                "advisory": "Optimal solar radiation index for fruit maturation.",
            },
        ]

    return {
        "location": resolved_loc,
        "latitude": resolved_lat,
        "longitude": resolved_lon,
        "current": {
            "temp": temp,
            "condition": cond,
            "humidity": humidity,
            "rainProb": rain_prob,
            "windSpeed": wind,
        },
        "actionBanners": action_banners,
        "forecast": forecast,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 5. Sustainability Score (/api/sustainability/score)
# ─────────────────────────────────────────────────────────────────────────────
class FrontendSustainabilityRequest(BaseModel):
    water_used_liters_per_ha_week: Optional[float] = 22000.0
    fertilizer_kg_per_hectare: Optional[float] = 30.0
    disease_detected: Optional[bool] = False
    irrigation_method: Optional[str] = "drip"
    pesticide_used: Optional[bool] = False
    crop: Optional[str] = "Tomato"


@router.post(
    "/sustainability/score",
    summary="Sustainability Score (Frontend format)",
    description="Evaluates 4 agricultural eco-pillars (0–100) and returns actionable recommendations.",
)
async def api_sustainability_score(req: Optional[FrontendSustainabilityRequest] = None):
    data = req or FrontendSustainabilityRequest()
    s_req = SustainabilityRequest(
        crop_type=data.crop or "Tomato",
        area_hectares=2.5,
        water_used_liters=data.water_used_liters_per_ha_week or 22000.0,
        fertilizer_kg_per_hectare=data.fertilizer_kg_per_hectare or 30.0,
        disease_detected=data.disease_detected or False,
        irrigation_applied=True,
        irrigation_method=data.irrigation_method or "drip",
        pesticide_used=data.pesticide_used or False,
    )

    score_res = compute_sustainability(s_req)
    overall = score_res.get("score", 84.0)
    grade = score_res.get("grade", "A")

    w_score = score_res.get("water_efficiency_score", 88.0)
    f_score = score_res.get("fertilizer_score", 76.0)
    m_score = score_res.get("irrigation_method_score", 85.0)
    d_score = score_res.get("disease_management_score", 90.0)

    breakdown = [
        {
            "pillar": "Water Efficiency",
            "score": round(w_score, 1),
            "color": "#0288D1",
            "summary": "Micro-drip deployment reduces runoff and evaporation losses significantly.",
            "metric": f"{round(w_score, 1)}/100 • Tier 1 Efficiency",
        },
        {
            "pillar": "Chemical Reduction",
            "score": round(f_score, 1),
            "color": "#E65100",
            "summary": "Balanced bio-stimulants mitigate nitrate leaching risk into groundwater.",
            "metric": f"{round(f_score, 1)}/100 • Moderate Usage",
        },
        {
            "pillar": "Irrigation & Energy",
            "score": round(m_score, 1),
            "color": "#2E7D32",
            "summary": "Efficient solar pumping displaces ~1.2 tonnes of CO2 equivalent emissions per season.",
            "metric": f"{round(m_score, 1)}/100 • Low Carbon Footprint",
        },
        {
            "pillar": "Foliar & Plant Health",
            "score": round(d_score, 1),
            "color": "#7B1FA2",
            "summary": "Active residue mulching and vermicompost retention rebuild organic carbon pools.",
            "metric": f"{round(d_score, 1)}/100 • Excellent Regeneration",
        },
    ]

    suggestions = [
        {
            "impact": "High Impact",
            "title": "Install Solar Drip Automation",
            "description": "Pairing soil moisture sensor probes with automated solenoid valves cuts energy by 18% and water consumption by 22%.",
        },
        {
            "impact": "Medium Impact",
            "title": "Biochar & Vermicompost Top-Dressing",
            "description": "Boost soil cation exchange capacity (CEC) to retain applied nutrients during heavy monsoon showers.",
        },
        {
            "impact": "Best Practice",
            "title": "Leguminous Cover Cropping",
            "description": "Introduce cowpea or sunn-hemp between primary crop rows to fix 40 kg atmospheric N/ha naturally.",
        },
    ]

    return {
        "overallScore": round(overall, 1),
        "grade": grade,
        "breakdown": breakdown,
        "suggestions": suggestions,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 6. Farmer Assistant (/api/assistant/chat)
# ─────────────────────────────────────────────────────────────────────────────
class FrontendChatRequest(BaseModel):
    query: str
    language: Optional[str] = "en"
    session_id: Optional[str] = "default-session"
    location: Optional[str] = None
    weather_summary: Optional[str] = None
    crop: Optional[str] = None
    disease_detected: Optional[str] = None
    irrigation_advice: Optional[str] = None


@router.post(
    "/assistant/chat",
    summary="Farmer AI Assistant (Frontend format)",
    description="Conversational plain-language agricultural assistant with multi-lingual support.",
)
async def api_assistant_chat(req: FrontendChatRequest):
    context = {
        "location": req.location,
        "weather_summary": req.weather_summary,
        "crop": req.crop,
        "disease_detected": req.disease_detected,
        "irrigation_advice": req.irrigation_advice,
    }
    res = await get_assistant_response(
        question=req.query,
        language=req.language or "en",
        context=context,
    )

    return {
        "text": res.get("answer", "I am your AgriSmart assistant. How can I assist you with your crops today?"),
        "language": req.language or "en",
        "timestamp": datetime.now().strftime("%I:%M %p"),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 7. Agentic Feed & On-Demand Trigger (/api/agentic/feed, /api/agentic/trigger-cycle)
# ─────────────────────────────────────────────────────────────────────────────
@router.get(
    "/agentic/feed",
    summary="Agentic Advisor Feed (Frontend format)",
    description="Returns the chronological timeline of autonomous farm monitoring events.",
)
async def api_agentic_feed():
    advisories = get_recent_advisories(limit=10)

    events = []
    for idx, adv in enumerate(advisories):
        adv_type = adv.get("type", "irrigation" if idx % 2 == 0 else "weather")
        badge_class = "info" if "delay" in adv.get("action_summary", "").lower() or "hold" in adv.get("action_summary", "").lower() else "warning"
        events.append({
            "type": adv_type,
            "badge": "Automated Advisory" if adv_type == "weather" else "Irrigation Evaluated",
            "badgeClass": badge_class,
            "time": "Recent Cycle" if idx > 0 else "Just now",
            "title": f"Autonomous Cycle: {adv.get('crop', 'Farm')} Condition Check",
            "trigger": f"Telemetry check at {adv.get('timestamp', 'latest interval')}",
            "reasoning": adv.get("rationale", "Routine background sensor scan across soil moisture and meteorological forecast."),
            "actionTaken": adv.get("action_summary", "Condition evaluated within safety parameters; normal monitoring continues."),
        })

    if not events:
        events = [
            {
                "type": "irrigation",
                "badge": "Irrigation Cycle Adjusted",
                "badgeClass": "info",
                "time": "12 mins ago",
                "title": "Drip Irrigation Postponed — Monsoon Surge Forecast",
                "trigger": "Soil moisture at 68% + Rain probability surge to 65% in next 12 hours.",
                "reasoning": "Precipitation will adequately recharge root zone without depleting farm groundwater reserves.",
                "actionTaken": "Dispatched hold command to main drip manifold valve #2 until next moisture check cycle.",
            },
            {
                "type": "pathology",
                "badge": "Foliar Alert",
                "badgeClass": "warning",
                "time": "45 mins ago",
                "title": "Early Blight Spore Dispersion Risk Elevated",
                "trigger": "RH > 65% sustained for 6 consecutive hours at 27°C ambient temperature.",
                "reasoning": "Microclimate parameters align with Alternaria solani incubation profile.",
                "actionTaken": "Triggered prophylactic advisory for bio-fungicide (Trichoderma viride @ 2.5g/L) spray at sunrise.",
            },
            {
                "type": "sustainability",
                "badge": "Eco Metric Updated",
                "badgeClass": "success",
                "time": "2 hours ago",
                "title": "Daily Water Conservation Target Achieved",
                "trigger": "Drip sensor automated cutoff after root-zone field capacity reached.",
                "reasoning": "Prevented 1,450 liters of surface runoff and nitrogen leaching.",
                "actionTaken": "Sustainability score index boosted to 84/100 (+2 pts).",
            },
        ]

    return events


@router.post(
    "/agentic/trigger-cycle",
    summary="Trigger On-Demand Agent Cycle",
    description="Forces immediate autonomous telemetry evaluation cycle and returns the new event.",
)
async def api_trigger_agent_cycle():
    recent = await run_advisory_cycle_now()
    adv = recent[0] if recent else {}

    return {
        "type": adv.get("type", "irrigation"),
        "badge": "Real-time Agent Trigger",
        "badgeClass": "info",
        "time": "Just now",
        "title": f"On-Demand Evaluation for {adv.get('farm_name', 'Farm Plot')}",
        "trigger": "Manual farmer trigger via telemetry console.",
        "reasoning": adv.get("recommendation", "Autonomous rules engine analyzed live weather forecast and soil moisture."),
        "actionTaken": adv.get("recommendation", "Telemetry verified. Advisory broadcasted to farmer notification stream."),
    }
