"""
AgriSmart AI — Pydantic Schemas
All request/response models for the FastAPI backend.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────────────
# /predict  (Core — Crop Disease Detection)
# ─────────────────────────────────────────────────────────────────────────────

class PredictionResponse(BaseModel):
    """Response from POST /predict"""
    label: str = Field(..., description="Internal class label, e.g. 'Tomato___Early_Blight'")
    display_name: str = Field(..., description="Human-readable disease name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence score")
    is_healthy: bool = Field(..., description="True if plant is detected as healthy")
    precaution: str = Field(..., description="Actionable precaution text for the farmer")
    timestamp: str = Field(..., description="ISO 8601 timestamp of the prediction")
    model_mode: str = Field(..., description="'mock' or 'real'")


# ─────────────────────────────────────────────────────────────────────────────
# /recommend-crop  (Bonus A)
# ─────────────────────────────────────────────────────────────────────────────

class CropRecommendRequest(BaseModel):
    """Request body for POST /recommend-crop"""
    soil_type: str = Field(..., description="e.g. 'Loamy', 'Sandy', 'Clay', 'Silty', 'Peaty'")
    pH: float = Field(..., ge=3.0, le=10.0, description="Soil pH value")
    temperature: float = Field(..., description="Average temperature in °C")
    humidity: float = Field(..., ge=0.0, le=100.0, description="Relative humidity %")
    rainfall: float = Field(..., ge=0.0, description="Annual rainfall in mm")
    season: str = Field(..., description="e.g. 'Kharif', 'Rabi', 'Zaid', 'Summer', 'Winter'")
    location: Optional[str] = Field(None, description="Region or state name")
    previous_crop: Optional[str] = Field(None, description="Previous crop grown for rotation advice")
    water_availability: Optional[str] = Field("moderate", description="'low', 'moderate', 'high'")

    model_config = {
        "json_schema_extra": {
            "example": {
                "soil_type": "Loamy",
                "pH": 6.5,
                "temperature": 28.0,
                "humidity": 65.0,
                "rainfall": 800.0,
                "season": "Kharif",
                "location": "Gujarat",
                "previous_crop": "Wheat",
                "water_availability": "moderate",
            }
        }
    }


class CropRecommendResponse(BaseModel):
    recommended_crop: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    alternative_crops: List[str]
    rotation_note: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# /irrigation  (Bonus B)
# ─────────────────────────────────────────────────────────────────────────────

class IrrigationRequest(BaseModel):
    """Request body for POST /irrigation"""
    soil_moisture: float = Field(..., ge=0.0, le=100.0, description="Current soil moisture %")
    crop_type: str = Field(..., description="e.g. 'Tomato', 'Wheat', 'Rice'")
    growth_stage: str = Field(..., description="e.g. 'Seedling', 'Vegetative', 'Flowering', 'Fruiting', 'Maturity'")
    lat: float = Field(..., description="Farm latitude for weather lookup")
    lon: float = Field(..., description="Farm longitude for weather lookup")

    model_config = {
        "json_schema_extra": {
            "example": {
                "soil_moisture": 31.0,
                "crop_type": "Tomato",
                "growth_stage": "Flowering",
                "lat": 23.03,
                "lon": 72.59,
            }
        }
    }


class IrrigationResponse(BaseModel):
    irrigate: bool = Field(..., description="True = irrigate now, False = hold off")
    recommendation: str = Field(..., description="Plain-language recommendation")
    reasoning: str = Field(..., description="Detailed reasoning")
    soil_moisture: float
    rain_probability_24h: float
    temperature: float
    water_stress_level: str = Field(..., description="'none', 'low', 'moderate', 'high', 'critical'")


# ─────────────────────────────────────────────────────────────────────────────
# /weather-advice  (Bonus C)
# ─────────────────────────────────────────────────────────────────────────────

class WeatherAdviceResponse(BaseModel):
    location: str
    temperature: float
    humidity: float
    precipitation_probability: float
    wind_speed: float
    weather_description: str
    actions: List[str] = Field(..., description="Actionable farm advice based on weather")
    disease_risk: str = Field(..., description="'low', 'moderate', 'high'")
    disease_risk_reason: str
    timestamp: str


# ─────────────────────────────────────────────────────────────────────────────
# /sustainability  (Bonus D)
# ─────────────────────────────────────────────────────────────────────────────

class SustainabilityRequest(BaseModel):
    """Request body for POST /sustainability"""
    water_used_liters: float = Field(..., ge=0.0, description="Water used in liters this week")
    crop_type: str = Field(..., description="Crop being grown")
    area_hectares: float = Field(..., gt=0.0, description="Farm area in hectares")
    fertilizer_kg_per_hectare: float = Field(..., ge=0.0, description="Fertilizer applied kg/ha")
    pesticide_used: bool = Field(..., description="Was pesticide used this week?")
    disease_detected: bool = Field(..., description="Was disease detected this week?")
    irrigation_applied: bool = Field(..., description="Was irrigation applied this week?")
    irrigation_method: Optional[str] = Field("flood", description="'drip', 'sprinkler', 'flood', 'furrow'")

    model_config = {
        "json_schema_extra": {
            "example": {
                "water_used_liters": 5000.0,
                "crop_type": "Tomato",
                "area_hectares": 1.0,
                "fertilizer_kg_per_hectare": 40.0,
                "pesticide_used": False,
                "disease_detected": True,
                "irrigation_applied": True,
                "irrigation_method": "drip",
            }
        }
    }


class SustainabilityResponse(BaseModel):
    score: float = Field(..., ge=0.0, le=100.0, description="Sustainability score 0-100")
    grade: str = Field(..., description="'A', 'B', 'C', 'D', 'F'")
    water_efficiency_score: float
    fertilizer_score: float
    disease_management_score: float
    irrigation_method_score: float
    improvement_suggestions: List[str]
    formula_breakdown: dict = Field(..., description="Exact formula values for reproducibility")


# ─────────────────────────────────────────────────────────────────────────────
# /assistant  (Bonus E)
# ─────────────────────────────────────────────────────────────────────────────

class AssistantContext(BaseModel):
    """Optional farming context to ground the LLM response."""
    disease_detected: Optional[str] = None
    crop: Optional[str] = None
    weather_summary: Optional[str] = None
    irrigation_advice: Optional[str] = None
    sustainability_score: Optional[float] = None


class AssistantRequest(BaseModel):
    question: str = Field(..., description="Farmer's question in plain language")
    context: Optional[AssistantContext] = None
    language: Optional[str] = Field("en", description="Response language code: 'en', 'hi', 'gu', 'mr', 'pa', 'te', 'ta', 'kn'")

    model_config = {
        "json_schema_extra": {
            "example": {
                "question": "My tomato leaves have brown spots. What should I do?",
                "context": {
                    "disease_detected": "Tomato Early Blight",
                    "crop": "Tomato",
                    "weather_summary": "Humid, 28°C, 70% rain probability",
                },
                "language": "en",
            }
        }
    }


class AssistantResponse(BaseModel):
    answer: str = Field(..., description="Grounded, plain-language answer from the AI assistant")
    language: str
    grounded: bool = Field(..., description="True if answer is grounded in actual model/weather data")
    sources_used: List[str] = Field(..., description="What data was used to ground the answer")


# ─────────────────────────────────────────────────────────────────────────────
# Shared / Health Check
# ─────────────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    model_mode: str
    endpoints: List[str]
