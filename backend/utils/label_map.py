"""
AgriSmart AI — Disease Label Map & Precautions (38 Classes)
Matches the PlantVillage 38-class dataset format trained in model/best_agri_model.pth.
Provides clean display names, healthy classifications, and 3-tier precautions
(Organic, Cultural, Chemical) for all 38 supported crop pathology conditions.
"""

INDEX_TO_LABEL = {
    0:  "Apple___Apple_scab",
    1:  "Apple___Black_rot",
    2:  "Apple___Cedar_apple_rust",
    3:  "Apple___healthy",
    4:  "Blueberry___healthy",
    5:  "Cherry_(including_sour)___Powdery_mildew",
    6:  "Cherry_(including_sour)___healthy",
    7:  "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    8:  "Corn_(maize)___Common_rust_",
    9:  "Corn_(maize)___Northern_Leaf_Blight",
    10: "Corn_(maize)___healthy",
    11: "Grape___Black_rot",
    12: "Grape___Esca_(Black_Measles)",
    13: "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    14: "Grape___healthy",
    15: "Orange___Haunglongbing_(Citrus_greening)",
    16: "Peach___Bacterial_spot",
    17: "Peach___healthy",
    18: "Pepper,_bell___Bacterial_spot",
    19: "Pepper,_bell___healthy",
    20: "Potato___Early_blight",
    21: "Potato___Late_blight",
    22: "Potato___healthy",
    23: "Raspberry___healthy",
    24: "Soybean___healthy",
    25: "Squash___Powdery_mildew",
    26: "Strawberry___Leaf_scorch",
    27: "Strawberry___healthy",
    28: "Tomato___Bacterial_spot",
    29: "Tomato___Early_blight",
    30: "Tomato___Late_blight",
    31: "Tomato___Leaf_Mold",
    32: "Tomato___Septoria_leaf_spot",
    33: "Tomato___Spider_mites Two-spotted_spider_mite",
    34: "Tomato___Target_Spot",
    35: "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    36: "Tomato___Tomato_mosaic_virus",
    37: "Tomato___healthy",
}

LABEL_TO_INDEX = {v: k for k, v in INDEX_TO_LABEL.items()}
NUM_CLASSES = len(INDEX_TO_LABEL)  # 38

# Human-readable display names
LABEL_DISPLAY = {
    "Apple___Apple_scab": "Apple Scab",
    "Apple___Black_rot": "Apple Black Rot",
    "Apple___Cedar_apple_rust": "Apple Cedar Rust",
    "Apple___healthy": "Apple Healthy",
    "Blueberry___healthy": "Blueberry Healthy",
    "Cherry_(including_sour)___Powdery_mildew": "Cherry Powdery Mildew",
    "Cherry_(including_sour)___healthy": "Cherry Healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "Corn Grey Leaf Spot",
    "Corn_(maize)___Common_rust_": "Corn Common Rust",
    "Corn_(maize)___Northern_Leaf_Blight": "Corn Northern Leaf Blight",
    "Corn_(maize)___healthy": "Corn Healthy",
    "Grape___Black_rot": "Grape Black Rot",
    "Grape___Esca_(Black_Measles)": "Grape Esca (Black Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "Grape Leaf Blight (Isariopsis)",
    "Grape___healthy": "Grape Healthy",
    "Orange___Haunglongbing_(Citrus_greening)": "Citrus Greening (Huanglongbing)",
    "Peach___Bacterial_spot": "Peach Bacterial Spot",
    "Peach___healthy": "Peach Healthy",
    "Pepper,_bell___Bacterial_spot": "Bell Pepper Bacterial Spot",
    "Pepper,_bell___healthy": "Bell Pepper Healthy",
    "Potato___Early_blight": "Potato Early Blight",
    "Potato___Late_blight": "Potato Late Blight",
    "Potato___healthy": "Potato Healthy",
    "Raspberry___healthy": "Raspberry Healthy",
    "Soybean___healthy": "Soybean Healthy",
    "Squash___Powdery_mildew": "Squash Powdery Mildew",
    "Strawberry___Leaf_scorch": "Strawberry Leaf Scorch",
    "Strawberry___healthy": "Strawberry Healthy",
    "Tomato___Bacterial_spot": "Tomato Bacterial Spot",
    "Tomato___Early_blight": "Tomato Early Blight",
    "Tomato___Late_blight": "Tomato Late Blight",
    "Tomato___Leaf_Mold": "Tomato Leaf Mould",
    "Tomato___Septoria_leaf_spot": "Tomato Septoria Leaf Spot",
    "Tomato___Spider_mites Two-spotted_spider_mite": "Tomato Spider Mites",
    "Tomato___Target_Spot": "Tomato Target Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "Tomato Yellow Leaf Curl Virus",
    "Tomato___Tomato_mosaic_virus": "Tomato Mosaic Virus",
    "Tomato___healthy": "Tomato Healthy",
}

