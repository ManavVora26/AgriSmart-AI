"""
AgriSmart AI — /recommend-crop Router (Bonus A)
POST /recommend-crop — Soil/pH/climate inputs → recommended crop.
"""

import logging
from fastapi import APIRouter, HTTPException
from models.schemas import CropRecommendRequest, CropRecommendResponse
from services.crop_service import recommend_crop

router = APIRouter(prefix="/recommend-crop", tags=["Bonus A — Crop Recommendation"])
logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=CropRecommendResponse,
    summary="Recommend a suitable crop based on soil and climate data",
    description=(
        "**Bonus A** — Provide soil type, pH, temperature, humidity, rainfall, and season "
        "to get a data-driven crop recommendation. "
        "Optionally include the previous crop for rotation advice."
    ),
)
async def crop_recommendation(req: CropRecommendRequest):
    try:
        result = recommend_crop(req)
        return CropRecommendResponse(**result)
    except Exception as e:
        logger.exception("Crop recommendation error")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")
