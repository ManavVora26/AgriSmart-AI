"""
AgriSmart AI — Disease Label Map & Precautions
Shared class list from SIH 2026 Problem Statement (C-433).
~15-20 crop-disease classes that exist in BOTH PlantVillage (training)
and PlantDoc-style field images (held-out test set).
"""

# Canonical label → display name
LABEL_DISPLAY = {
    "Tomato___Early_Blight": "Tomato Early Blight",
    "Tomato___Late_Blight": "Tomato Late Blight",
    "Tomato___Leaf_Mold": "Tomato Leaf Mould",
    "Tomato___Bacterial_Spot": "Tomato Bacterial Spot",
    "Tomato___healthy": "Tomato Healthy",
    "Potato___Early_Blight": "Potato Early Blight",
    "Potato___Late_Blight": "Potato Late Blight",
    "Potato___healthy": "Potato Healthy",
    "Corn_(maize)___Common_rust_": "Corn Common Rust",
    "Corn_(maize)___Gray_leaf_spot": "Corn Grey Leaf Spot",
    "Corn_(maize)___healthy": "Corn Healthy",
    "Apple___Apple_scab": "Apple Scab",
    "Apple___Black_rot": "Apple Black Rot",
    "Apple___healthy": "Apple Healthy",
    "Grape___Black_rot": "Grape Black Rot",
    "Grape___healthy": "Grape Healthy",
    "Pepper,_bell___Bacterial_spot": "Bell Pepper Bacterial Spot",
    "Pepper,_bell___healthy": "Bell Pepper Healthy",
}

# Class index → label (index order matches PlantVillage standard ordering)
INDEX_TO_LABEL = {
    0:  "Apple___Apple_scab",
    1:  "Apple___Black_rot",
    2:  "Apple___healthy",
    3:  "Corn_(maize)___Common_rust_",
    4:  "Corn_(maize)___Gray_leaf_spot",
    5:  "Corn_(maize)___healthy",
    6:  "Grape___Black_rot",
    7:  "Grape___healthy",
    8:  "Pepper,_bell___Bacterial_spot",
    9:  "Pepper,_bell___healthy",
    10: "Potato___Early_Blight",
    11: "Potato___Late_Blight",
    12: "Potato___healthy",
    13: "Tomato___Bacterial_Spot",
    14: "Tomato___Early_Blight",
    15: "Tomato___Late_Blight",
    16: "Tomato___Leaf_Mold",
    17: "Tomato___healthy",
}

LABEL_TO_INDEX = {v: k for k, v in INDEX_TO_LABEL.items()}

NUM_CLASSES = len(INDEX_TO_LABEL)  # 18

# Labels that indicate a healthy plant
HEALTHY_LABELS = {k for k in INDEX_TO_LABEL.values() if "healthy" in k.lower()}

