"""
AgriSmart AI — /irrigation Router (Bonus B)
POST /irrigation — Soil moisture + weather forecast + crop stage → irrigate Y/N.
"""

import logging
from fastapi import APIRouter, HTTPException
from models.schemas import IrrigationRequest, IrrigationResponse
from services.weather_service import get_weather
from services.irrigation_service import decide_irrigation

router = APIRouter(prefix="/irrigation", tags=["Bonus B — Smart Irrigation"])
logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=IrrigationResponse,
    summary="Predict whether irrigation is required",
    description=(
        "**Bonus B** — Provide soil moisture %, crop type, growth stage, and farm GPS coordinates. "
        "The API fetches live weather from Open-Meteo and returns an irrigation recommendation "
        "based on FAO-56 soil moisture thresholds and 24-hour rain forecast."
    ),
)
async def irrigation_prediction(req: IrrigationRequest):
    try:
        weather = await get_weather(req.lat, req.lon)
        result = decide_irrigation(
            soil_moisture=req.soil_moisture,
            crop_type=req.crop_type,
            growth_stage=req.growth_stage,
            weather=weather,
        )
        return IrrigationResponse(
            irrigate=result["irrigate"],
            recommendation=result["recommendation"],
            reasoning=result["reasoning"],
            soil_moisture=result["soil_moisture"],
            rain_probability_24h=result["rain_probability_24h"],
            temperature=result["temperature"],
            water_stress_level=result["water_stress_level"],
        )
    except Exception as e:
        logger.exception("Irrigation prediction error")
        raise HTTPException(status_code=500, detail=f"Irrigation prediction failed: {str(e)}")
