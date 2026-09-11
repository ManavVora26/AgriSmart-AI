/**
 * AgriSmart AI - API Service Layer
 * 
 * Future Integration Notice for Backend / ML Teammate:
 * ----------------------------------------------------
 * All backend API communications are strictly isolated in this file.
 * The rest of the frontend (main.js, UI, forms) only calls the functions below.
 * 
 * To connect to the real backend:
 * 1. Set `USE_MOCK_API = false` below (or swap lines inside individual functions).
 * 2. Update `API_BASE_URL` with your server address (e.g. 'http://localhost:8000' or '/api').
 * 3. Uncomment the REAL `fetch(...)` block in the respective function.
 */

// Toggle between Mock mode and Real Backend mode
const USE_MOCK_API = true;
const API_BASE_URL = 'http://localhost:8000/api';

/**
 * 1. Disease Detection (Core)
 * Uploads leaf image with contextual farm telemetry.
 * 
 * @param {File|Blob|Object} imageFile - The leaf image file or mock preset
 * @param {Object} farmContext - Farm telemetry: { cropType, growthStage, soilType, ph, soilMoisture, temperature, rainProb, location }
 * @returns {Promise<Object>} Predicted disease, confidence, symptoms, precautions
 */
async function predictDisease(imageFile, farmContext = {}) {
  /*
  // ==========================================
  // REAL BACKEND INTEGRATION (Uncomment when ready):
  // ==========================================
  const formData = new FormData();
  if (imageFile instanceof File || imageFile instanceof Blob) {
    formData.append('image', imageFile, imageFile.name || 'leaf_sample.jpg');
  } else if (imageFile?.file instanceof File) {
    formData.append('image', imageFile.file, imageFile.file.name);
  }
  formData.append('crop_type', farmContext.cropType || 'Tomato');
  formData.append('growth_stage', farmContext.growthStage || 'Vegetative');
  formData.append('soil_type', farmContext.soilType || 'Loamy');
  formData.append('ph', farmContext.ph || 6.5);
  formData.append('soil_moisture', farmContext.soilMoisture || 45);
  formData.append('temperature', farmContext.temperature || 28);
  formData.append('rain_probability', farmContext.rainProb || 30);
  formData.append('location', farmContext.location || 'Farm Plot');

  const response = await fetch(`${API_BASE_URL}/predict-disease`, {
    method: 'POST',
    body: formData
    // Note: Do not set Content-Type header when sending FormData; browser sets boundary automatically
  });

  if (!response.ok) {
    throw new Error(`Disease analysis service error: ${response.status} ${response.statusText}`);
  }
  return await response.json();
  */

  // MOCK (Current):
  return window.AgriSmartMock.mockPredictDisease(imageFile, farmContext);
}

/**
 * 2. Crop Recommendation (Bonus A)
 * Recommends best crops based on soil nutrients and climatic parameters.
 * 
 * @param {Object} soilData - { ph, moisture, temperature, rainProb, soilType, location }
 * @returns {Promise<Object>} Ranked crops with suitability scores and justifications
 */
async function recommendCrop(soilData = {}) {
  /*
  // ==========================================
  // REAL BACKEND INTEGRATION (Uncomment when ready):
  // ==========================================
  const response = await fetch(`${API_BASE_URL}/recommend-crop`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    body: JSON.stringify({
      ph: Number(soilData.ph) || 6.5,
      moisture: Number(soilData.moisture) || 45,
      temperature: Number(soilData.temperature) || 28,
      rainfall_prob: Number(soilData.rainProb) || 30,
      soil_type: soilData.soilType || 'Loamy',
      location: soilData.location || 'Local'
    })
  });

  if (!response.ok) {
    throw new Error(`Crop recommendation service error: ${response.status} ${response.statusText}`);
  }
  return await response.json();
  */

  // MOCK (Current):
  return window.AgriSmartMock.mockRecommendCrop(soilData);
}

/**
 * 3. Smart Irrigation Advice (Bonus B)
 * Computes whether irrigation is needed based on real-time soil moisture and weather outlook.
 * 
 * @param {Object} data - { moisture, rainProb, temp, crop, soilType }
 * @returns {Promise<Object>} Binary decision (needed: true/false), reasoning, volume, delivery window
 */
async function getIrrigationAdvice(data = {}) {
  /*
  // ==========================================
  // REAL BACKEND INTEGRATION (Uncomment when ready):
  // ==========================================
  const queryParams = new URLSearchParams({
    moisture: data.moisture ?? 42,
    rain_prob: data.rainProb ?? 65,
    temp: data.temp ?? 28,
    crop: data.crop || 'Tomato',
    soil_type: data.soilType || 'Loamy'
  });

  const response = await fetch(`${API_BASE_URL}/irrigation/advice?${queryParams}`, {
    method: 'GET',
    headers: { 'Accept': 'application/json' }
  });

  if (!response.ok) {
    throw new Error(`Irrigation advisory service error: ${response.status} ${response.statusText}`);
  }
  return await response.json();
  */

  // MOCK (Current):
  return window.AgriSmartMock.mockGetIrrigationAdvice(data);
}

