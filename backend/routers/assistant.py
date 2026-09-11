"""
AgriSmart AI — /assistant Router (Bonus E)
POST /assistant — Farmer Q&A powered by Google Gemini with grounded context.
"""

import logging
from fastapi import APIRouter, HTTPException
from models.schemas import AssistantRequest, AssistantResponse
from services.assistant_service import get_assistant_response

router = APIRouter(prefix="/assistant", tags=["Bonus E — Farmer Assistant (GenAI)"])
logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {"en", "hi", "gu", "mr", "pa", "te", "ta", "kn", "bn", "or"}


@router.post(
    "",
    response_model=AssistantResponse,
    summary="Ask the AI farming assistant a question",
    description=(
        "**Bonus E** — Ask any farming question in plain language. "
        "Optionally provide context (disease detected, crop, weather, irrigation advice, sustainability score) "
        "for grounded, more accurate answers. "
        "Supports English and 8 Indian regional languages. "
        "Powered by Google Gemini with grounded prompting."
    ),
)
async def assistant(req: AssistantRequest):
    if req.language and req.language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language '{req.language}'. "
                   f"Supported: {sorted(SUPPORTED_LANGUAGES)}",
        )
    try:
        result = await get_assistant_response(
            question=req.question,
            context=req.context,
            language=req.language or "en",
        )
        return AssistantResponse(**result)
    except Exception as e:
        logger.exception("Assistant error")
        raise HTTPException(status_code=500, detail=f"Assistant failed: {str(e)}")
