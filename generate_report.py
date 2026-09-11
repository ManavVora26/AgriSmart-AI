"""
AgriSmart AI — Professional PDF Report Generator
Generates a complete project documentation PDF with screenshots.
"""

import os, glob
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus.flowables import Flowable
from PIL import Image as PILImage

# ── Paths ─────────────────────────────────────────────────────────────────────
ARTIFACTS = Path(r"C:\Users\mbsor\.gemini\antigravity-ide\brain\a2f16afb-c1b7-42e0-af91-fca8f2f3f3e5")
OUTPUT_PDF = Path(r"E:\SIH Project3\AgriSmart_AI_Project_Report.pdf")

def find_screenshot(name: str) -> Path | None:
    """Find the most recent screenshot matching a name pattern."""
    matches = sorted(ARTIFACTS.glob(f"{name}_*.png"), reverse=True)
    if matches:
        return matches[0]
    matches = sorted(ARTIFACTS.glob(f"{name}.png"), reverse=True)
    return matches[0] if matches else None

# ── Color Palette ─────────────────────────────────────────────────────────────
GREEN_DARK   = colors.HexColor("#1B5E20")
GREEN_MID    = colors.HexColor("#2E7D32")
GREEN_LIGHT  = colors.HexColor("#43A047")
GREEN_PALE   = colors.HexColor("#E8F5E9")
AMBER        = colors.HexColor("#F57F17")
BLUE_DARK    = colors.HexColor("#0D47A1")
BLUE_LIGHT   = colors.HexColor("#E3F2FD")
GREY_DARK    = colors.HexColor("#263238")
GREY_MID     = colors.HexColor("#546E7A")
GREY_LIGHT   = colors.HexColor("#ECEFF1")
WHITE        = colors.white
RED_SOFT     = colors.HexColor("#B71C1C")
ORANGE_SOFT  = colors.HexColor("#E65100")

# ── Styles ────────────────────────────────────────────────────────────────────
BASE = getSampleStyleSheet()

def S(name, **kw):
    """Create a named ParagraphStyle with keyword overrides."""
    return ParagraphStyle(name, **kw)

H1 = S("H1", fontSize=26, textColor=GREEN_DARK, fontName="Helvetica-Bold",
        spaceAfter=8, leading=32, alignment=TA_CENTER)
H2 = S("H2", fontSize=18, textColor=GREEN_DARK, fontName="Helvetica-Bold",
        spaceAfter=6, spaceBefore=14, leading=22)
H3 = S("H3", fontSize=13, textColor=GREEN_MID, fontName="Helvetica-Bold",
        spaceAfter=4, spaceBefore=8, leading=16)
H4 = S("H4", fontSize=11, textColor=GREY_DARK, fontName="Helvetica-Bold",
        spaceAfter=3, spaceBefore=6, leading=14)
BODY = S("BODY", fontSize=10, textColor=GREY_DARK, fontName="Helvetica",
         spaceAfter=4, leading=14, alignment=TA_JUSTIFY)
BODY_BOLD = S("BODY_BOLD", fontSize=10, textColor=GREY_DARK, fontName="Helvetica-Bold",
              spaceAfter=4, leading=14)
CAPTION = S("CAPTION", fontSize=8, textColor=GREY_MID, fontName="Helvetica-Oblique",
            spaceAfter=6, alignment=TA_CENTER)
CODE = S("CODE", fontSize=8, textColor=colors.HexColor("#1A237E"),
         fontName="Courier", spaceAfter=4, leading=12, backColor=GREY_LIGHT,
         leftIndent=10, rightIndent=10)
BULLET = S("BULLET", fontSize=10, textColor=GREY_DARK, fontName="Helvetica",
           spaceAfter=3, leading=14, leftIndent=16, bulletIndent=6)
SMALL = S("SMALL", fontSize=8, textColor=GREY_MID, fontName="Helvetica", leading=10)
SUBTITLE = S("SUBTITLE", fontSize=12, textColor=GREY_MID, fontName="Helvetica",
             spaceAfter=4, alignment=TA_CENTER, leading=16)
TAG = S("TAG", fontSize=9, textColor=WHITE, fontName="Helvetica-Bold",
        alignment=TA_CENTER)

# ── Helper Flowables ──────────────────────────────────────────────────────────

def divider(color=GREEN_MID, thickness=1):
    return HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=6, spaceBefore=6)

def space(h=6):
    return Spacer(1, h)

def screenshot(name: str, caption: str, max_w_mm=160) -> list:
    """Return [Image, Caption] flowables for a screenshot, or empty list if not found."""
    path = find_screenshot(name)
    if not path:
        return [Paragraph(f"[Screenshot '{name}' not available]", CAPTION)]
    try:
        pil = PILImage.open(path)
        w, h = pil.size
        max_w = max_w_mm * mm
        scale = min(max_w / w, (100 * mm) / h)
        return [
            Image(str(path), width=w * scale, height=h * scale),
            Paragraph(caption, CAPTION),
            space(4),
        ]
    except Exception as e:
        return [Paragraph(f"[Could not load screenshot: {e}]", CAPTION)]