# Healthy labels set
HEALTHY_LABELS = {label for label in INDEX_TO_LABEL.values() if "healthy" in label.lower()}

# Structured 3-tier precautions and summary text per disease
PRECAUTIONS = {
    "Apple___Apple_scab": {
        "organic": "Apply sulfur or copper octanoate spray during bud swelling. Rake and compost fallen leaves.",
        "cultural": "Prune tree canopies to maximize sunlight and rapid leaf drying. Avoid overhead sprinkler irrigation.",
        "chemical": "Spray Captan 50 WP (2 g/L) or Mancozeb 75 WP at green tip and petal fall stages.",
        "summary": "Venturia inaequalis fungus causing velvety olive-green to black foliar and fruit lesions.",
    },
    "Apple___Black_rot": {
        "organic": "Prune out mummified fruit, dead cankered twigs, and clear orchard debris.",
        "cultural": "Sterilize shears with 70% alcohol between cuts. Paint trunk bark wounds with grafting sealant.",
        "chemical": "Apply Thiophanate-methyl or Captan from pink bud stage through harvest intervals.",
        "summary": "Botryosphaeria obtusa fungus causing leaf frogeye spots, wood cankers, and fruit rot.",
    },
    "Apple___Cedar_apple_rust": {
        "organic": "Remove nearby eastern red cedar and juniper hosts within 200–500m radius if possible.",
        "cultural": "Select rust-resistant cultivars (Liberty, Enterprise, Freedom). Maintain open canopy.",
        "chemical": "Apply Myclobutanil or Propiconazole at pink bud stage and reapply every 10–14 days during wet spring.",
        "summary": "Gymnosporangium juniperi-virginianae heteroecious rust producing bright orange-yellow foliar spots.",
    },
    "Apple___healthy": {
        "organic": "Maintain regular seaweed extract foliar spray and compost mulching.",
        "cultural": "Scout weekly for aphids and leaf-miners. Monitor soil moisture around drip zones.",
        "chemical": "No chemical intervention needed. Maintain routine seasonal dormant oil spray.",
        "summary": "Foliage exhibits vigorous chlorophyll pigmentation, intact cuticle, and healthy venation.",
    },
    "Blueberry___healthy": {
        "organic": "Apply pine needle or acidic peat mulch to sustain soil pH between 4.5 and 5.2.",
        "cultural": "Ensure well-drained raised beds and steady drip irrigation.",
        "chemical": "No chemical intervention required.",
        "summary": "Blueberry foliage is healthy with balanced vegetative growth and deep green coloration.",
    },
    "Cherry_(including_sour)___Powdery_mildew": {
        "organic": "Spray potassium bicarbonate (3 g/L) or diluted neem oil (0.5%) at first sign of white mycelium.",
        "cultural": "Prune water sprouts and interior suckers to promote air circulation throughout the tree crown.",
        "chemical": "Apply Myclobutanil or Tebuconazole fungicide at petal fall and shuck-split stages.",
        "summary": "Podosphaera clandestina fungus creating white powdery powdery patches on young foliage.",
    },
    "Cherry_(including_sour)___healthy": {
        "organic": "Apply vermicompost tea during fruit set to enhance leaf turgor and resilience.",
        "cultural": "Prune dead wood in dry summer conditions to prevent wound infections.",
        "chemical": "No chemical treatment required.",
        "summary": "Cherry leaf tissue shows optimal photosynthesis capacity with intact cellular structure.",
    },
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "organic": "Incorporate Trichoderma viride bio-fungicide in furrow. Practice 2-year crop rotation with non-hosts.",
        "cultural": "Chop and till corn stubble residue deep into the soil after harvest to accelerate decomposition.",
        "chemical": "Apply Pyraclostrobin + Fluxapyroxad or Azoxystrobin at tasseling (VT/R1) when humidity exceeds 85%.",
        "summary": "Cercospora zeae-maydis pathogen causing rectangular tan lesions bounded by leaf veins.",
    },
    "Corn_(maize)___Common_rust_": {
        "organic": "Plant rust-tolerant hybrid lines. Spray diluted fermented butter milk or cow urine bio-protectant.",
        "cultural": "Avoid excessive nitrogen fertilization which produces succulent, rust-susceptible foliage.",
        "chemical": "Apply Mancozeb 75 WP (2.5 g/L) or Azoxystrobin 23 SC (1 ml/L) upon detecting pustules.",
        "summary": "Puccinia sorghi rust producing oval reddish-brown powdery pustules on both leaf surfaces.",
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "organic": "Apply bio-control sprays containing Bacillus subtilis. Rotate with legumes or brassicas.",
        "cultural": "Bury corn debris to break fungal survival in soil. Ensure balanced potash fertilization.",
        "chemical": "Apply Propiconazole 25 EC (1 ml/L) or Azoxystrobin at early onset before cob silking.",
        "summary": "Exserohilum turcicum causing large cigar-shaped grayish-green lesions across foliar blades.",
    },
    "Corn_(maize)___healthy": {
        "organic": "Top-dress with composted farmyard manure and bio-fertilizers (Azospirillum).",
        "cultural": "Maintain optimum plant population (60,000–65,000 plants/ha) and field weed-free state.",
        "chemical": "No chemical treatment needed.",
        "summary": "Maize foliage displays uniform dark green color, healthy vascular bundles, and excellent vigor.",
    },
    "Grape___Black_rot": {
        "organic": "Destroy mummified berries hanging on canes or on ground. Spray copper hydroxide before bud break.",
        "cultural": "Train vines on trellis for optimal airflow and rapid drying of morning dew.",
        "chemical": "Apply Mancozeb 75 WP or Myclobutanil beginning at 1-inch shoot growth through bloom.",
        "summary": "Guignardia bidwellii fungus producing circular brown spots on leaves and shriveling berry clusters.",
    },
    "Grape___Esca_(Black_Measles)": {
        "organic": "Apply Trichoderma-based pruning wound protectant immediately after pruning.",
        "cultural": "Avoid large pruning wounds during wet weather. Mark and monitor affected vines separately.",
        "chemical": "No single chemical cure; paint wounds with wound sealants containing tebuconazole.",
        "summary": "Fungal complex (Phaeomoniella, Phaeoacremonium) causing 'tiger-stripe' interveinal leaf necrosis.",
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "organic": "Spray Bordeaux mixture (1%) or Copper oxychloride (2.5 g/L) at post-pruning stages.",
        "cultural": "Collect and burn fallen leaves beneath the canopy to minimize overwintering spores.",
        "chemical": "Spray Carbendazim 50 WP (1 g/L) or Difenoconazole 25 EC (0.5 ml/L) upon early spotting.",
        "summary": "Pseudocercospora vitis causing irregular dark brown spots with darker purplish margins.",
    },
    "Grape___healthy": {
        "organic": "Foliar spray with micronutrient mixture and amino-acid enriched seaweed extract.",
        "cultural": "Maintain canonical shoot positioning and canopy thinning to prevent microclimate moisture traps.",
        "chemical": "No chemical treatment required.",
        "summary": "Grapevine leaf is robust, well-expanded, with glossy cuticular surface and vibrant green pigmentation.",
    },
    "Orange___Haunglongbing_(Citrus_greening)": {
        "organic": "Release parasitic wasps (Tamarixia radiata) for biological control of the Asian citrus psyllid vector.",
        "cultural": "Scout and eradicate severely infected trees to prevent orchard-wide epidemic spread.",
        "chemical": "Systemic insecticide treatment (Imidacloprid 17.8 SL @ 0.5 ml/L) targeting psyllid vectors, plus zinc/iron foliar nutrients.",
        "summary": "Candidatus Liberibacter bacterium causing asymmetric blotchy mottle, yellow shoots, and bitter lopsided fruit.",
    },
    "Peach___Bacterial_spot": {
        "organic": "Apply dormant copper spray before bud swell. Spray bio-stimulant foliar zinc.",
        "cultural": "Avoid sandblasting wounds in windy orchards by establishing windbreaks. Avoid sprinkler overhead irrigation.",
        "chemical": "Apply Oxytetracycline or low-dose copper bactericide according to label warning thresholds.",
        "summary": "Xanthomonas arboricola pv. pruni bacteria creating angular water-soaked purplish lesions that drop out (shot-hole).",
    },
    "Peach___healthy": {
        "organic": "Mulch root zones with well-aged compost and mycorrhizal inoculants.",
        "cultural": "Maintain summer pruning to permit 50%+ sunlight penetration to lower fruiting spurs.",
        "chemical": "No chemical spray needed.",
        "summary": "Peach foliage is fully expanded, shiny green, without chlorotic stippling or necrotic shot-holes.",
    },
    "Pepper,_bell___Bacterial_spot": {
        "organic": "Apply Bacillus amyloliquefaciens bio-bactericide or Copper hydroxide (2 g/L) preventively.",
        "cultural": "Use certified pathogen-free seeds; do not work in pepper fields while foliage is wet.",
        "chemical": "Apply Copper oxychloride + Streptocycline (0.5 g/L) at first detection of water-soaked spots.",
        "summary": "Xanthomonas euvesicatoria causing small circular to irregular water-soaked spots on leaves and fruit.",
    },
    "Pepper,_bell___healthy": {
        "organic": "Apply vermiwash foliar feed (5%) and neem cake around root basins.",
        "cultural": "Maintain consistent drip irrigation and stake plants to keep leaves off damp soil.",
        "chemical": "No chemical application necessary.",
        "summary": "Bell pepper foliage is healthy, vibrant green, and exhibiting sturdy vegetative branching.",
    },
    "Potato___Early_blight": {
        "organic": "Spray potassium silicate or copper octanoate. Avoid nitrogen deficiency which stresses older leaves.",
        "cultural": "Rotate away from solanaceous crops for 3 years. Mulch soil to prevent rain-splash transmission.",
        "chemical": "Apply Chlorothalonil 75 WP (2 g/L) or Mancozeb 75 WP (2.5 g/L) on a 7–10 day protective schedule.",
        "summary": "Alternaria solani fungus forming characteristic concentric target-board rings on lower mature leaves.",
    },
    "Potato___Late_blight": {
        "organic": "Apply Copper Oxychloride (3 g/L) preventively. Destroy infected haulms prior to tuber harvest.",
        "cultural": "Hill up soil around potato ridges to prevent spore wash into tubers. Avoid late evening sprinkler irrigation.",
        "chemical": "IMMEDIATE: Apply Cymoxanil + Mancozeb (2 g/L) or Metalaxyl-M (1.5 g/L) with translaminar curative action.",
        "summary": "Phytophthora infestans water-mold causing rapid water-soaked brown lesions with white fuzzy sporulation beneath.",
    },
    "Potato___healthy": {
        "organic": "Apply balanced organic NPK with potassium sulfate to support tuber starch expansion.",
        "cultural": "Inspect field margins and low spots weekly for early symptom emergence.",
        "chemical": "No chemical intervention needed.",
        "summary": "Potato plant canopy shows intact leaf margins, dense foliage, and optimal photosynthetic health.",
    },
    "Raspberry___healthy": {
        "organic": "Maintain compost mulch and beneficial predatory mite populations.",
        "cultural": "Trellis primocanes and floricanes cleanly to sustain horizontal airflow.",
        "chemical": "No chemical application necessary.",
        "summary": "Raspberry cane foliage is clear, serrated margins intact, without rust or fungal spotting.",
    },
    "Soybean___healthy": {
        "organic": "Ensure effective seed inoculation with Bradyrhizobium japonicum.",
        "cultural": "Maintain optimum row spacing (45 cm) and field drainage to avert root rot.",
        "chemical": "No chemical application necessary.",
        "summary": "Soybean trifoliate leaves show uniform lush green pigmentation with strong nitrogen-fixation vigor.",
    },
    "Squash___Powdery_mildew": {
        "organic": "Spray 10% cow milk solution, potassium bicarbonate (4 g/L), or neem oil (5 ml/L).",
        "cultural": "Plant in full sun; space vines at 1.5–2m. Water only at the soil level via drip lines.",
        "chemical": "Apply Azoxystrobin 23 SC (1 ml/L) or Dinocap (1 ml/L) at early talcum-like spotting.",
        "summary": "Podosphaera xanthii powdery mildew covering upper and lower leaf surfaces in white fungal powdery carpets.",
    },
    "Strawberry___Leaf_scorch": {
        "organic": "Remove old dead leaves after harvest. Spray copper soap bio-fungicide.",
        "cultural": "Renovate strawberry beds after picking. Improve spacing to allow air circulation.",
        "chemical": "Apply Captan 50 WP or Thiophanate-methyl before flowering and post-harvest.",
        "summary": "Diplocarpon earlianum fungus causing numerous small purple-to-brown irregular blotches on leaves.",
    },
    "Strawberry___healthy": {
        "organic": "Apply straw mulching under leaves to keep fruit and leaves elevated above wet soil.",
        "cultural": "Irrigate via subterranean or surface drip tubes beneath plastic mulch.",
        "chemical": "No chemical spray needed.",
        "summary": "Strawberry crowns and leaves are vigorous, dark green, free from spots or edge scorch.",
    },
    "Tomato___Bacterial_spot": {
        "organic": "Spray Bacillus subtilis or fixed copper formulations preventatively.",
        "cultural": "Avoid handling plants when wet; clean stakes and ties with disinfectant before re-use.",
        "chemical": "Apply Copper Hydroxide (2 g/L) + Mancozeb (2 g/L) or Kasugamycin (2 ml/L) every 7 days.",
        "summary": "Xanthomonas perforans causing small dark water-soaked spots with yellow halos across leaflets.",
    },
    "Tomato___Early_blight": {
        "organic": "Prune bottom 12 inches of foliage. Mulch ground heavily. Spray Trichoderma viride.",
        "cultural": "Stake plants for upright growth. Water base only; never wet leaves in the evening.",
        "chemical": "Spray Chlorothalonil 75 WP (2 g/L) or Azoxystrobin + Difenoconazole (1 ml/L).",
        "summary": "Alternaria linariae producing target-pattern concentric rings on older lower leaves.",
    },
    "Tomato___Late_blight": {
        "organic": "Apply copper hydroxide immediately; bag and remove infected vines away from field.",
        "cultural": "Ensure rapid drainage. Plant certified resistant hybrids (e.g. Mountain Magic, Defiant).",
        "chemical": "HIGH PRIORITY: Spray Dimethomorph (1 g/L) + Mancozeb (2 g/L) or Metalaxyl-M (2 g/L) immediately.",
        "summary": "Phytophthora infestans aggressive pathogen causing rapid greasy brown patches and canopy collapse.",
    },
    "Tomato___Leaf_Mold": {
        "organic": "Ventilate greenhouses aggressively to lower relative humidity below 80%.",
        "cultural": "Prune dense interior foliage to allow horizontal breeze. Avoid high plant density.",
        "chemical": "Apply Chlorothalonil or Difenoconazole (0.5 ml/L) targeting leaf undersides.",
        "summary": "Passalora fulva fungus creating pale green to yellow spots on upper leaf surfaces and olive-velvet mold beneath.",
    },
    "Tomato___Septoria_leaf_spot": {
        "organic": "Remove spotted lower leaflets as soon as they appear. Keep soil covered with straw mulch.",
        "cultural": "Practice 2-year crop rotation. Space indeterminate tomato plants 60–90 cm apart.",
        "chemical": "Apply Mancozeb 75 WP (2.5 g/L) or Chlorothalonil (2 g/L) starting right after transplant establishment.",
        "summary": "Septoria lycopersici fungus creating tiny circular spots with dark brown margins and gray centers.",
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "organic": "Spray cold-pressed neem oil (5 ml/L) or insecticidal soap. Introduce predatory mites (Phytoseiulus persimilis).",
        "cultural": "Misting overhead during hot dry spells helps suppress mite population explosions.",
        "chemical": "Apply Abamectin 1.9 EC (0.5 ml/L) or Spiromesifen 22.9 SC (1 ml/L) targeting leaf undersides.",
        "summary": "Tetranychus urticae arachnids producing fine foliar stippling, chlorosis, and silky webbing under leaves.",
    },
    "Tomato___Target_Spot": {
        "organic": "Apply bio-control Bacillus amyloliquefaciens. Maintain generous row spacing.",
        "cultural": "Discard infected cull tomatoes far from field. Disinfect trellis stakes between seasons.",
        "chemical": "Apply Azoxystrobin (1 ml/L) or Boscalid + Pyraclostrobin at early symptom onset.",
        "summary": "Corynespora cassiicola causing brown pinpoint lesions expanding into target-like circular necrotic zones.",
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "organic": "Install 40-mesh insect-proof netting in nurseries. Spray Beauveria bassiana against whiteflies.",
        "cultural": "Eradicate alternate weed hosts (nightshades). Place yellow sticky traps (1 trap/50 sq.m) for monitoring.",
        "chemical": "Control whitefly vectors using Acetamiprid 20 SP (0.5 g/L) or Spirotetramat (1 ml/L). Remove symptomatic plants.",
        "summary": "Begomovirus transmitted by Bemisia tabaci whiteflies, causing stunted bushy growth and upward cupped leaves.",
    },
    "Tomato___Tomato_mosaic_virus": {
        "organic": "Wash hands with milk or soap before touching plants; smokers must sanitize hands prior to field work.",
        "cultural": "Rogue out infected plants immediately. Disinfect tools in 10% trisodium phosphate solution.",
        "chemical": "No chemical cures viruses. Focus strictly on sanitation, resistant seed varieties, and clean propagation.",
        "summary": "Tobamovirus causing mottled light and dark green mosaic patterns, leaf puckering, and filiform shoestring leaves.",
    },
    "Tomato___healthy": {
        "organic": "Apply seaweed extract foliar spray and compost tea every 14 days during flowering and fruit sizing.",
        "cultural": "Maintain regular watering to prevent blossom end rot. Keep plants securely trellised.",
        "chemical": "No chemical intervention needed. Monitor regularly for early blight signs.",
        "summary": "Tomato vine shows deep green lush foliage, sturdy stems, and balanced photosynthetic growth.",
    },
}