/**
 * 4. Weather-Based Intelligence (Bonus C)
 * Retrieves local agro-meteorological metrics and prioritized farmer action banners.
 * 
 * @param {string} location - Farm location string or lat,lon
 * @returns {Promise<Object>} Current weather, action banners, 5-day agro-forecast
 */
async function getWeatherAdvice(location = 'Nashik Valley, MH') {
  /*
  // ==========================================
  // REAL BACKEND INTEGRATION (Uncomment when ready):
  // ==========================================
  const response = await fetch(`${API_BASE_URL}/weather/advisory?location=${encodeURIComponent(location)}`, {
    method: 'GET',
    headers: { 'Accept': 'application/json' }
  });

  if (!response.ok) {
    throw new Error(`Weather service error: ${response.status} ${response.statusText}`);
  }
  return await response.json();
  */

  // MOCK (Current):
  return window.AgriSmartMock.mockGetWeatherAdvice(location);
}

/**
 * 5. Sustainability Score (Bonus D)
 * Evaluates farm eco-efficiency (0–100) across 4 agricultural pillars.
 * 
 * @param {Object} data - Farm resource telemetry
 * @returns {Promise<Object>} Overall score, grade, pillar breakdowns, 3 improvement recommendations
 */
async function getSustainabilityScore(data = {}) {
  /*
  // ==========================================
  // REAL BACKEND INTEGRATION (Uncomment when ready):
  // ==========================================
  const response = await fetch(`${API_BASE_URL}/sustainability/score`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });

  if (!response.ok) {
    throw new Error(`Sustainability service error: ${response.status} ${response.statusText}`);
  }
  return await response.json();
  */

  // MOCK (Current):
  return window.AgriSmartMock.mockGetSustainabilityScore(data);
}

/**
 * 6. Farmer Assistant (Bonus E)
 * Conversational plain-language AI assistant with regional language support.
 * 
 * @param {string} question - Farmer's typed query
 * @param {string} language - ISO language code ('en', 'hi', 'mr', 'te', 'es')
 * @returns {Promise<Object>} Text response, language, timestamp
 */
async function askAssistant(question, language = 'en') {
  /*
  // ==========================================
  // REAL BACKEND INTEGRATION (Uncomment when ready):
  // ==========================================
  const response = await fetch(`${API_BASE_URL}/assistant/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    body: JSON.stringify({
      query: question,
      language: language,
      session_id: window.currentSessionId || 'default-session'
    })
  });

  if (!response.ok) {
    throw new Error(`Farmer Assistant service error: ${response.status} ${response.statusText}`);
  }
  return await response.json();
  */

  // MOCK (Current):
  return window.AgriSmartMock.mockAskAssistant(question, language);
}

/**
 * 7. Agentic Advisor Feed (Bonus G)
 * Retrieves chronological timeline of autonomous agent monitor events.
 * 
 * @returns {Promise<Array>} List of agentic monitoring events
 */
async function getAgenticFeed() {
  /*
  // ==========================================
  // REAL BACKEND INTEGRATION (Uncomment when ready):
  // ==========================================
  const response = await fetch(`${API_BASE_URL}/agentic/feed`, {
    method: 'GET',
    headers: { 'Accept': 'application/json' }
  });

  if (!response.ok) {
    throw new Error(`Agent feed service error: ${response.status} ${response.statusText}`);
  }
  return await response.json();
  */

  // MOCK (Current):
  return window.AgriSmartMock.mockGetAgenticFeed();
}

/**
 * Bonus: Trigger on-demand agent cycle
 */
async function triggerAgentCheck() {
  /*
  // ==========================================
  // REAL BACKEND INTEGRATION (Uncomment when ready):
  // ==========================================
  const response = await fetch(`${API_BASE_URL}/agentic/trigger-cycle`, {
    method: 'POST',
    headers: { 'Accept': 'application/json' }
  });
  if (!response.ok) throw new Error('Agent cycle trigger failed');
  return await response.json();
  */

  // MOCK (Current):
  return window.AgriSmartMock.mockGenerateAgentEvent();
}

// Export functions to global scope for clean vanilla JS usage
window.AgriSmartAPI = {
  predictDisease,
  recommendCrop,
  getIrrigationAdvice,
  getWeatherAdvice,
  getSustainabilityScore,
  askAssistant,
  getAgenticFeed,
  triggerAgentCheck
};