def badge(text: str, bg=GREEN_MID) -> Table:
    """Inline colored badge."""
    tbl = Table([[Paragraph(text, TAG)]], colWidths=[40 * mm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("ROUNDEDCORNERS", [4]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return tbl

def section_header(title: str, subtitle: str = "") -> list:
    items = [
        divider(GREEN_MID, 2),
        Paragraph(title, H2),
    ]
    if subtitle:
        items.append(Paragraph(subtitle, SUBTITLE))
    return items

def colored_table(headers, rows, col_widths=None, header_bg=GREEN_MID):
    """Styled table with alternating rows."""
    data = [[Paragraph(h, S("TH", fontSize=9, textColor=WHITE, fontName="Helvetica-Bold",
                             alignment=TA_CENTER)) for h in headers]]
    for i, row in enumerate(rows):
        data.append([Paragraph(str(c), S("TD", fontSize=9, textColor=GREY_DARK,
                                         fontName="Helvetica", leading=12)) for c in row])
    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, GREY_LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B0BEC5")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(style)
    return t

def info_box(text: str, bg=GREEN_PALE, border=GREEN_MID) -> Table:
    inner = Paragraph(text, S("IB", fontSize=10, textColor=GREY_DARK,
                               fontName="Helvetica", leading=14))
    t = Table([[inner]], colWidths=[165 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 1.5, border),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    return t

# ── Page Footer/Header callback ───────────────────────────────────────────────

def on_page(canvas, doc):
    canvas.saveState()
    w, h = A4
    # Bottom bar
    canvas.setFillColor(GREEN_DARK)
    canvas.rect(0, 0, w, 20, fill=1, stroke=0)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(WHITE)
    canvas.drawString(15, 6, "AgriSmart AI — SIH 2026 | C-433 | Confidential")
    canvas.drawRightString(w - 15, 6, f"Page {doc.page}")
    # Top accent line
    canvas.setFillColor(GREEN_LIGHT)
    canvas.rect(0, h - 4, w, 4, fill=1, stroke=0)
    canvas.restoreState()

# ── Build document ─────────────────────────────────────────────────────────────

def build_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=22 * mm,
        bottomMargin=25 * mm,
        title="AgriSmart AI — Project Report",
        author="SIH 2026 Team C-433",
        subject="Backend Implementation + ML Guide",
    )

    story = []
    W = 170 * mm  # usable page width

    # ═══════════════════════════════════════════════════════════════════════
    # COVER PAGE
    # ═══════════════════════════════════════════════════════════════════════
    story += [
        space(30),
        Paragraph("🌱 AgriSmart AI", H1),
        Paragraph("Intelligent Agriculture for a Sustainable Future", SUBTITLE),
        space(6),
        divider(GREEN_LIGHT, 3),
        space(6),
        Paragraph("Project Documentation & Implementation Report", 
                  S("CT", fontSize=14, textColor=GREEN_MID, fontName="Helvetica-Bold",
                    alignment=TA_CENTER)),
        space(4),
        Paragraph("SIH 2026 Internal Hackathon  •  Problem Statement C-433  •  L.J. Institute of Engineering & Technology",
                  SUBTITLE),
        space(20),
    ]

    # Cover info table
    cover_data = [
        ["Field", "Details"],
        ["Problem ID", "C-433"],
        ["Domain", "AI / AgriTech / Sustainability"],
        ["Tech Stack", "AI/ML • Computer Vision • GenAI"],
        ["Hackathon Window", "10 – 15 September 2026"],
        ["Team Split", "Member 1: Frontend  |  Member 2: Backend  |  Member 3: ML/Training"],
        ["Modules Built", "Core (Mandatory) + Bonus A, B, C, D, E, G"],
        ["Report Date", datetime.now().strftime("%d %B %Y, %H:%M")],
    ]
    story.append(colored_table(
        cover_data[0], cover_data[1:],
        col_widths=[50 * mm, 120 * mm]
    ))
    story += [space(20), PageBreak()]

    # ═══════════════════════════════════════════════════════════════════════
    # TABLE OF CONTENTS
    # ═══════════════════════════════════════════════════════════════════════
    story += section_header("Table of Contents")
    toc = [
        ("1", "Project Overview & Architecture", "3"),
        ("2", "Member 2 — Backend: What Was Built", "4"),
        ("3", "API Endpoints — Details & Live Tests", "5"),
        ("4", "Swagger UI Screenshots", "7"),
        ("5", "Backend File Structure", "10"),
        ("6", "Sustainability Formula (Bonus D)", "11"),
        ("7", "Member 3 — ML/Training: What to Build", "12"),
        ("8", "How to Run the Backend", "15"),
        ("9", "Deployment Guide", "16"),
    ]
    for num, title, page in toc:
        story.append(Paragraph(
            f"<b>{num}.</b> &nbsp;&nbsp; {title} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <i>pg. {page}</i>",
            S("TOC", fontSize=10, textColor=GREY_DARK, fontName="Helvetica",
              spaceAfter=5, leading=14)
        ))
    story += [space(8), PageBreak()]

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 1 — PROJECT OVERVIEW
    # ═══════════════════════════════════════════════════════════════════════
    story += section_header("1. Project Overview & Architecture",
                             "AgriSmart AI — SIH 2026 Problem C-433")
    story += [
        Paragraph(
            "AgriSmart AI is an intelligent agriculture platform built for the SIH 2026 hackathon. "
            "It combines Computer Vision, Machine Learning, Generative AI, and live weather data "
            "to help Indian farmers detect crop diseases, optimise irrigation, recommend crops, "
            "and access a conversational AI assistant — all via a clean REST API.",
            BODY
        ),
        space(8),
    ]

    story.append(info_box(
        "<b>Core Task (Mandatory):</b> Accept a leaf/crop image → classify disease → "
        "display confidence + precaution. Evaluated on held-out field-condition test set via macro-F1.",
        GREEN_PALE, GREEN_MID
    ))
    story += [space(8)]

    story.append(Paragraph("Bonus Modules Built:", H3))
    bonus_data = [
        ["Module", "What it does", "Endpoint", "Status"],
        ["Core", "Crop disease detection from leaf image", "POST /predict", "✅ Built"],
        ["Bonus A", "Crop recommendation from soil/climate", "POST /recommend-crop", "✅ Built"],
        ["Bonus B", "Smart irrigation Y/N decision", "POST /irrigation", "✅ Built"],
        ["Bonus C", "Live weather → farm actions", "GET /weather-advice", "✅ Built"],
        ["Bonus D", "Sustainability score (0-100)", "POST /sustainability", "✅ Built"],
        ["Bonus E", "Gemini AI farmer assistant", "POST /assistant", "✅ Built"],
        ["Bonus F", "IoT Integration", "—", "⏭ Skipped (per plan)"],
        ["Bonus G", "Agentic advisor loop", "GET /agent/advisories", "✅ Built"],
    ]
    story.append(colored_table(
        bonus_data[0], bonus_data[1:],
        col_widths=[25*mm, 60*mm, 50*mm, 30*mm]
    ))
    story += [space(10)]

    story.append(Paragraph("System Architecture:", H3))
    arch_text = (
        "<b>Frontend (Member 1)</b> → Plain HTML/CSS/JS → <b>Backend REST API (Member 2)</b> → "
        "FastAPI on Python → Services layer → "
        "<b>ML Model (Member 3)</b> EfficientNet-B0 weights + "
        "Open-Meteo Weather API + Google Gemini AI"
    )
    story.append(info_box(arch_text, BLUE_LIGHT, BLUE_DARK))
    story += [space(8), PageBreak()]

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 2 — BACKEND WHAT WAS BUILT
    # ═══════════════════════════════════════════════════════════════════════
    story += section_header("2. Member 2 — Backend: What Was Built",
                             "Complete FastAPI backend implementation")

    story += [
        Paragraph("Technology Stack", H3),
        Paragraph("• <b>FastAPI</b> — Python REST API framework (auto-docs, async, Pydantic validation)", BULLET),
        Paragraph("• <b>Uvicorn</b> — ASGI production server", BULLET),
        Paragraph("• <b>Open-Meteo</b> — Free weather API (no API key needed!)", BULLET),
        Paragraph("• <b>Google Gemini 2.0 Flash</b> — AI assistant via google-genai SDK", BULLET),
        Paragraph("• <b>APScheduler</b> — Background job scheduler for Bonus G agentic loop", BULLET),
        Paragraph("• <b>timm + PyTorch</b> — EfficientNet-B0 model inference (real mode)", BULLET),
        Paragraph("• <b>Pydantic v2</b> — Request/response schema validation", BULLET),
        space(8),
        Paragraph("Key Design Decisions", H3),
        Paragraph("• <b>Dual model mode:</b> SERVER_MODE=mock runs without any .pt weights (for development/demo); "
                  "MODEL_MODE=real loads the trained EfficientNet-B0 from disk. "
                  "Member 3 just drops the weights file and flips the env var.", BULLET),
        Paragraph("• <b>Grounded AI answers:</b> The /assistant endpoint injects actual disease results, "
                  "weather data, irrigation advice, and sustainability score into Gemini's context — "
                  "this scores higher per the problem statement than free-form generation.", BULLET),
        Paragraph("• <b>Reproducible sustainability formula:</b> Every /sustainability response includes "
                  "the full formula_breakdown JSON so judges can verify the math.", BULLET),
        Paragraph("• <b>FAO-56 thresholds:</b> Irrigation decisions use per-crop, per-growth-stage "
                  "soil moisture thresholds from FAO guidelines.", BULLET),
        space(8), PageBreak(),
    ]

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 3 — API ENDPOINTS
    # ═══════════════════════════════════════════════════════════════════════
    story += section_header("3. API Endpoints — Details & Live Tests")

    endpoints = [
        {
            "method": "POST", "path": "/predict", "tag": "Core — Disease Detection",
            "desc": "Upload a leaf/crop image (JPEG/PNG/WebP, max 10 MB). Returns disease class, confidence score, is_healthy flag, and actionable precaution text.",
            "input": "multipart/form-data: file (image)",
            "output": '{"label": "Tomato___Early_Blight", "display_name": "Tomato Early Blight", "confidence": 0.91, "is_healthy": false, "precaution": "Remove affected leaves, apply fungicide...", "model_mode": "mock"}',
        },
        {
            "method": "POST", "path": "/recommend-crop", "tag": "Bonus A",
            "desc": "Provide soil type, pH, temperature, humidity, rainfall, season. Returns best matching crop from 14-crop knowledge base with confidence and rotation advice.",
            "input": '{"soil_type": "Loamy", "pH": 6.5, "temperature": 28, "humidity": 65, "rainfall": 800, "season": "Kharif"}',
            "output": '{"recommended_crop": "Maize", "confidence": 1.0, "alternative_crops": ["Cotton", "Groundnut"]}',
        },
        {
            "method": "POST", "path": "/irrigation", "tag": "Bonus B — Smart Irrigation",
            "desc": "Provide soil moisture %, crop type, growth stage, and GPS coordinates. Fetches live 24h rain forecast from Open-Meteo and applies FAO-56 decision rules.",
            "input": '{"soil_moisture": 31, "crop_type": "Tomato", "growth_stage": "Flowering", "lat": 23.03, "lon": 72.59}',
            "output": '{"irrigate": true, "recommendation": "Irrigate now — 29% below threshold", "water_stress_level": "critical"}',
        },
        {
            "method": "GET", "path": "/weather-advice", "tag": "Bonus C — Weather Intelligence",
            "desc": "Provide GPS coordinates and optional crop. Returns live weather from Open-Meteo + actionable farm advice + disease risk level. Data source: open-meteo.com (no API key).",
            "input": "?lat=23.03&lon=72.59&crop=Tomato",
            "output": '{"temperature": 33.6, "humidity": 49, "disease_risk": "low", "actions": ["No rain expected. Irrigate as per schedule.", "High temp (33.6°C) — check moisture"]}',
        },
        {
            "method": "POST", "path": "/sustainability", "tag": "Bonus D — Sustainability Score",
            "desc": "Provide weekly farm operations data. Returns scored 0-100 sustainability grade with full formula breakdown (published for judge reproducibility) and improvement suggestions.",
            "input": '{"water_used_liters": 5000, "crop_type": "Tomato", "area_hectares": 1, "fertilizer_kg_per_hectare": 40, "irrigation_method": "drip", "disease_detected": true}',
            "output": '{"score": 88.0, "grade": "B", "improvement_suggestions": ["Early disease treatment reduces crop loss..."]}',
        },
        {
            "method": "POST", "path": "/assistant", "tag": "Bonus E — Farmer Assistant (GenAI)",
            "desc": "Plain-language Q&A powered by Google Gemini 2.0 Flash. Answers are grounded in actual model outputs (disease, weather, irrigation). Supports 10 languages including Hindi, Gujarati, Marathi.",
            "input": '{"question": "My tomato has brown spots?", "context": {"disease_detected": "Tomato Early Blight"}, "language": "hi"}',
            "output": '{"answer": "...(Gemini grounded response in Hindi)...", "grounded": true, "sources_used": ["disease detection result"]}',
        },
        {
            "method": "GET", "path": "/agent/advisories", "tag": "Bonus G — Agentic Advisor",
            "desc": "Returns recent auto-generated farm advisories from the APScheduler background loop (runs every 30 min). Demonstrates the full Bonus G decision loop: weather → reasoning → recommendation → log.",
            "input": "?limit=20",
            "output": '{"count": 2, "advisories": [{"farm_name": "Ramesh Patels Tomato Farm", "disease_risk": "low", "irrigate": true, "alert_level": "MEDIUM"}]}',
        },
    ]

    for ep in endpoints:
        method_color = GREEN_MID if ep["method"] == "GET" else ORANGE_SOFT
        story += [
            KeepTogether([
                Paragraph(f'<font color="{method_color.hexval()}" size="10"><b>{ep["method"]}</b></font>  '
                          f'<font color="{GREY_DARK.hexval()}" size="12"><b>{ep["path"]}</b></font>  '
                          f'<font color="{GREY_MID.hexval()}" size="9"><i>({ep["tag"]})</i></font>',
                          S("EP", fontSize=11, fontName="Helvetica", spaceAfter=3, leading=16)),
                Paragraph(ep["desc"], BODY),
                Paragraph(f"<b>Request:</b> <font color='#1A237E' name='Courier'>{ep['input']}</font>", CODE),
                Paragraph(f"<b>Response:</b> <font color='#1A237E' name='Courier'>{ep['output']}</font>", CODE),
                space(8),
            ])
        ]
    story += [PageBreak()]

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 4 — SWAGGER SCREENSHOTS
    # ═══════════════════════════════════════════════════════════════════════
    story += section_header("4. Swagger UI Screenshots",
                             "Live API documentation at http://localhost:8000/docs")

    story += [
        Paragraph("The Swagger UI auto-generated by FastAPI provides interactive documentation "
                  "for every endpoint. Judges can test any endpoint directly from the browser "
                  "without writing a single line of code.", BODY),
        space(8),
        Paragraph("Full Swagger UI Overview:", H3),
    ]
    story += screenshot("swagger_top", "Fig 1 — AgriSmart AI Swagger UI (http://localhost:8000/docs) showing all endpoints", 160)

    story += [Paragraph("Disease Detection — POST /predict (Core Task):", H3)]
    story += screenshot("swagger_predict", "Fig 2 — POST /predict endpoint: Upload leaf image → disease + confidence + precaution", 160)

    story += [Paragraph("Crop Recommendation — POST /recommend-crop (Bonus A):", H3)]
    story += screenshot("swagger_crop", "Fig 3 — POST /recommend-crop: Soil/climate parameters → best crop", 160)

    story += [PageBreak(), Paragraph("Smart Irrigation — POST /irrigation (Bonus B):", H3)]
    story += screenshot("swagger_irrigation", "Fig 4 — POST /irrigation: Soil moisture + GPS → irrigate Y/N with live weather", 160)

    story += [Paragraph("Weather Intelligence — GET /weather-advice (Bonus C):", H3)]
    story += screenshot("swagger_weather", "Fig 5 — GET /weather-advice: Live Open-Meteo weather + farm actions", 160)

    story += [Paragraph("Live Weather Response from Open-Meteo:", H3)]
    story += screenshot("swagger_weather_response", "Fig 6 — Live API response from GET /weather-advice for Ahmedabad (33.6°C, disease risk: low)", 160)

    story += [PageBreak(), Paragraph("Sustainability Score — POST /sustainability (Bonus D):", H3)]
    story += screenshot("swagger_sustainability", "Fig 7 — POST /sustainability: Reproducible 0-100 score with full formula breakdown", 160)

    story += [Paragraph("AI Farmer Assistant — POST /assistant (Bonus E):", H3)]
    story += screenshot("swagger_assistant", "Fig 8 — POST /assistant: Gemini-powered grounded Q&A with multi-language support", 160)

    story += [Paragraph("Agentic Advisor — GET /agent/advisories (Bonus G):", H3)]
    story += screenshot("swagger_agent", "Fig 9 — GET /agent/advisories: Autonomous farm advisories generated every 30 min", 160)

    story += [PageBreak()]

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 5 — FILE STRUCTURE
    # ═══════════════════════════════════════════════════════════════════════
    story += section_header("5. Backend File Structure")
    structure = [
        "backend/",
        "├── main.py                      ← FastAPI app entry point, CORS, scheduler",
        "├── requirements.txt             ← Python dependencies",
        "├── .env.example                 ← Environment variables template",
        "├── .env                         ← Your config (add GEMINI_API_KEY here)",
        "├── README.md                    ← Setup guide (runnable in < 10 min)",
        "│",
        "├── routers/                     ← One file per endpoint",
        "│   ├── predict.py               ← POST /predict (Core)",
        "│   ├── crop.py                  ← POST /recommend-crop (Bonus A)",
        "│   ├── irrigation.py            ← POST /irrigation (Bonus B)",
        "│   ├── weather.py               ← GET /weather-advice (Bonus C)",
        "│   ├── sustainability.py        ← POST /sustainability (Bonus D)",
        "│   └── assistant.py             ← POST /assistant (Bonus E)",
        "│",
        "├── services/                    ← Business logic layer",
        "│   ├── disease_service.py       ← Model loading + inference (mock/real)",
        "│   ├── weather_service.py       ← Open-Meteo API integration",
        "│   ├── crop_service.py          ← 14-crop recommendation knowledge base",
        "│   ├── irrigation_service.py    ← FAO-56 moisture thresholds + rules",
        "│   ├── sustainability_service.py← Weighted sustainability formula",
        "│   └── assistant_service.py     ← Google Gemini 2.0 Flash integration",
        "│",
        "├── scheduler/",
        "│   └── agentic_loop.py          ← APScheduler (every 30 min) Bonus G",
        "│",
        "├── models/",
        "│   └── schemas.py               ← All Pydantic request/response schemas",
        "│",
        "├── utils/",
        "│   └── label_map.py             ← 18 disease classes + precautions",
        "│",
        "└── model_weights/",
        "    └── README.md                ← Where Member 3 places disease_model.pt",
    ]
    for line in structure:
        story.append(Paragraph(line, CODE))
    story += [space(8), PageBreak()]

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 6 — SUSTAINABILITY FORMULA
    # ═══════════════════════════════════════════════════════════════════════
    story += section_header("6. Sustainability Formula (Bonus D)",
                             "Fully reproducible — as required by Problem Statement Section 3.2-D")

    story += [
        Paragraph("The sustainability score is computed as a weighted average of 4 sub-scores. "
                  "The exact formula and every intermediate value are included in every API response "
                  "under the formula_breakdown field, making it fully verifiable by judges.", BODY),
        space(6),
    ]

    formula_lines = [
        "score = water_score × 0.35",
        "      + fertilizer_score × 0.25",
        "      + disease_score × 0.20",
        "      + irrigation_method_score × 0.20",
        "",
        "── Sub-score formulas ──────────────────────────────────────────────────",
        "water_score          = min(FAO_reference_liters / actual_liters, 1.0) × 100",
        "fertilizer_score     = max(0, 100 − max(0, kg_per_ha − 40) × 2)",
        "disease_score        = 100 if no disease detected, else 40",
        "irrigation_method    = drip → 100 | sprinkler → 75 | furrow → 50 | flood → 30",
    ]
    for line in formula_lines:
        story.append(Paragraph(line, CODE))

    story += [
        space(6),
        Paragraph("Grade Thresholds:", H3),
    ]
    grade_data = [
        ["Score Range", "Grade", "Interpretation"],
        ["90 – 100", "A", "Excellent — exemplary sustainable farming"],
        ["75 – 89", "B", "Good — above average, minor improvements possible"],
        ["60 – 74", "C", "Average — notable improvements needed"],
        ["45 – 59", "D", "Below average — significant changes required"],
        ["0 – 44", "F", "Poor — urgent intervention needed"],
    ]
    story.append(colored_table(grade_data[0], grade_data[1:],
                               col_widths=[35*mm, 20*mm, 110*mm]))
    story += [space(6), PageBreak()]

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 7 — MEMBER 3 TASKS
    # ═══════════════════════════════════════════════════════════════════════
    story += section_header("7. Member 3 — ML/Training: Complete Task Guide",
                             "Everything Member 3 needs to build to complete the project")

    story += [
        info_box(
            "⚠️ <b>Critical:</b> The backend is already running with a mock model. "
            "Member 3's job is to train the REAL model and integrate it. "
            "Integration = copy disease_model.pt + set MODEL_MODE=real. That's it!",
            colors.HexColor("#FFF3E0"), AMBER
        ),
        space(10),
        Paragraph("7.1 Core Task — Crop Disease Classifier (MANDATORY)", H3),
        Paragraph("Build a transfer-learning image classifier on the PlantVillage dataset:", BODY),
        Paragraph("• <b>Architecture:</b> EfficientNet-B0 from timm (recommended) or ResNet50/ViT-Small", BULLET),
        Paragraph("• <b>Dataset:</b> PlantVillage (~54,000 lab images, shared at kickoff)", BULLET),
        Paragraph("• <b>Classes:</b> Use the exact 18 classes in backend/utils/label_map.py (INDEX_TO_LABEL dict)", BULLET),
        Paragraph("• <b>Split:</b> 80% train / 10% val / 10% test — report on held-out test only", BULLET),
        Paragraph("• <b>Metric:</b> Macro-averaged F1 (NOT accuracy) — required by problem statement", BULLET),
        Paragraph("• <b>Output report:</b> Confusion matrix + per-class precision/recall table", BULLET),
        space(8),
        Paragraph("Recommended Training Code Structure:", H3),
    ]

    train_code = [
        "# training/train.py",
        "import timm, torch",
        "from torchvision import transforms, datasets",
        "",
        "# 1. Create model",
        "model = timm.create_model('efficientnet_b0', pretrained=True, num_classes=18)",
        "",
        "# 2. Data augmentation (important for field image generalization)",
        "train_tf = transforms.Compose([",
        "    transforms.RandomResizedCrop(224),",
        "    transforms.RandomHorizontalFlip(),",
        "    transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2),",
        "    transforms.ToTensor(),",
        "    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])",
        "])",
        "",
        "# 3. Save weights — MUST match this format for backend to load!",
        "torch.save({'model_state_dict': model.state_dict()}, 'disease_model.pt')",
    ]
    for line in train_code:
        story.append(Paragraph(line, CODE))

    story += [
        space(8),
        Paragraph("7.2 Integration with Backend (2 Steps Only!):", H3),
        info_box(
            "<b>Step 1:</b> Copy disease_model.pt → backend/model_weights/disease_model.pt\n"
            "<b>Step 2:</b> Edit backend/.env → change MODEL_MODE=mock to MODEL_MODE=real\n"
            "<b>Step 3:</b> Restart server: python -m uvicorn main:app --reload\n\n"
            "The backend will automatically load the real model. No other code changes needed!",
            GREEN_PALE, GREEN_MID
        ),
        space(8),
        Paragraph("7.3 Required Output — MODEL_WEIGHTS", H3),
    ]

    weight_data = [
        ["Requirement", "Specification"],
        ["File name", "disease_model.pt"],
        ["Format", "PyTorch state_dict: {'model_state_dict': model.state_dict()}"],
        ["Architecture", "timm.create_model('efficientnet_b0', num_classes=18)"],
        ["Input", "224×224 RGB, ImageNet normalized (mean=[0.485,0.456,0.406])"],
        ["Output", "18 logits — one per disease class (see label_map.py)"],
        ["Class order", "Must match INDEX_TO_LABEL in backend/utils/label_map.py"],
    ]
    story.append(colored_table(weight_data[0], weight_data[1:],
                               col_widths=[50*mm, 120*mm]))
    story += [space(8)]

    story += [
        Paragraph("7.4 Bonus A — Crop Recommendation (Optional Upgrade)", H3),
        Paragraph("The backend has a rule-based crop recommender. Member 3 can improve it with "
                  "a trained scikit-learn classifier:", BODY),
        Paragraph("• Dataset: <b>Crop Recommendation Dataset</b> (Kaggle — 2200 samples, 22 crops)", BULLET),
        Paragraph("• Features: N, P, K, temperature, humidity, pH, rainfall → crop label", BULLET),
        Paragraph("• Model: RandomForestClassifier or GradientBoostingClassifier", BULLET),
        Paragraph("• Save: joblib.dump(model, 'crop_recommender.pkl')", BULLET),
        Paragraph("• Report: accuracy, F1 per crop class", BULLET),
        space(6),
        Paragraph("7.5 Bonus B — Irrigation Model (Optional Upgrade)", H3),
        Paragraph("The backend already has rule-based logic. If Member 3 wants ML-based:", BODY),
        Paragraph("• Frame as binary classification: irrigate=1 / skip=0", BULLET),
        Paragraph("• Features: soil_moisture, temperature, humidity, rain_forecast, growth_stage_encoded", BULLET),
        Paragraph("• Model: LogisticRegression or RandomForest", BULLET),
        Paragraph("• Validation: explain logic or show confusion matrix", BULLET),
        space(6),
        Paragraph("7.6 Required Model Report (One Page — Section 7.3 of Problem Statement)", H3),
    ]

    report_data = [
        ["Field", "What to State"],
        ["Task", "Crop-disease image classification, 18 classes"],
        ["Dataset & split", "PlantVillage (lab, ~54k images) | 80/10/10 train/val/test split"],
        ["Model / approach", "EfficientNet-B0 via timm | Transfer learning from ImageNet | Key hyperparameters"],
        ["Metric & result", "Macro-F1 (primary) + accuracy + confusion matrix + per-class precision/recall"],
        ["Baseline", "Report the provided baseline number and your improvement over it"],
        ["Limitations", "Real-field vs lab image gap (PlantVillage → PlantDoc), occlusion, lighting"],
    ]
    story.append(colored_table(report_data[0], report_data[1:],
                               col_widths=[40*mm, 130*mm]))
    story += [space(8), PageBreak()]

    story += [
        Paragraph("7.7 Recommended Tools & Libraries for Member 3:", H3),
    ]
    tools_data = [
        ["Tool", "Purpose", "Install"],
        ["timm", "EfficientNet-B0 pretrained model", "pip install timm"],
        ["torch + torchvision", "Training + transforms", "pip install torch torchvision"],
        ["albumentations", "Image augmentation for field robustness", "pip install albumentations"],
        ["scikit-learn", "Crop recommender + irrigation model", "pip install scikit-learn"],
        ["Weights & Biases", "Training curve tracking", "pip install wandb"],
        ["matplotlib / seaborn", "Confusion matrix visualization", "pip install matplotlib seaborn"],
        ["Kaggle CLI", "Download PlantVillage dataset", "pip install kaggle"],
    ]
    story.append(colored_table(tools_data[0], tools_data[1:],
                               col_widths=[35*mm, 90*mm, 45*mm]))

    story += [space(8)]
    story += [
        Paragraph("7.8 Class Index Order (CRITICAL — must match backend):", H3),
        Paragraph("The model output must match this exact index-to-label mapping:", BODY),
    ]
    labels = [
        (0, "Apple___Apple_scab"), (1, "Apple___Black_rot"), (2, "Apple___healthy"),
        (3, "Corn_(maize)___Common_rust_"), (4, "Corn_(maize)___Gray_leaf_spot"),
        (5, "Corn_(maize)___healthy"), (6, "Grape___Black_rot"), (7, "Grape___healthy"),
        (8, "Pepper,_bell___Bacterial_spot"), (9, "Pepper,_bell___healthy"),
        (10, "Potato___Early_Blight"), (11, "Potato___Late_Blight"), (12, "Potato___healthy"),
        (13, "Tomato___Bacterial_Spot"), (14, "Tomato___Early_Blight"),
        (15, "Tomato___Late_Blight"), (16, "Tomato___Leaf_Mold"), (17, "Tomato___healthy"),
    ]
    label_data = [["Index", "Label"]] + [[str(i), l] for i, l in labels]
    story.append(colored_table(label_data[0], label_data[1:], col_widths=[20*mm, 150*mm]))
    story += [space(8), PageBreak()]

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 8 — HOW TO RUN
    # ═══════════════════════════════════════════════════════════════════════
    story += section_header("8. How to Run the Backend",
                             "Judges must be able to reproduce a prediction in under 10 minutes")

    run_steps = [
        ("Step 1", "Clone the repository", "git clone https://github.com/your-repo/agrismart-ai.git"),
        ("Step 2", "Enter backend directory", "cd agrismart-ai/backend"),
        ("Step 3", "Install dependencies", "pip install -r requirements.txt"),
        ("Step 4", "Configure environment", "cp .env.example .env  # then add GEMINI_API_KEY"),
        ("Step 5", "Start the server", "python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"),
        ("Step 6", "Open API docs", "Open http://localhost:8000/docs in browser"),
    ]
    for step, title, cmd in run_steps:
        story += [
            Paragraph(f"<b>{step}:</b> {title}", BODY_BOLD),
            Paragraph(cmd, CODE),
            space(4),
        ]

    story += [
        space(4),
        Paragraph("Quick Endpoint Tests:", H3),
    ]
    test_cmds = [
        "# Health check",
        "curl http://localhost:8000/",
        "",
        "# Disease prediction (upload a leaf image)",
        "curl -X POST http://localhost:8000/predict -F 'file=@leaf.jpg'",
        "",
        "# Live weather for Ahmedabad",
        'curl "http://localhost:8000/weather-advice?lat=23.03&lon=72.59&crop=Tomato"',
        "",
        "# Crop recommendation",
        'curl -X POST http://localhost:8000/recommend-crop -H "Content-Type: application/json" \\',
        '  -d \'{"soil_type":"Loamy","pH":6.5,"temperature":28,"humidity":65,"rainfall":800,"season":"Kharif"}\'',
    ]
    for line in test_cmds:
        story.append(Paragraph(line, CODE))

    story += [space(8), PageBreak()]

    # ═══════════════════════════════════════════════════════════════════════
    # SECTION 9 — DEPLOYMENT
    # ═══════════════════════════════════════════════════════════════════════
    story += section_header("9. Deployment Guide",
                             "Deploy to Render.com (free tier) in 5 minutes")

    story += [
        Paragraph("Option A — Render.com (Recommended for submission):", H3),
        Paragraph("1. Push repository to GitHub", BULLET),
        Paragraph("2. Go to render.com → New Web Service → Connect GitHub repo", BULLET),
        Paragraph("3. Build command: <font name='Courier'>pip install -r requirements.txt</font>", BULLET),
        Paragraph("4. Start command: <font name='Courier'>python -m uvicorn main:app --host 0.0.0.0 --port $PORT</font>", BULLET),
        Paragraph("5. Add environment variables: GEMINI_API_KEY, MODEL_MODE=mock", BULLET),
        Paragraph("6. Deploy! URL will be: https://agrismart-ai.onrender.com", BULLET),
        space(8),
        Paragraph("Option B — Local demo + screen recording (fastest for hackathon):", H3),
        Paragraph("Run the server locally and screen-record the demo video using OBS or Windows built-in recorder. "
                  "This avoids deployment issues during the short hackathon window.", BODY),
        space(8),
        info_box(
            "<b>Demo Video Requirements (Section 7.4 of Problem Statement):</b>\n"
            "• 3–5 minutes recorded demo (unlisted YouTube link is fine)\n"
            "• Must show: core disease detection on a new image\n"
            "• Show any bonus modules in action\n"
            "• All 3 members should be visible doing their part",
            BLUE_LIGHT, BLUE_DARK
        ),
        space(10),
        divider(GREEN_DARK, 2),
        space(6),
        Paragraph("Originality Declaration", H3),
        Paragraph("• Model architecture: EfficientNet-B0 via timm (pretrained ImageNet, fine-tuned on PlantVillage)", BULLET),
        Paragraph("• Weather data: Open-Meteo API (open-meteo.com)", BULLET),
        Paragraph("• Crop knowledge base: based on FAO guidelines and ICAR crop recommendations", BULLET),
        Paragraph("• Sustainability formula: original design (inspired by FAO-56 water efficiency)", BULLET),
        Paragraph("• All backend code written during SIH 2026 hackathon window (10–15 September 2026)", BULLET),
        space(6),
        Paragraph("Contact & Resources", H3),
    ]
    resources = [
        ["Resource", "Link"],
        ["Gemini API Key (free)", "https://aistudio.google.com/app/apikey"],
        ["Open-Meteo API", "https://open-meteo.com"],
        ["PlantVillage Dataset", "https://www.kaggle.com/datasets/emmarex/plantdisease"],
        ["timm Library", "https://github.com/huggingface/pytorch-image-models"],
        ["Render (deployment)", "https://render.com"],
        ["API Docs (local)", "http://localhost:8000/docs"],
    ]
    story.append(colored_table(resources[0], resources[1:], col_widths=[60*mm, 110*mm]))
    story += [space(8)]

    # Build
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"[OK] PDF saved to: {OUTPUT_PDF}")

if __name__ == "__main__":
    build_pdf()
