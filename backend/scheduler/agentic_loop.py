"""
AgriSmart AI — Agentic Advisor Scheduler (Bonus G)
An autonomous agent that continuously analyses inputs, reasons,
checks weather/data, decides, and notifies the farmer.

Runs as a background APScheduler job every 30 minutes.
Each cycle:
  1. Fetch weather for a configured farm location
  2. Evaluate disease risk from weather conditions
  3. Check irrigation threshold against last known soil moisture
  4. Generate a consolidated advisory
  5. Log the advisory (in production: push to DB, send SMS/notification)

This demonstrates the "decision loop" required by Bonus G:
  weather check → reasoning → recommendation → notification
"""

import logging
import asyncio
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

logger = logging.getLogger(__name__)

# ─── Demo farm config (replace with real farm DB in production) ───────────────
DEMO_FARMS = [
    {
        "farm_id": "DEMO_FARM_001",
        "name": "Ramesh Patel's Tomato Farm",
        "lat": 23.0225,    # Ahmedabad, Gujarat
        "lon": 72.5714,
        "crop": "Tomato",
        "growth_stage": "Flowering",
        "soil_moisture": 42.0,  # Would come from sensor/IoT feed in production
    },
    {
        "farm_id": "DEMO_FARM_002",
        "name": "Sunita Devi's Potato Field",
        "lat": 28.6139,    # Delhi region
        "lon": 77.2090,
        "crop": "Potato",
        "growth_stage": "Vegetative",
        "soil_moisture": 55.0,
    },
]

# Advisory log (in-memory; production would write to DB)
_advisory_log: list[dict] = []


async def _run_advisory_cycle():
    """
    Core agentic loop logic — runs once per schedule tick.
    Fetches weather, evaluates all farms, generates advisories.
    """
    from services.weather_service import get_weather, generate_weather_actions
    from services.irrigation_service import decide_irrigation

    tick_time = datetime.now(timezone.utc).isoformat()
    logger.info(f"[AgentLoop] Tick at {tick_time} — analysing {len(DEMO_FARMS)} farm(s)...")

    for farm in DEMO_FARMS:
        try:
            # Step 1: Fetch live weather
            weather = await get_weather(farm["lat"], farm["lon"])

            # Step 2: Generate weather actions + disease risk
            actions, disease_risk, disease_risk_reason = generate_weather_actions(
                weather, farm["crop"]
            )

            # Step 3: Evaluate irrigation need
            irrigation = decide_irrigation(
                soil_moisture=farm["soil_moisture"],
                crop_type=farm["crop"],
                growth_stage=farm["growth_stage"],
                weather=weather,
            )

            # Step 4: Build consolidated advisory
            advisory = {
                "farm_id": farm["farm_id"],
                "farm_name": farm["name"],
                "timestamp": tick_time,
                "crop": farm["crop"],
                "growth_stage": farm["growth_stage"],
                "weather": {
                    "temperature": weather["temperature"],
                    "humidity": weather["humidity"],
                    "rain_probability_24h": weather["precipitation_probability_24h"],
                    "description": weather["weather_description"],
                },
                "disease_risk": disease_risk,
                "disease_risk_reason": disease_risk_reason,
                "irrigation": {
                    "irrigate": irrigation["irrigate"],
                    "recommendation": irrigation["recommendation"],
                    "water_stress": irrigation["water_stress_level"],
                },
                "actions": actions,
                "alert_level": _determine_alert_level(disease_risk, irrigation),
            }

            # Step 5: Log advisory
            _advisory_log.append(advisory)
            if len(_advisory_log) > 200:  # cap memory usage
                _advisory_log.pop(0)

            alert = advisory["alert_level"]
            logger.info(
                f"[AgentLoop] {farm['name']} | "
                f"Disease risk: {disease_risk} | "
                f"Irrigate: {irrigation['irrigate']} | "
                f"Alert: {alert}"
            )

            # In production: send SMS/push notification if alert == "HIGH"
            if alert == "HIGH":
                logger.warning(
                    f"[AgentLoop] 🚨 HIGH ALERT for {farm['name']}: "
                    f"{disease_risk_reason} | {irrigation['recommendation']}"
                )

        except Exception as e:
            logger.error(f"[AgentLoop] Error processing {farm['farm_id']}: {e}")


def _determine_alert_level(disease_risk: str, irrigation: dict) -> str:
    """Determine farm alert level from risk factors."""
    if disease_risk == "high" or irrigation["water_stress_level"] == "critical":
        return "HIGH"
    elif disease_risk == "moderate" or irrigation["water_stress_level"] == "high":
        return "MEDIUM"
    else:
        return "LOW"


def get_recent_advisories(limit: int = 20) -> list[dict]:
    """Return recent advisories from the in-memory log (for API inspection)."""
    return _advisory_log[-limit:][::-1]  # most recent first


async def run_advisory_cycle_now() -> list[dict]:
    """Force an immediate advisory cycle and return updated log."""
    await _run_advisory_cycle()
    return get_recent_advisories(limit=10)


def create_scheduler() -> AsyncIOScheduler:
    """Create and configure the APScheduler instance."""
    scheduler = AsyncIOScheduler(timezone="UTC")

    # Run every 30 minutes
    scheduler.add_job(
        _run_advisory_cycle,
        trigger="interval",
        minutes=30,
        id="agrismart_agentic_advisor",
        name="AgriSmart Agentic Advisor (Bonus G)",
        replace_existing=True,
        max_instances=1,
    )

    # Also run immediately at startup after a short delay
    scheduler.add_job(
        _run_advisory_cycle,
        trigger="date",
        run_date=None,  # runs at next available tick → effectively on startup
        id="agrismart_startup_advisory",
        name="AgriSmart Startup Advisory",
        replace_existing=True,
    )

    def on_job_error(event):
        logger.error(f"[AgentLoop] Job failed: {event.exception}")

    scheduler.add_listener(on_job_error, EVENT_JOB_ERROR)
    return scheduler
