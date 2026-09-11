"""
AgriSmart AI — Farmer Assistant Service (Bonus E)
Provides grounded, plain-language answers using Google Gemini API.

"Grounded" means: the LLM is given the actual model outputs (disease name,
irrigation advice, weather summary, sustainability score) as context.
This is explicitly required by the problem statement:
  "Grounded answers score higher than free-form generation."
"""

import os
import logging
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Language display names for prompt
LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi (हिंदी)",
    "gu": "Gujarati (ગુજરાતી)",
    "mr": "Marathi (मराठी)",
    "pa": "Punjabi (ਪੰਜਾਬੀ)",
    "te": "Telugu (తెలుగు)",
    "ta": "Tamil (தமிழ்)",
    "kn": "Kannada (ಕನ್ನಡ)",
    "bn": "Bengali (বাংলা)",
    "or": "Odia (ଓଡ଼ିଆ)",
}


def _build_system_prompt(context: Optional[dict], language: str) -> str:
    """Build the grounded system prompt for Gemini."""
    lang_name = LANGUAGE_NAMES.get(language, "English")

    context_str = ""
    sources_used = []

    if context:
        parts = []
        if context.get("disease_detected"):
            parts.append(f"- Disease detected: {context['disease_detected']}")
            sources_used.append("disease detection result")
        if context.get("crop"):
            parts.append(f"- Crop type: {context['crop']}")
            sources_used.append("crop type")
        if context.get("weather_summary"):
            parts.append(f"- Current weather: {context['weather_summary']}")
            sources_used.append("live weather data")
        if context.get("irrigation_advice"):
            parts.append(f"- Irrigation recommendation: {context['irrigation_advice']}")
            sources_used.append("irrigation model output")
        if context.get("sustainability_score") is not None:
            parts.append(f"- Sustainability score: {context['sustainability_score']}/100")
            sources_used.append("sustainability score")

        if parts:
            context_str = "\n\nCurrent farm data:\n" + "\n".join(parts)

    system_prompt = f"""You are AgriBot, an expert agricultural AI assistant for Indian farmers.
Your role is to give clear, practical, and trustworthy advice about crop diseases, irrigation,
weather, and sustainable farming practices.

Guidelines:
1. Always ground your answers in the farm data provided below (if any). DO NOT contradict it.
2. If no farm data is provided, give general best-practice advice.
3. Use simple language a farmer can understand — avoid jargon.
4. Be concise but complete. Give specific action steps.
5. Respond ONLY in {lang_name}.
6. If you don't know something, say so honestly and suggest consulting a local agricultural extension officer.
{context_str}

You are a trusted advisor, not a salesperson. Prioritize the farmer's crop health and livelihood.
"""
    return system_prompt, sources_used


async def get_assistant_response(
    question: str,
    context: Optional[object],
    language: str = "en",
) -> dict:
    """
    Get a grounded response from Google Gemini.

    Args:
        question: The farmer's question
        context: AssistantContext pydantic object (optional)
        language: BCP-47 language code

    Returns:
        Dict with answer, language, grounded flag, sources_used
    """
    ctx_dict = None
    if context:
        ctx_dict = {
            "disease_detected": context.disease_detected,
            "crop": context.crop,
            "weather_summary": context.weather_summary,
            "irrigation_advice": context.irrigation_advice,
            "sustainability_score": context.sustainability_score,
        }

    system_prompt, sources_used = _build_system_prompt(ctx_dict, language)
    grounded = bool(sources_used)

    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set — returning mock assistant response.")
        return _mock_response(question, language, grounded, sources_used)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(system_instruction=system_prompt),
            contents=question,
        )
        answer = response.text.strip()

        return {
            "answer": answer,
            "language": language,
            "grounded": grounded,
            "sources_used": sources_used if sources_used else ["general agricultural knowledge"],
        }

    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return {
            "answer": (
                f"I apologize, the AI assistant is temporarily unavailable. "
                f"Error: {str(e)[:100]}. "
                f"Please consult your local Krishi Vigyan Kendra (KVK) or agricultural extension officer."
            ),
            "language": language,
            "grounded": grounded,
            "sources_used": sources_used,
        }


def _mock_response(question: str, language: str, grounded: bool, sources: list) -> dict:
    """Fallback mock response when API key is not configured."""
    answer = (
        f"[Mock Response — Set GEMINI_API_KEY in .env for real AI answers]\n\n"
        f"Your question: '{question}'\n\n"
        f"As AgriBot, I would analyze the following data: {', '.join(sources) if sources else 'your general farming context'}. "
        f"Based on best practices, I recommend:\n"
        f"1. Monitor your crops daily for early signs of disease.\n"
        f"2. Follow the irrigation schedule recommended by the irrigation module.\n"
        f"3. Consult your local agricultural extension officer for region-specific advice.\n"
        f"4. Keep records of disease occurrences and weather patterns.\n"
        f"5. Use certified disease-free seeds and practice crop rotation annually."
    )
    return {
        "answer": answer,
        "language": language,
        "grounded": grounded,
        "sources_used": sources if sources else ["general agricultural knowledge (mock)"],
    }
