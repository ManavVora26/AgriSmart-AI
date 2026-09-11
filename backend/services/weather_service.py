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


async def get_weather(lat: float, lon: float, forecast_days: int = 5) -> dict:
    """
    Fetch current weather + 5-day forecast from Open-Meteo.
    Returns structured current telemetry, hourly rain probabilities, and 5-day daily forecasts.
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
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_probability_max",
            "weather_code",
        ],
        "forecast_days": min(forecast_days, 7),
        "timezone": "auto",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(OPEN_METEO_BASE, params=params)
            resp.raise_for_status()
            data = resp.json()

        current = data.get("current", {})
        hourly = data.get("hourly", {})
        daily = data.get("daily", {})

        # Max precipitation probability in the next 24 hours
        precip_probs = hourly.get("precipitation_probability", [0])
        max_rain_prob_24h = max(precip_probs[:24]) if precip_probs else 0

        wmo_code = current.get("weather_code", 0)
        description = WMO_CODES.get(wmo_code, "Partly Cloudy")

        # Parse daily 5-day forecast
        daily_forecast = []
        times = daily.get("time", [])
        t_max = daily.get("temperature_2m_max", [])
        t_min = daily.get("temperature_2m_min", [])
        p_max = daily.get("precipitation_probability_max", [])
        codes = daily.get("weather_code", [])

        day_names = ["Today", "Tomorrow", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"]
        for idx in range(min(len(times), forecast_days)):
            code_i = codes[idx] if idx < len(codes) else 0
            d_rain = int(p_max[idx]) if idx < len(p_max) and p_max[idx] is not None else 10
            daily_forecast.append({
                "day": day_names[idx] if idx < len(day_names) else f"Day {idx+1}",
                "date": times[idx] if idx < len(times) else f"+{idx}d",
                "tempHigh": round(t_max[idx]) if idx < len(t_max) and t_max[idx] is not None else 30,
                "tempLow": round(t_min[idx]) if idx < len(t_min) and t_min[idx] is not None else 22,
                "rainProb": d_rain,
                "weatherCode": code_i,
                "description": WMO_CODES.get(code_i, "Partly Cloudy"),
                "advisory": (
                    "Delay chemical sprays; verify drainage channels." if d_rain > 50
                    else "Scout bottom leaves for water-soaked spots." if d_rain > 30
                    else "Clear skies. Standard drip fertigation recommended."
                )
            })

        return {
            "temperature": round(current.get("temperature_2m", 25.0), 1),
            "humidity": round(current.get("relative_humidity_2m", 60.0), 1),
            "precipitation_mm": round(current.get("precipitation", 0.0), 2),
            "precipitation_probability_24h": float(max_rain_prob_24h),
            "wind_speed": round(current.get("wind_speed_10m", 0.0), 1),
            "weather_code": wmo_code,
            "weather_description": description,
            "daily_forecast": daily_forecast,
            "source": "Open-Meteo (open-meteo.com)",
            "fetched_at": datetime.utcnow().isoformat() + "Z",
        }

    except httpx.HTTPError as e:
        logger.error(f"Open-Meteo API error: {e}")
        # Return safe fallback values so downstream endpoints still respond
        return {
            "temperature": 26.5,
            "humidity": 65.0,
            "precipitation_mm": 0.0,
            "precipitation_probability_24h": 35.0,
            "wind_speed": 10.0,
            "weather_code": 1,
            "weather_description": "Mainly clear",
            "daily_forecast": [],
            "source": "Fallback (Open-Meteo unreachable)",
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "error": str(e),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Location Utilities: Geocoding, Reverse Geocoding & IP Auto-Detection
# ─────────────────────────────────────────────────────────────────────────────
POPULAR_AGRI_HUBS = {
    "surat": {"lat": 21.1981, "lon": 72.8298, "name": "Surat", "state": "Gujarat", "country": "India"},
    "nashik": {"lat": 19.9975, "lon": 73.7898, "name": "Nashik", "state": "Maharashtra", "country": "India"},
    "pune": {"lat": 18.5204, "lon": 73.8567, "name": "Pune", "state": "Maharashtra", "country": "India"},
    "mumbai": {"lat": 19.0760, "lon": 72.8777, "name": "Mumbai", "state": "Maharashtra", "country": "India"},
    "ahmedabad": {"lat": 23.0225, "lon": 72.5714, "name": "Ahmedabad", "state": "Gujarat", "country": "India"},
    "rajkot": {"lat": 22.3039, "lon": 70.8022, "name": "Rajkot", "state": "Gujarat", "country": "India"},
    "ludhiana": {"lat": 30.9010, "lon": 75.8573, "name": "Ludhiana", "state": "Punjab", "country": "India"},
    "karnal": {"lat": 29.6857, "lon": 76.9905, "name": "Karnal", "state": "Haryana", "country": "India"},
    "nagpur": {"lat": 21.1458, "lon": 79.0882, "name": "Nagpur", "state": "Maharashtra", "country": "India"},
    "shimla": {"lat": 31.1048, "lon": 77.1734, "name": "Shimla", "state": "Himachal Pradesh", "country": "India"},
    "delhi": {"lat": 28.6139, "lon": 77.2090, "name": "Delhi", "state": "Delhi", "country": "India"},
    "bengaluru": {"lat": 12.9716, "lon": 77.5946, "name": "Bengaluru", "state": "Karnataka", "country": "India"},
    "hyderabad": {"lat": 17.3850, "lon": 78.4867, "name": "Hyderabad", "state": "Telangana", "country": "India"},
    "varanasi": {"lat": 25.3176, "lon": 82.9739, "name": "Varanasi", "state": "Uttar Pradesh", "country": "India"},
}


async def geocode_location(query: str) -> dict:
    """
    Geocode a location query (e.g. city name, district, or 'lat,lon' string) into coordinates.
    """
    if not query or not query.strip():
        return POPULAR_AGRI_HUBS["surat"]

    q_clean = query.strip()

    # Check if coords entered directly "21.1981, 72.8298"
    if "," in q_clean:
        parts = q_clean.split(",")
        try:
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())
            rev = await reverse_geocode(lat, lon)
            return {
                "name": rev.get("city") or "Custom Coordinates",
                "state": rev.get("state") or "",
                "country": rev.get("country") or "India",
                "latitude": lat,
                "longitude": lon,
                "display_name": rev.get("display_name") or f"{lat:.4f}°N, {lon:.4f}°E",
            }
        except (ValueError, IndexError):
            pass

    # Check local fast dictionary
    q_lower = q_clean.lower().split(",")[0].strip()
    if q_lower in POPULAR_AGRI_HUBS:
        hub = POPULAR_AGRI_HUBS[q_lower]
        return {
            "name": hub["name"],
            "state": hub["state"],
            "country": hub["country"],
            "latitude": hub["lat"],
            "longitude": hub["lon"],
            "display_name": f"{hub['name']}, {hub['state']}, {hub['country']}",
        }

    # Query Open-Meteo Free Geocoding API
    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": q_clean, "count": 1, "language": "en", "format": "json"}
            )
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results")
                if results and len(results) > 0:
                    top = results[0]
                    name = top.get("name", q_clean)
                    admin1 = top.get("admin1", "")
                    country = top.get("country", "India")
                    display = f"{name}, {admin1}" if admin1 else name
                    if country:
                        display += f", {country}"
                    return {
                        "name": name,
                        "state": admin1,
                        "country": country,
                        "latitude": float(top.get("latitude")),
                        "longitude": float(top.get("longitude")),
                        "display_name": display,
                    }
    except Exception as e:
        logger.warning(f"Geocoding API error: {e}")

    # Fallback to Surat
    fallback = POPULAR_AGRI_HUBS["surat"]
    return {
        "name": fallback["name"],
        "state": fallback["state"],
        "country": fallback["country"],
        "latitude": fallback["lat"],
        "longitude": fallback["lon"],
        "display_name": f"{fallback['name']}, {fallback['state']}",
    }


async def reverse_geocode(lat: float, lon: float) -> dict:
    """
    Reverse geocode coordinates into a human-friendly placename (city, state, country).
    """
    # Try Nominatim with custom User-Agent
    try:
        async with httpx.AsyncClient(headers={"User-Agent": "AgriSmartAI/1.0"}, timeout=5.0) as client:
            resp = await client.get(
                "https://nominatim.openstreetmap.org/reverse",
                params={"lat": lat, "lon": lon, "format": "json", "zoom": 12}
            )
            if resp.status_code == 200:
                data = resp.json()
                addr = data.get("address", {})
                city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("suburb") or addr.get("county") or "Local Farm"
                state = addr.get("state", "")
                country = addr.get("country", "India")
                display = f"{city}, {state}" if state else city
                return {
                    "city": city,
                    "state": state,
                    "country": country,
                    "display_name": display,
                    "latitude": lat,
                    "longitude": lon,
                }
    except Exception as e:
        logger.warning(f"Reverse geocode error: {e}")

    return {
        "city": "Current Farm Station",
        "state": "",
        "country": "India",
        "display_name": f"{lat:.3f}°N, {lon:.3f}°E",
        "latitude": lat,
        "longitude": lon,
    }


async def get_ip_location() -> dict:
    """
    Auto-detect approximate farm location from IP address.
    """
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get("http://ip-api.com/json/")
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    city = data.get("city", "Surat")
                    state = data.get("regionName", "Gujarat")
                    country = data.get("country", "India")
                    return {
                        "city": city,
                        "state": state,
                        "country": country,
                        "latitude": float(data.get("lat", 21.1981)),
                        "longitude": float(data.get("lon", 72.8298)),
                        "display_name": f"{city}, {state}, {country}",
                        "source": "IP Geolocation",
                    }
    except Exception as e:
        logger.warning(f"IP location error: {e}")

    fallback = POPULAR_AGRI_HUBS["surat"]
    return {
        "city": fallback["name"],
        "state": fallback["state"],
        "country": fallback["country"],
        "latitude": fallback["lat"],
        "longitude": fallback["lon"],
        "display_name": f"{fallback['name']}, {fallback['state']}",
        "source": "Default Preset",
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
