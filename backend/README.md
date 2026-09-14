# AgriSmart AI — Backend

> **SIH 2026 Internal Hackathon | Problem C-433 | Member 2 (Backend)**

FastAPI backend for AgriSmart AI — an intelligent agriculture platform with crop disease detection and 5 bonus advisory modules.

---

## 🚀 Quick Start (under 10 minutes)

### Prerequisites
- Python 3.10+ 
- `pip` (comes with Python)

### 1. Clone & enter the backend directory
```bash
git clone https://github.com/your-repo/agrismart-ai.git
cd agrismart-ai/backend
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY (free at https://aistudio.google.com)
# Leave MODEL_MODE=mock to run without a trained model file
```

### 4. Start the server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Open API docs
Visit **http://localhost:8000/docs** in your browser — all endpoints are documented with example requests.

---

## 📡 Endpoints

| Method | Endpoint | Module | Description |
|--------|----------|--------|-------------|
| GET | `/` | Health | Server status & endpoint map |
| POST | `/predict` | **Core** | Upload leaf image → disease + confidence + precaution |
| POST | `/recommend-crop` | Bonus A | Soil/climate → recommended crop |
| POST | `/irrigation` | Bonus B | Soil moisture + weather → irrigate Y/N |
| GET | `/weather-advice` | Bonus C | GPS location → weather actions + disease risk |
| POST | `/sustainability` | Bonus D | Farm data → sustainability score (0-100) |
| POST | `/assistant` | Bonus E | Plain-language Q&A (Gemini-powered) |
| GET | `/agent/advisories` | Bonus G | Recent agentic advisor outputs |

---

## 🧪 Quick Test

```bash
# Health check
curl http://localhost:8000/

# Disease prediction (with a test image)
curl -X POST http://localhost:8000/predict \
  -F "file=@test_leaf.jpg"

# Weather advice for Ahmedabad, Gujarat
curl "http://localhost:8000/weather-advice?lat=23.03&lon=72.59&crop=Tomato"

# Crop recommendation
curl -X POST http://localhost:8000/recommend-crop \
  -H "Content-Type: application/json" \
  -d '{"soil_type":"Loamy","pH":6.5,"temperature":28,"humidity":65,"rainfall":800,"season":"Kharif"}'
```

---

## 🔧 Model Modes

| MODE | Description |
|------|-------------|
| `real` (recommended) | Loads trained EfficientNet-B0 weights from `model/best_agri_model.pth` (38 classes, included in repo) |
| `mock` | Stub model — deterministic results from image stats, no GPU or model loading needed |

The trained model weights are already located at `model/best_agri_model.pth` (16.5 MB).

To run with the real model:
1. Ensure `MODEL_WEIGHTS_PATH=../model/best_agri_model.pth` in `backend/.env`
2. Set `MODEL_MODE=real` in `backend/.env`
3. Start or restart the server: `uvicorn main:app --reload`


---

## 🌿 Modules & Architecture

```
backend/
├── main.py                     # FastAPI app, CORS, router registration, scheduler startup
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── routers/
│   ├── predict.py              # POST /predict — core disease detection
│   ├── crop.py                 # POST /recommend-crop — bonus A
│   ├── irrigation.py           # POST /irrigation — bonus B
│   ├── weather.py              # GET /weather-advice — bonus C
│   ├── sustainability.py       # POST /sustainability — bonus D
│   └── assistant.py            # POST /assistant — bonus E
├── services/
│   ├── disease_service.py      # Model loading + inference (mock/real)
│   ├── weather_service.py      # Open-Meteo API integration
│   ├── crop_service.py         # Rule-based crop recommendation (14 crops)
│   ├── irrigation_service.py   # FAO-56 soil moisture thresholds + decision rules
│   ├── sustainability_service.py # Weighted sustainability formula
│   └── assistant_service.py   # Gemini API with grounded context injection
├── scheduler/
│   └── agentic_loop.py        # APScheduler bonus G — runs every 30 min
├── models/
│   └── schemas.py             # All Pydantic request/response models
├── utils/
│   └── label_map.py           # Disease class labels + precautions
└── model_weights/
    └── README.md              # How to add real model weights
```

---

## 📊 Sustainability Formula (Bonus D)

Published for full reproducibility (required by problem statement):

```
score = water_score × 0.35
      + fertilizer_score × 0.25
      + disease_score × 0.20
      + irrigation_method_score × 0.20
```

| Component | How it's computed |
|-----------|------------------|
| water_score | `min(FAO_reference_liters / actual_liters, 1.0) × 100` |
| fertilizer_score | `max(0, 100 - max(0, kg_per_ha - 40) × 2)` |
| disease_score | 100 if healthy, 40 if disease detected |
| irrigation_method | drip=100, sprinkler=75, furrow=50, flood=30 |

The exact breakdown is returned in every `/sustainability` response under `formula_breakdown`.

---

## 🌤️ Weather Data Source

**Open-Meteo** — https://open-meteo.com  
- Free, no API key required
- Provides current conditions + 24-hour forecast
- WMO-standard weather codes
- Used by: `/weather-advice`, `/irrigation`, `/agent/advisories`

---

## 🤖 AI Assistant (Bonus E)

Powered by **Google Gemini 1.5 Flash** (free tier — https://aistudio.google.com).  
Answers are grounded: the LLM receives the actual disease detection results, weather data, irrigation advice, and sustainability score as context before answering.

**Supported languages**: English, Hindi, Gujarati, Marathi, Punjabi, Telugu, Tamil, Kannada, Bengali, Odia

---

## 🌱 Agentic Advisor (Bonus G)

An autonomous agent running via APScheduler (every 30 minutes):
1. Fetches live weather for configured farm locations
2. Evaluates disease risk from temperature/humidity
3. Checks irrigation thresholds against soil moisture
4. Generates a consolidated advisory with alert levels (LOW/MEDIUM/HIGH)
5. Logs results to in-memory store (accessible at `GET /agent/advisories`)

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | ≥0.111 | REST API framework |
| uvicorn | ≥0.30 | ASGI server |
| Pillow | ≥10.3 | Image processing |
| torch + timm | ≥2.3 | EfficientNet-B0 inference (real mode) |
| scikit-learn | ≥1.5 | Crop recommendation model |
| httpx | ≥0.27 | Async HTTP for Open-Meteo |
| apscheduler | ≥3.10 | Bonus G scheduler |
| google-generativeai | ≥0.7 | Gemini API for assistant |
| python-dotenv | ≥1.0 | .env file loading |

---

## 🏗️ Deploy to Render (free tier)

1. Push this repo to GitHub
2. Go to https://render.com → New Web Service → Connect repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add env vars: `GEMINI_API_KEY`, `MODEL_MODE=mock`

---

## 📝 Originality Declaration

- Model architecture: EfficientNet-B0 via `timm` (pretrained ImageNet backbone, fine-tuned on PlantVillage)
- Weather data: Open-Meteo API
- Crop knowledge base: based on FAO guidelines and ICAR crop recommendations
- Sustainability formula: original design (inspired by FAO-56 water efficiency framework)
- All code is original, written during the SIH 2026 hackathon window (10-15 September 2026)