# Detailed precaution text per class
PRECAUTIONS = {
    "Apple___Apple_scab": (
        "Apple Scab (Venturia inaequalis): "
        "Remove and destroy fallen leaves. Apply fungicide sprays (e.g., captan, mancozeb) "
        "during wet weather from bud-break. Prune to improve air circulation. "
        "Avoid overhead irrigation. Plant resistant apple varieties where possible."
    ),
    "Apple___Black_rot": (
        "Apple Black Rot (Botryosphaeria obtusa): "
        "Prune out dead or canker-infected wood at least 15 cm below visible infection. "
        "Destroy mummified fruit. Apply copper-based or thiophanate-methyl fungicides. "
        "Avoid injuring bark. Maintain tree vigor with balanced fertilization."
    ),
    "Apple___healthy": (
        "Your apple plant appears healthy! Continue regular monitoring, "
        "balanced fertilization, and protective fungicide schedule during wet seasons."
    ),
    "Corn_(maize)___Common_rust_": (
        "Corn Common Rust (Puccinia sorghi): "
        "Plant rust-resistant hybrids. Apply foliar fungicide (e.g., azoxystrobin, "
        "propiconazole) at early infection signs, especially if weather is cool and humid. "
        "Avoid late planting in rust-prone areas. Crop rotation helps reduce inoculum."
    ),
    "Corn_(maize)___Gray_leaf_spot": (
        "Corn Grey Leaf Spot (Cercospora zeae-maydis): "
        "Use resistant hybrids as the primary defense. Till crop residue to reduce inoculum. "
        "Apply strobilurin or triazole fungicides at VT/R1 stage if conditions favor disease. "
        "Improve field drainage and avoid excessive irrigation."
    ),
    "Corn_(maize)___healthy": (
        "Your maize plant appears healthy! Monitor for early rust or leaf spot symptoms, "
        "especially during humid conditions."
    ),
    "Grape___Black_rot": (
        "Grape Black Rot (Guignardia bidwellii): "
        "Remove and destroy mummified berries and infected canes during dormant pruning. "
        "Apply mancozeb or myclobutanil fungicides starting at bud-break and through bloom. "
        "Improve canopy air circulation. Avoid wounds and train vines properly."
    ),
    "Grape___healthy": (
        "Your grapevine appears healthy! Continue regular scouting for black rot, "
        "powdery mildew, and downy mildew especially during wet spring weather."
    ),
    "Pepper,_bell___Bacterial_spot": (
        "Bell Pepper Bacterial Spot (Xanthomonas campestris): "
        "Use certified disease-free seed or transplants. Apply copper-based bactericides "
        "preventively. Avoid overhead irrigation. Practice 2-3 year crop rotation. "
        "Remove and destroy infected plant debris. Avoid working in wet fields."
    ),
    "Pepper,_bell___healthy": (
        "Your bell pepper plant appears healthy! Watch for water-soaked lesions on leaves "
        "which are early signs of bacterial spot, especially after rain."
    ),
    "Potato___Early_Blight": (
        "Potato Early Blight (Alternaria solani): "
        "Apply chlorothalonil or mancozeb fungicides every 7-10 days when conditions are "
        "favorable (warm, humid). Use certified disease-free seed potatoes. "
        "Maintain adequate plant nutrition (nitrogen). Remove lower infected leaves. "
        "Rotate crops at least every 3 years."
    ),
    "Potato___Late_Blight": (
        "Potato Late Blight (Phytophthora infestans) — HIGH PRIORITY: "
        "Act immediately. Apply metalaxyl+mancozeb or cymoxanil-based fungicide. "
        "Destroy infected haulm before harvesting. Do NOT leave infected debris in the field. "
        "Use certified seed potatoes and resistant varieties. Avoid excessive irrigation. "
        "This disease spreads rapidly and can cause total crop loss."
    ),
    "Potato___healthy": (
        "Your potato plant appears healthy! Scout regularly for late blight symptoms "
        "(dark, water-soaked lesions on leaves), especially during cool, wet conditions."
    ),
    "Tomato___Bacterial_Spot": (
        "Tomato Bacterial Spot (Xanthomonas perforans): "
        "Use copper-based bactericides + mancozeb as protectant spray program. "
        "Start sprays at first sign of disease or when conditions are warm and rainy. "
        "Use disease-free transplants. Avoid overhead irrigation. "
        "Rotate out of tomato and pepper for 2+ years."
    ),
    "Tomato___Early_Blight": (
        "Tomato Early Blight (Alternaria linariae): "
        "Remove affected lower leaves immediately. Apply chlorothalonil, mancozeb, or "
        "azoxystrobin fungicide on a 7-10 day schedule. Mulch around plants to prevent "
        "soil splash. Avoid overhead watering. Stake plants to improve air circulation. "
        "Rotate crops annually."
    ),
    "Tomato___Late_Blight": (
        "Tomato Late Blight (Phytophthora infestans) — HIGH PRIORITY: "
        "Apply metalaxyl + mancozeb fungicide immediately. Remove and bag all infected tissue "
        "— do NOT compost. Avoid overhead irrigation. Monitor neighbors' farms. "
        "In severe cases, remove entire plant to protect the crop. "
        "Humid, cool (15-20°C) nights greatly accelerate spread."
    ),
    "Tomato___Leaf_Mold": (
        "Tomato Leaf Mould (Passalora fulva): "
        "Improve greenhouse ventilation — this disease thrives in high humidity (>85%). "
        "Apply chlorothalonil or copper fungicide at first sign. "
        "Avoid wetting foliage when irrigating. Remove and destroy affected leaves. "
        "Consider resistant varieties for next season."
    ),
    "Tomato___healthy": (
        "Your tomato plant appears healthy! Continue scouting for early blight spots "
        "(brown rings on lower leaves) and keep plants staked for good air circulation."
    ),
}


def get_label_info(label: str) -> dict:
    """Return display name, precaution, and healthy flag for a given label."""
    return {
        "label": label,
        "display_name": LABEL_DISPLAY.get(label, label.replace("___", " — ").replace("_", " ")),
        "precaution": PRECAUTIONS.get(label, "Consult your local agricultural extension officer."),
        "is_healthy": label in HEALTHY_LABELS,
    }
