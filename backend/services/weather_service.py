"""
AgriSmart AI — Weather Service
Integrates with Open-Meteo API (no API key required).
Provides current + 24h forecast data for /weather-advice and /irrigation endpoints.
"""

import logging
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)

OPEN_METEO_BASE = "https://api.open-meteo.com/v1/forecast"

# WMO Weather interpretation codes → plain descriptions
WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
}


async def get_weather(lat: float, lon: float) -> dict:
    """
    Fetch current weather + 24-hour forecast from Open-Meteo.
    Returns a structured dict with temperature, humidity, precipitation probability,
    wind speed, WMO weather code, and description.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "weather_code",
            "wind_speed_10m",
        ],
        "hourly": [
            "precipitation_probability",
            "temperature_2m",
        ],
        "forecast_days": 2,
        "timezone": "auto",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(OPEN_METEO_BASE, params=params)
            resp.raise_for_status()
            data = resp.json()

        current = data.get("current", {})
        hourly = data.get("hourly", {})

        # Max precipitation probability in the next 24 hours
        precip_probs = hourly.get("precipitation_probability", [0])
        max_rain_prob_24h = max(precip_probs[:24]) if precip_probs else 0

        wmo_code = current.get("weather_code", 0)
        description = WMO_CODES.get(wmo_code, "Unknown")

        return {
            "temperature": round(current.get("temperature_2m", 25.0), 1),
            "humidity": round(current.get("relative_humidity_2m", 60.0), 1),
            "precipitation_mm": round(current.get("precipitation", 0.0), 2),
            "precipitation_probability_24h": float(max_rain_prob_24h),
            "wind_speed": round(current.get("wind_speed_10m", 0.0), 1),
            "weather_code": wmo_code,
            "weather_description": description,
            "source": "Open-Meteo (open-meteo.com)",
            "fetched_at": datetime.utcnow().isoformat() + "Z",
        }

    except httpx.HTTPError as e:
        logger.error(f"Open-Meteo API error: {e}")
        # Return safe fallback values so downstream endpoints still respond
        return {
            "temperature": 25.0,
            "humidity": 60.0,
            "precipitation_mm": 0.0,
            "precipitation_probability_24h": 30.0,
            "wind_speed": 10.0,
            "weather_code": 0,
            "weather_description": "Data unavailable",
            "source": "Fallback (Open-Meteo unreachable)",
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "error": str(e),
        }


def generate_weather_actions(weather: dict, crop: str | None = None) -> tuple[list[str], str, str]:
    """
    Generate actionable farm advice from weather data.
    Returns: (actions_list, disease_risk_level, disease_risk_reason)
    """
    actions = []
    rain_prob = weather["precipitation_probability_24h"]
    temp = weather["temperature"]
    humidity = weather["humidity"]
    wind = weather["wind_speed"]

    # ── Irrigation advice ──────────────────────────────────────────────────
    if rain_prob >= 70:
        actions.append(f"Delay irrigation — rainfall likely in next 24 h ({rain_prob:.0f}% probability).")
    elif rain_prob >= 40:
        actions.append(f"Monitor soil moisture — moderate rain possible ({rain_prob:.0f}% probability).")
    else:
        actions.append("No significant rain expected. Irrigate as per crop schedule.")

    # ── Temperature stress ──────────────────────────────────────────────────
    if temp > 38:
        actions.append(f"ALERT: Extreme heat ({temp}°C). Consider shade nets; irrigate in early morning.")
    elif temp > 33:
        actions.append(f"High temperature ({temp}°C). Water stress likely — check soil moisture frequently.")
    elif temp < 10:
        actions.append(f"Cold weather ({temp}°C). Protect sensitive crops from frost damage.")

    # ── Wind ─────────────────────────────────────────────────────────────────
    if wind > 40:
        actions.append(f"Strong winds ({wind} km/h). Avoid spraying pesticides/fungicides today.")

    # ── Fungal disease risk from humidity + temp ──────────────────────────
    if humidity >= 85 and 15 <= temp <= 28:
        risk = "high"
        risk_reason = (
            f"High humidity ({humidity}%) and temperature ({temp}°C) create ideal conditions "
            "for late blight, leaf mould, and other fungal diseases."
        )
        actions.append("High fungal disease risk! Inspect plants closely; apply preventive fungicide.")
    elif humidity >= 70 and temp <= 32:
        risk = "moderate"
        risk_reason = f"Moderate humidity ({humidity}%) and temperature ({temp}°C) — some disease pressure possible."
        actions.append("Moderate disease risk. Monitor for early signs of leaf spots or mould.")
    else:
        risk = "low"
        risk_reason = f"Current humidity ({humidity}%) and temperature ({temp}°C) are not strongly conducive to disease spread."

    # ── Crop-specific advice ──────────────────────────────────────────────
    if crop:
        crop_lower = crop.lower()
        if "tomato" in crop_lower and humidity >= 80:
            actions.append("Tomato-specific: High humidity increases Late Blight risk — check undersides of leaves.")
        elif "potato" in crop_lower and humidity >= 80:
            actions.append("Potato-specific: Watch for water-soaked lesions indicative of Late Blight.")
        elif "rice" in crop_lower or "paddy" in crop_lower:
            actions.append("Rice-specific: Monitor water levels in paddy fields after heavy rain.")

    return actions, risk, risk_reason
