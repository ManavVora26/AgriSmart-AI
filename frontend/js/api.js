/**
 * AgriSmart AI - API Service Layer
 * 
 * Connected to live FastAPI Backend (http://localhost:8000/api)
 * Seamlessly falls back to mock engine if the backend is unreachable.
 */

// Toggle between Mock mode and Real Backend mode
const USE_MOCK_API = false; // Live Backend Enabled!
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
  if (!USE_MOCK_API) {
    try {
      const formData = new FormData();
      if (imageFile instanceof File || imageFile instanceof Blob) {
        formData.append('image', imageFile, imageFile.name || 'leaf_sample.jpg');
      } else if (imageFile?.file instanceof File) {
        formData.append('image', imageFile.file, imageFile.file.name);
      }
      formData.append('crop_type', farmContext.cropType || 'Tomato');
      formData.append('growth_stage', farmContext.growthStage || 'Vegetative');
      formData.append('soil_type', farmContext.soilType || 'Loamy');
      formData.append('ph', String(farmContext.ph ?? 6.5));
      formData.append('soil_moisture', String(farmContext.soilMoisture ?? 45));
      formData.append('temperature', String(farmContext.temperature ?? 28));
      formData.append('rain_probability', String(farmContext.rainProb ?? 30));
      formData.append('location', farmContext.location || 'Farm Plot');

      const response = await fetch(`${API_BASE_URL}/predict-disease`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Disease analysis service error: ${response.status} ${response.statusText}`);
      }
      return await response.json();
    } catch (err) {
      console.warn('Backend /predict-disease unreachable, falling back to mock:', err);
    }
  }

  // Fallback to Mock:
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
  if (!USE_MOCK_API) {
    try {
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
          rainfall_prob: Number(soilData.rainProb || soilData.rainfall_prob) || 30,
          soil_type: soilData.soilType || soilData.soil_type || 'Loamy',
          location: soilData.location || 'Local'
        })
      });

      if (!response.ok) {
        throw new Error(`Crop recommendation service error: ${response.status} ${response.statusText}`);
      }
      return await response.json();
    } catch (err) {
      console.warn('Backend /recommend-crop unreachable, falling back to mock:', err);
    }
  }

  // Fallback to Mock:
  return window.AgriSmartMock.mockRecommendCrop(soilData);
}

/**
 * 0. Location Services
 * Geocoding, reverse geocoding, and auto-detecting farm location.
 */
async function detectCurrentLocation() {
  if (!USE_MOCK_API) {
    try {
      const response = await fetch(`${API_BASE_URL}/location/current`, {
        headers: { 'Accept': 'application/json' }
      });
      if (response.ok) return await response.json();
    } catch (e) {
      console.warn('Auto IP location failed, using default:', e);
    }
  }
  return { city: 'Surat', state: 'Gujarat', country: 'India', latitude: 21.1981, longitude: 72.8298, display_name: 'Surat, Gujarat' };
}

async function searchLocation(query) {
  if (!query) return null;
  if (!USE_MOCK_API) {
    try {
      const response = await fetch(`${API_BASE_URL}/location/search?query=${encodeURIComponent(query)}`, {
        headers: { 'Accept': 'application/json' }
      });
      if (response.ok) return await response.json();
    } catch (e) {
      console.warn('Location search failed:', e);
    }
  }
  return { name: query, display_name: query, latitude: 21.1981, longitude: 72.8298 };
}

async function reverseGeocodeLocation(lat, lon) {
  if (!USE_MOCK_API) {
    try {
      const response = await fetch(`${API_BASE_URL}/location/reverse?lat=${lat}&lon=${lon}`, {
        headers: { 'Accept': 'application/json' }
      });
      if (response.ok) return await response.json();
    } catch (e) {
      console.warn('Reverse geocode failed:', e);
    }
  }
  return { city: 'Current Farm', display_name: `${lat.toFixed(3)}°N, ${lon.toFixed(3)}°E`, latitude: lat, longitude: lon };
}

/**
 * 3. Smart Irrigation Advice (Bonus B)
 * Computes whether irrigation is needed based on real-time soil moisture and weather outlook.
 * 
 * @param {Object} data - { moisture, rainProb, temp, crop, soilType, lat, lon, location }
 * @returns {Promise<Object>} Binary decision (needed: true/false), reasoning, volume, delivery window
 */
async function getIrrigationAdvice(data = {}) {
  if (!USE_MOCK_API) {
    try {
      const queryParams = new URLSearchParams({
        moisture: String(data.moisture ?? 42),
        crop: data.crop || 'Tomato',
        soil_type: data.soilType || 'Loamy'
      });

      if (data.rainProb !== undefined && data.rainProb !== null) {
        queryParams.set('rain_prob', String(data.rainProb));
      }
      if (data.temp !== undefined && data.temp !== null) {
        queryParams.set('temp', String(data.temp));
      }
      if (data.lat !== undefined && data.lat !== null) {
        queryParams.set('lat', String(data.lat));
      }
      if (data.lon !== undefined && data.lon !== null) {
        queryParams.set('lon', String(data.lon));
      }
      if (data.location) {
        queryParams.set('location', data.location);
      }

      const response = await fetch(`${API_BASE_URL}/irrigation/advice?${queryParams}`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' }
      });

      if (!response.ok) {
        throw new Error(`Irrigation advisory service error: ${response.status} ${response.statusText}`);
      }
      return await response.json();
    } catch (err) {
      console.warn('Backend /irrigation/advice unreachable, falling back to mock:', err);
    }
  }

  // Fallback to Mock:
  return window.AgriSmartMock.mockGetIrrigationAdvice(data);
}

/**
 * 4. Weather-Based Intelligence (Bonus C)
 * Retrieves local agro-meteorological metrics and prioritized farmer action banners.
 * 
 * @param {string} location - Farm location string or lat,lon
 * @param {number} lat - Latitude
 * @param {number} lon - Longitude
 * @returns {Promise<Object>} Current weather, action banners, 5-day agro-forecast
 */
async function getWeatherAdvice(location = 'Surat, Gujarat', lat = null, lon = null) {
  if (!USE_MOCK_API) {
    try {
      const params = new URLSearchParams();
      if (location) params.set('location', location);
      if (lat !== null && lat !== undefined) params.set('lat', String(lat));
      if (lon !== null && lon !== undefined) params.set('lon', String(lon));

      const response = await fetch(`${API_BASE_URL}/weather/advisory?${params}`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' }
      });

      if (!response.ok) {
        throw new Error(`Weather service error: ${response.status} ${response.statusText}`);
      }
      return await response.json();
    } catch (err) {
      console.warn('Backend /weather/advisory unreachable, falling back to mock:', err);
    }
  }

  // Fallback to Mock:
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
  if (!USE_MOCK_API) {
    try {
      const response = await fetch(`${API_BASE_URL}/sustainability/score`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data || { crop: 'Tomato' })
      });

      if (!response.ok) {
        throw new Error(`Sustainability service error: ${response.status} ${response.statusText}`);
      }
      return await response.json();
    } catch (err) {
      console.warn('Backend /sustainability/score unreachable, falling back to mock:', err);
    }
  }

  // Fallback to Mock:
  return window.AgriSmartMock.mockGetSustainabilityScore(data);
}

/**
 * 6. Farmer Assistant (Bonus E)
 * Conversational plain-language AI assistant with regional language support.
 * 
 * @param {string} question - Farmer's typed query
 * @param {string} language - ISO language code ('en', 'hi', 'mr', 'te', 'es')
 * @param {Object} context - Optional farm context (location, weatherSummary, crop, disease)
 * @returns {Promise<Object>} Text response, language, timestamp
 */
async function askAssistant(question, language = 'en', context = {}) {
  if (!USE_MOCK_API) {
    try {
      const response = await fetch(`${API_BASE_URL}/assistant/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          query: question,
          language: language,
          session_id: window.currentSessionId || 'default-session',
          location: context.location || window.currentFarmLocation?.displayName || 'Surat, Gujarat',
          weather_summary: context.weatherSummary || window.currentWeatherSummary || undefined,
          crop: context.crop || undefined,
          disease_detected: context.diseaseDetected || undefined,
          irrigation_advice: context.irrigationAdvice || undefined,
        })
      });

      if (!response.ok) {
        throw new Error(`Farmer Assistant service error: ${response.status} ${response.statusText}`);
      }
      return await response.json();
    } catch (err) {
      console.warn('Backend /assistant/chat unreachable, falling back to mock:', err);
    }
  }

  // Fallback to Mock:
  return window.AgriSmartMock.mockAskAssistant(question, language);
}

