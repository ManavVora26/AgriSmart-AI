"""
AgriSmart AI — /sustainability Router (Bonus D)
POST /sustainability — Compute sustainability score for farm operations this week.
"""

import logging
from fastapi import APIRouter, HTTPException
from models.schemas import SustainabilityRequest, SustainabilityResponse
from services.sustainability_service import compute_sustainability

router = APIRouter(prefix="/sustainability", tags=["Bonus D — Sustainability Score"])
logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=SustainabilityResponse,
    summary="Compute a reproducible sustainability score for this week's farm operations",
    description=(
        "**Bonus D** — Provide water used, fertilizer applied, disease/irrigation flags, and "
        "irrigation method. Returns a scored sustainability report (0-100, grade A-F) with "
        "the exact formula breakdown and actionable improvement suggestions. "
        "Formula is fully reproducible and published in the response."
    ),
)
async def sustainability(req: SustainabilityRequest):
    try:
        result = compute_sustainability(req)
        return SustainabilityResponse(**result)
    except Exception as e:
        logger.exception("Sustainability scoring error")
        raise HTTPException(status_code=500, detail=f"Sustainability scoring failed: {str(e)}")
