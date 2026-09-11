"""
AgriSmart AI — /weather-advice Router (Bonus C)
GET /weather-advice — Location-based weather + farm condition actions.
"""

import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Query, HTTPException
from models.schemas import WeatherAdviceResponse
from services.weather_service import get_weather, generate_weather_actions

router = APIRouter(prefix="/weather-advice", tags=["Bonus C — Weather Intelligence"])
logger = logging.getLogger(__name__)


@router.get(
    "",
    response_model=WeatherAdviceResponse,
    summary="Get weather-based farming actions for your location",
    description=(
        "**Bonus C** — Provide GPS coordinates and optional crop type. "
        "Returns live weather data from Open-Meteo plus actionable advice such as "
        "'delay irrigation — rain likely' or 'raised disease risk — monitor crops'. "
        "Data source: Open-Meteo (open-meteo.com, no API key required)."
    ),
)
async def weather_advice(
    lat: float = Query(..., description="Farm latitude (e.g. 23.03 for Ahmedabad)", ge=-90, le=90),
    lon: float = Query(..., description="Farm longitude (e.g. 72.59 for Ahmedabad)", ge=-180, le=180),
    crop: str = Query(None, description="Crop type for crop-specific advice (e.g. 'Tomato')"),
):
    try:
        weather = await get_weather(lat, lon)
        actions, disease_risk, disease_risk_reason = generate_weather_actions(weather, crop)

        location_str = f"Lat {lat:.4f}, Lon {lon:.4f}"
        if crop:
            location_str += f" | Crop: {crop}"

        return WeatherAdviceResponse(
            location=location_str,
            temperature=weather["temperature"],
            humidity=weather["humidity"],
            precipitation_probability=weather["precipitation_probability_24h"],
            wind_speed=weather["wind_speed"],
            weather_description=weather["weather_description"],
            actions=actions,
            disease_risk=disease_risk,
            disease_risk_reason=disease_risk_reason,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
    except Exception as e:
        logger.exception("Weather advice error")
        raise HTTPException(status_code=500, detail=f"Weather advice failed: {str(e)}")