def get_label_info(label: str) -> dict:
    """
    Return comprehensive agronomic info, clean display name, healthy flag,
    and 3-tier precautions for any given disease label.
    """
    display_name = LABEL_DISPLAY.get(label, label.replace("___", " — ").replace("_", " "))
    prec = PRECAUTIONS.get(label, {
        "organic": "Apply biological preventive bio-pesticides or neem extract.",
        "cultural": "Prune infected sections and improve field airflow and drainage.",
        "chemical": "Consult local agricultural university or extension officer for targeted spray.",
        "summary": "Pathological condition identified on foliar sample.",
    })
    is_healthy = label in HEALTHY_LABELS

    # Extract crop name
    crop_name = label.split("___")[0].replace("_", " ").replace("(including sour)", "").replace("(maize)", "").strip()

    return {
        "label": label,
        "crop": crop_name,
        "display_name": display_name,
        "is_healthy": is_healthy,
        "precaution": prec.get("chemical") or prec.get("organic") or "Maintain routine crop monitoring.",
        "precautions": {
            "organic": prec.get("organic", "Apply preventive organic bio-agents."),
            "cultural": prec.get("cultural", "Improve aeration and field hygiene."),
            "chemical": prec.get("chemical", "Consult agronomist if economic threshold exceeded."),
        },
        "summary": prec.get("summary", f"Condition detected on {crop_name} foliage."),
    }