/**
 * 7. Agentic Advisor Feed (Bonus G)
 * Retrieves chronological timeline of autonomous agent monitor events.
 * 
 * @returns {Promise<Array>} List of agentic monitoring events
 */
async function getAgenticFeed() {
  if (!USE_MOCK_API) {
    try {
      const response = await fetch(`${API_BASE_URL}/agentic/feed`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' }
      });

      if (!response.ok) {
        throw new Error(`Agent feed service error: ${response.status} ${response.statusText}`);
      }
      return await response.json();
    } catch (err) {
      console.warn('Backend /agentic/feed unreachable, falling back to mock:', err);
    }
  }

  // Fallback to Mock:
  return window.AgriSmartMock.mockGetAgenticFeed();
}

/**
 * Bonus: Trigger on-demand agent cycle
 */
async function triggerAgentCheck() {
  if (!USE_MOCK_API) {
    try {
      const response = await fetch(`${API_BASE_URL}/agentic/trigger-cycle`, {
        method: 'POST',
        headers: { 'Accept': 'application/json' }
      });
      if (!response.ok) throw new Error('Agent cycle trigger failed');
      return await response.json();
    } catch (err) {
      console.warn('Backend /agentic/trigger-cycle unreachable, falling back to mock:', err);
    }
  }

  // Fallback to Mock:
  return window.AgriSmartMock.mockGenerateAgentEvent();
}

// Export functions to global scope for clean vanilla JS usage
window.AgriSmartAPI = {
  detectCurrentLocation,
  searchLocation,
  reverseGeocodeLocation,
  predictDisease,
  recommendCrop,
  getIrrigationAdvice,
  getWeatherAdvice,
  getSustainabilityScore,
  askAssistant,
  getAgenticFeed,
  triggerAgentCheck
};
