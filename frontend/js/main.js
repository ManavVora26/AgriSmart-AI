/**
 * AgriSmart AI - Application Controller
 * Vanilla JavaScript (No bundler, No frameworks)
 */

document.addEventListener('DOMContentLoaded', () => {
  'use strict';

  // State Management
  const state = {
    activeSection: 'section-disease',
    selectedImageFile: null,
    selectedSamplePreset: null,
    currentLanguage: 'en',
    currentCropRecs: null,
    currentWeather: null,
    currentIrrigation: null,
    agenticEvents: [],
    activeAgentFilter: 'all',
    currentLocation: {
      name: 'Surat',
      displayName: 'Surat, Gujarat',
      lat: 21.1981,
      lon: 72.8298,
      source: 'Auto IP Network'
    }
  };

  /* ==========================================================
     0. Live Location Tracking & Multi-Module Sync Controller
     ========================================================== */
  const headerLocationBtn = document.getElementById('headerLocationBtn');
  const headerLocationText = document.getElementById('headerLocationText');
  const headerWeatherVal = document.getElementById('headerWeatherVal');
  const headerMoistureVal = document.getElementById('headerMoistureVal');
  const locationInput = document.getElementById('locationInput');
  const detectGpsBtn = document.getElementById('detectGpsBtn');
  const locationStatusBadge = document.getElementById('locationStatusBadge');
  const weatherHeroLocation = document.getElementById('weatherHeroLocation');
  const phInput = document.getElementById('phInput');
  const phDisplay = document.getElementById('phDisplay');
  const moistureInput = document.getElementById('moistureInput');
  const moistureDisplay = document.getElementById('moistureDisplay');
  const tempInput = document.getElementById('tempInput');
  const tempDisplay = document.getElementById('tempDisplay');
  const rainProbInput = document.getElementById('rainProbInput');
  const rainProbDisplay = document.getElementById('rainProbDisplay');

  // Broadcast location update across all full-stack modules
  async function applyLocationUpdate(locationObj, isUserGesture = false) {
    if (!locationObj) return;
    state.currentLocation = locationObj;
    window.currentFarmLocation = locationObj;

    // 1. Update UI Elements
    if (headerLocationText) {
      headerLocationText.textContent = locationObj.displayName || `${locationObj.lat.toFixed(2)}°N, ${locationObj.lon.toFixed(2)}°E`;
    }
    if (locationInput) {
      locationInput.value = locationObj.displayName;
    }
    if (weatherHeroLocation) {
      weatherHeroLocation.textContent = `Station: ${locationObj.displayName} (${locationObj.lat.toFixed(2)}°N, ${locationObj.lon.toFixed(2)}°E) • Live Telemetry`;
    }
    if (locationStatusBadge) {
      const isGps = locationObj.source && locationObj.source.includes('GPS');
      locationStatusBadge.textContent = isGps ? '● Live GPS Active' : '● Auto Network Active';
      locationStatusBadge.style.color = '#2E7D32';
    }

    if (isUserGesture) {
      showToast(`Location set to ${locationObj.displayName}`, 'success');
    }

    // 2. Fetch and render Live Weather for exact coordinates
    await loadWeatherAdvice(locationObj.displayName, locationObj.lat, locationObj.lon);

    // 3. Sync Disease Form sliders to live ambient values
    if (state.currentWeather && state.currentWeather.current) {
      const curTemp = Math.round(state.currentWeather.current.temp);
      const curRain = state.currentWeather.current.rainProb;
      if (tempInput) {
        tempInput.value = curTemp;
        const tempDisplay = document.getElementById('tempDisplay');
        if (tempDisplay) tempDisplay.textContent = `${curTemp}°C`;
      }
      if (rainProbInput) {
        rainProbInput.value = curRain;
        const rainProbDisplay = document.getElementById('rainProbDisplay');
        if (rainProbDisplay) rainProbDisplay.textContent = `${curRain}%`;
      }
      if (headerWeatherVal) {
        headerWeatherVal.textContent = `${curTemp}°C • Rain ${curRain}%`;
      }
    }

    // 4. Recalculate Smart Irrigation based on local weather & coordinates
    await loadIrrigationAdvice();

    // 5. Update Crop Recommendations context for current location
    if (!state.cropSelectedLocation) {
      await loadCropRecommendations();
    }
  }

  // Trigger high-precision GPS detection
  async function detectGpsLocation() {
    if (locationStatusBadge) {
      locationStatusBadge.textContent = '● Acquiring GPS Satellite Lock...';
      locationStatusBadge.style.color = '#E65100';
    }
    showToast('Acquiring high-precision GPS coordinates...', 'info');

    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const lat = position.coords.latitude;
          const lon = position.coords.longitude;
          try {
            const rev = await window.AgriSmartAPI.reverseGeocodeLocation(lat, lon);
            const locObj = {
              name: rev.city || 'My Farm',
              displayName: rev.display_name || `${lat.toFixed(3)}°N, ${lon.toFixed(3)}°E`,
              lat: lat,
              lon: lon,
              source: 'High-Precision GPS'
            };
            await applyLocationUpdate(locObj, true);
          } catch (e) {
            const locObj = {
              name: 'GPS Station',
              displayName: `${lat.toFixed(3)}°N, ${lon.toFixed(3)}°E`,
              lat: lat,
              lon: lon,
              source: 'High-Precision GPS'
            };
            await applyLocationUpdate(locObj, true);
          }
        },
        async (err) => {
          console.warn('GPS permission denied or unavailable:', err.message);
          showToast('GPS access denied. Falling back to live network IP detection...', 'warning');
          await autoDetectIpLocation(true);
        },
        { enableHighAccuracy: true, timeout: 8000, maximumAge: 60000 }
      );
    } else {
      showToast('Geolocation not supported by browser. Using live IP location.', 'warning');
      await autoDetectIpLocation(true);
    }
  }

  // Auto-detect location via IP
  async function autoDetectIpLocation(notify = false) {
    try {
      const ipLoc = await window.AgriSmartAPI.detectCurrentLocation();
      const locObj = {
        name: ipLoc.city,
        displayName: ipLoc.display_name || `${ipLoc.city}, ${ipLoc.state}`,
        lat: ipLoc.latitude,
        lon: ipLoc.longitude,
        source: ipLoc.source || 'Auto Network IP'
      };
      await applyLocationUpdate(locObj, notify);
    } catch (e) {
      console.warn('Auto IP location failed:', e);
    }
  }

  // Bind location interaction listeners
  if (detectGpsBtn) {
    detectGpsBtn.addEventListener('click', () => {
      detectGpsLocation();
    });
  }

  if (headerLocationBtn) {
    headerLocationBtn.addEventListener('click', () => {
      detectGpsLocation();
    });
  }

  if (locationInput) {
    locationInput.addEventListener('keydown', async (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        const query = locationInput.value.trim();
        if (!query) return;
        showToast(`Locating "${query}"...`, 'info');
        const res = await window.AgriSmartAPI.searchLocation(query);
        if (res) {
          const locObj = {
            name: res.name || query,
            displayName: res.display_name || query,
            lat: res.latitude,
            lon: res.longitude,
            source: 'Manual Search'
          };
          await applyLocationUpdate(locObj, true);
        }
      }
    });
  }

  // Quick preset chips
  document.querySelectorAll('.loc-preset-chip').forEach(chip => {
    chip.addEventListener('click', async () => {
      const locStr = chip.getAttribute('data-loc');
      if (!locStr) return;
      showToast(`Switching location to ${locStr}...`, 'info');
      const res = await window.AgriSmartAPI.searchLocation(locStr);
      if (res) {
        const locObj = {
          name: res.name || locStr,
          displayName: res.display_name || locStr,
          lat: res.latitude,
          lon: res.longitude,
          source: 'Quick Preset'
        };
        await applyLocationUpdate(locObj, true);
      }
    });
  });

  /* ==========================================================
     1. Tab Navigation Controller
     ========================================================== */
  const navButtons = document.querySelectorAll('.nav-btn');
  const mobileNavItems = document.querySelectorAll('.mobile-nav-item');
  const sections = document.querySelectorAll('.app-section');
  const navToggleBtn = document.getElementById('navToggleBtn');
  const navWrapper = document.querySelector('.nav-wrapper');

  function switchSection(targetSectionId) {
    if (!targetSectionId) return;

    // Update section active state
    sections.forEach(sec => {
      const isTarget = sec.id === targetSectionId;
      sec.classList.toggle('active', isTarget);
      sec.setAttribute('aria-hidden', !isTarget);
    });

    // Update desktop nav buttons
    navButtons.forEach(btn => {
      const isTarget = btn.getAttribute('data-section') === targetSectionId;
      btn.classList.toggle('active', isTarget);
      btn.setAttribute('aria-selected', isTarget);
    });

    // Update mobile nav buttons
    mobileNavItems.forEach(btn => {
      const isTarget = btn.getAttribute('data-section') === targetSectionId;
      btn.classList.toggle('active', isTarget);
    });

    state.activeSection = targetSectionId;
    window.location.hash = targetSectionId;
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Lazy load section data on first navigation
    handleSectionActivation(targetSectionId);
  }

  // Desktop navigation click
  navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const sectionId = btn.getAttribute('data-section');
      switchSection(sectionId);
    });
  });

  // Mobile bottom bar click
  mobileNavItems.forEach(btn => {
    btn.addEventListener('click', () => {
      const sectionId = btn.getAttribute('data-section');
      switchSection(sectionId);
    });
  });

  // Header Brand click
  const brandHomeLink = document.getElementById('brandHomeLink');
  if (brandHomeLink) {
    brandHomeLink.addEventListener('click', (e) => {
      e.preventDefault();
      switchSection('section-disease');
    });
  }

  // Mobile toggle button for desktop nav bar
  if (navToggleBtn && navWrapper) {
    navToggleBtn.addEventListener('click', () => {
      const isExpanded = navToggleBtn.getAttribute('aria-expanded') === 'true';
      navToggleBtn.setAttribute('aria-expanded', !isExpanded);
      navWrapper.style.display = isExpanded ? 'none' : 'block';
    });
  }

  // Deep-linking via URL hash
  if (window.location.hash) {
    const hashId = window.location.hash.replace('#', '');
    if (document.getElementById(hashId)) {
      switchSection(hashId);
    }
  }

  /* ==========================================================
     2. Form Telemetry Sliders & Display Binding
     ========================================================== */
  if (phInput && phDisplay) {
    phInput.addEventListener('input', () => {
      phDisplay.textContent = `${phInput.value} pH`;
    });
  }

  if (moistureInput && moistureDisplay) {
    moistureInput.addEventListener('input', () => {
      moistureDisplay.textContent = `${moistureInput.value}%`;
      if (headerMoistureVal) headerMoistureVal.innerHTML = `Moisture: <strong>${moistureInput.value}%</strong>`;
    });
  }

  if (tempInput && tempDisplay) {
    tempInput.addEventListener('input', () => {
      tempDisplay.textContent = `${tempInput.value}°C`;
      updateHeaderWeather();
    });
  }

  if (rainProbInput && rainProbDisplay) {
    rainProbInput.addEventListener('input', () => {
      rainProbDisplay.textContent = `${rainProbInput.value}%`;
      updateHeaderWeather();
    });
  }

  function updateHeaderWeather() {
    if (headerWeatherVal && tempInput && rainProbInput) {
      headerWeatherVal.textContent = `${tempInput.value}°C • Rain ${rainProbInput.value}%`;
    }
  }

  /* ==========================================================
     3. Leaf Image Upload & Dropzone Controller
     ========================================================== */
  const leafDropzone = document.getElementById('leafDropzone');
  const leafFileInput = document.getElementById('leafFileInput');
  const imagePreviewCard = document.getElementById('imagePreviewCard');
  const previewThumbnailWrap = document.getElementById('previewThumbnailWrap');
  const previewFilename = document.getElementById('previewFilename');
  const previewMeta = document.getElementById('previewMeta');
  const previewRemoveBtn = document.getElementById('previewRemoveBtn');
  const samplePresetsContainer = document.getElementById('samplePresetsContainer');

  // Drag and drop events
  ['dragenter', 'dragover'].forEach(eventName => {
    leafDropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      leafDropzone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach(eventName => {
    leafDropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      leafDropzone.classList.remove('dragover');
    });
  });

  leafDropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files && files.length > 0) {
      handleImageFileSelected(files[0]);
    }
  });

  leafFileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleImageFileSelected(e.target.files[0]);
    }
  });

  function handleImageFileSelected(file) {
    if (!file.type.startsWith('image/')) {
      showToast('Please select a valid image file (JPEG, PNG, WebP)', 'warning');
      return;
    }

    state.selectedImageFile = file;
    state.selectedSamplePreset = null;
    clearActiveSampleChips();

    // Generate local preview
    const reader = new FileReader();
    reader.onload = (e) => {
      previewThumbnailWrap.innerHTML = `<img src="${e.target.result}" alt="Uploaded Leaf Preview" class="preview-thumbnail">`;
      previewFilename.textContent = file.name;
      previewMeta.textContent = `${(file.size / 1024).toFixed(1)} KB • Ready for pathology scan`;
      imagePreviewCard.classList.add('visible');
    };
    reader.readAsDataURL(file);
    showToast(`Loaded ${file.name}`, 'info');
  }

  // Remove preview
  if (previewRemoveBtn) {
    previewRemoveBtn.addEventListener('click', () => {
      state.selectedImageFile = null;
      state.selectedSamplePreset = null;
      leafFileInput.value = '';
      imagePreviewCard.classList.remove('visible');
      clearActiveSampleChips();
    });
  }

  // Sample Leaf Presets Controller
  function clearActiveSampleChips() {
    document.querySelectorAll('.sample-chip').forEach(c => c.classList.remove('active'));
  }

  if (samplePresetsContainer) {
    samplePresetsContainer.addEventListener('click', (e) => {
      const chip = e.target.closest('.sample-chip');
      if (!chip) return;

      const presetKey = chip.getAttribute('data-preset');
      const preset = window.AgriSmartMock.SAMPLE_LEAF_PRESETS[presetKey];
      if (!preset) return;

      clearActiveSampleChips();
      chip.classList.add('active');

      state.selectedSamplePreset = presetKey;
      state.selectedImageFile = { name: preset.imageLabel, isPreset: true, presetKey };

      const sampleImgUrl = `assets/samples/${presetKey}.jpg`;
      fetch(sampleImgUrl)
        .then(res => {
          if (!res.ok) throw new Error('Specimen image not found');
          return res.blob();
        })
        .then(blob => {
          state.selectedImageFile = new File([blob], `${presetKey}.jpg`, { type: 'image/jpeg' });
        })
        .catch(err => {
          console.warn('Using specimen placeholder:', err);
        });

      // Auto-fill farm context form from preset
      const cropSelect = document.getElementById('cropTypeSelect');
      const stageSelect = document.getElementById('growthStageSelect');
      const soilSelect = document.getElementById('soilTypeSelect');
      const locInput = document.getElementById('locationInput');

      if (cropSelect) cropSelect.value = preset.crop;
      if (stageSelect) stageSelect.value = preset.stage;
      if (soilSelect) soilSelect.value = preset.soil;
      if (locInput) locInput.value = preset.location;

      if (phInput) {
        phInput.value = preset.ph;
        phDisplay.textContent = `${preset.ph} pH`;
      }
      if (moistureInput) {
        moistureInput.value = preset.moisture;
        moistureDisplay.textContent = `${preset.moisture}%`;
        if (headerMoistureVal) headerMoistureVal.innerHTML = `Moisture: <strong>${preset.moisture}%</strong>`;
      }
      if (tempInput) {
        tempInput.value = preset.temp;
        tempDisplay.textContent = `${preset.temp}°C`;
      }
      if (rainProbInput) {
        rainProbInput.value = preset.rainProb;
        rainProbDisplay.textContent = `${preset.rainProb}%`;
      }
      updateHeaderWeather();

      // Show sample preview photo with SVG fallback
      previewThumbnailWrap.innerHTML = `<img src="${sampleImgUrl}" alt="${preset.name}" class="preview-thumbnail" style="width:100%;height:100%;object-fit:cover;border-radius:8px;">`;
      previewFilename.textContent = `${preset.name} (Live Specimen)`;
      previewMeta.textContent = `${preset.crop} • Auto-calibrated test photo • Ready for ML scan`;
      imagePreviewCard.classList.add('visible');

      showToast(`Selected ${preset.name} test sample`, 'success');
    });
  }

  function generateSampleLeafSVG(svgType, isDiseased) {
    const strokeColor = isDiseased ? '#E65100' : '#2E7D32';
    const fillColor = isDiseased ? '#FFF3E0' : '#E8F5E9';
    return `
      <svg viewBox="0 0 100 100" width="70" height="70" aria-hidden="true">
        <path d="M50 10 C25 25 15 55 50 90 C85 55 75 25 50 10 Z" fill="${fillColor}" stroke="${strokeColor}" stroke-width="3"/>
        <line x1="50" y1="15" x2="50" y2="85" stroke="${strokeColor}" stroke-width="2.5"/>
        <line x1="50" y1="35" x2="35" y2="45" stroke="${strokeColor}" stroke-width="1.8"/>
        <line x1="50" y1="48" x2="65" y2="58" stroke="${strokeColor}" stroke-width="1.8"/>
        <line x1="50" y1="62" x2="38" y2="70" stroke="${strokeColor}" stroke-width="1.8"/>
        ${isDiseased ? `
          <circle cx="40" cy="38" r="6" fill="#D32F2F" opacity="0.85"/>
          <circle cx="58" cy="52" r="8" fill="#D32F2F" opacity="0.85"/>
          <circle cx="44" cy="65" r="5" fill="#E65100" opacity="0.85"/>
        ` : `
          <circle cx="50" cy="50" r="4" fill="#66BB6A" opacity="0.6"/>
        `}
      </svg>
    `;
  }

  /* ==========================================================
     4. Disease Detection Analysis Handler
     ========================================================== */
  const farmContextForm = document.getElementById('farmContextForm');
  const diseaseLoadingOverlay = document.getElementById('diseaseLoadingOverlay');
  const analyzeBtn = document.getElementById('analyzeBtn');

  if (farmContextForm) {
    farmContextForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      await runDiseaseAnalysis();
    });
  }

  if (analyzeBtn) {
    analyzeBtn.addEventListener('click', async (e) => {
      e.preventDefault();
      await runDiseaseAnalysis();
    });
  }

  async function runDiseaseAnalysis() {
    const cropType = document.getElementById('cropTypeSelect')?.value || 'Tomato';
    const growthStage = document.getElementById('growthStageSelect')?.value || 'Fruiting';
    const soilType = document.getElementById('soilTypeSelect')?.value || 'Loamy';
    const ph = parseFloat(phInput?.value) || 6.4;
    const soilMoisture = parseInt(moistureInput?.value) || 68;
    const temperature = parseInt(tempInput?.value) || 27;
    const rainProb = parseInt(rainProbInput?.value) || 65;
    const location = document.getElementById('locationInput')?.value || 'Nashik Valley, MH';

    const isHealthyPreset = state.selectedSamplePreset === 'corn_healthy';

    const farmContext = {
      cropType,
      growthStage,
      soilType,
      ph,
      soilMoisture,
      temperature,
      rainProb,
      location,
      isHealthyPreset
    };

    // Show loading spinner
    if (diseaseLoadingOverlay) diseaseLoadingOverlay.classList.add('active');
    if (analyzeBtn) analyzeBtn.disabled = true;

    try {
      const result = await window.AgriSmartAPI.predictDisease(
        state.selectedImageFile || { name: 'sample_leaf.jpg' },
        farmContext
      );
      renderDiseaseResult(result);
      showToast(`Analysis complete: ${result.disease}`, result.status === 'healthy' ? 'success' : 'warning');
    } catch (err) {
      console.error('Disease prediction error:', err);
      showToast('Error during disease diagnosis: ' + err.message, 'warning');
    } finally {
      if (diseaseLoadingOverlay) diseaseLoadingOverlay.classList.remove('active');
      if (analyzeBtn) analyzeBtn.disabled = false;
    }
  }

  function renderDiseaseResult(result) {
    const statusBadge = document.getElementById('resStatusBadge');
    const statusText = document.getElementById('resStatusText');
    const diseaseName = document.getElementById('resDiseaseName');
    const scientificName = document.getElementById('resScientificName');
    const severityTag = document.getElementById('resSeverityTag');
    const confidenceVal = document.getElementById('resConfidenceVal');
    const confidenceBar = document.getElementById('resConfidenceBar');
    const summaryText = document.getElementById('resSummaryText');
    const symptomsList = document.getElementById('resSymptomsList');
    const organicAdvice = document.getElementById('resOrganicAdvice');
    const culturalAdvice = document.getElementById('resCulturalAdvice');
    const chemicalAdvice = document.getElementById('resChemicalAdvice');

    if (diseaseName) diseaseName.textContent = result.disease;
    if (scientificName) scientificName.textContent = `${result.scientificName} • Diagnostic Confidence Matrix`;
    if (summaryText) summaryText.textContent = result.summary;

    if (confidenceVal) confidenceVal.textContent = `${result.confidence}%`;
    if (confidenceBar) {
      confidenceBar.style.width = '0%';
      setTimeout(() => {
        confidenceBar.style.width = `${result.confidence}%`;
      }, 50);
    }

    if (statusBadge && statusText) {
      if (result.status === 'healthy') {
        statusBadge.className = 'result-status-badge healthy';
        statusText.textContent = 'Healthy Foliage';
        if (severityTag) {
          severityTag.textContent = 'Optimal Plant Health';
          severityTag.style.background = 'var(--color-success-bg)';
          severityTag.style.color = 'var(--color-success)';
        }
      } else {
        statusBadge.className = 'result-status-badge diseased';
        statusText.textContent = 'Pathogen Detected';
        if (severityTag) {
          severityTag.textContent = result.severity;
          severityTag.style.background = 'var(--color-warning-bg)';
          severityTag.style.color = 'var(--color-warning)';
        }
      }
    }

    if (symptomsList && result.symptoms) {
      symptomsList.innerHTML = result.symptoms.map(sym => `
        <li>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
          <span>${sym}</span>
        </li>
      `).join('');
    }

    if (result.precautions) {
      if (organicAdvice) organicAdvice.innerHTML = `<strong>Organic / Biological:</strong> ${result.precautions.organic || 'Maintain balanced nutrition.'}`;
      if (culturalAdvice) culturalAdvice.innerHTML = `<strong>Cultural Practice:</strong> ${result.precautions.cultural || 'Ensure aeration and sanitation.'}`;
      if (chemicalAdvice) {
        if (result.precautions.chemical) {
          chemicalAdvice.parentElement.style.display = 'flex';
          chemicalAdvice.innerHTML = `<strong>Chemical Option (If severe):</strong> ${result.precautions.chemical}`;
        } else {
          chemicalAdvice.parentElement.style.display = 'none';
        }
      }
    }

    // Render Real Model Differentials & Model Badge
    const top3Container = document.getElementById('resTop3Container');
    const top3List = document.getElementById('resTop3List');
    const modelBadge = document.getElementById('resModelBadge');

    if (top3Container && top3List) {
      if (result.top_3 && result.top_3.length > 0) {
        top3Container.style.display = 'block';
        if (modelBadge) {
          modelBadge.textContent = (result.model_mode === 'real')
            ? '⚡ Real PyTorch Model (38 Classes)'
            : '🧪 Simulated Mode';
        }
        top3List.innerHTML = result.top_3.map((item, idx) => `
          <span style="background: rgba(46,125,50,0.07); border: 1px solid var(--color-border); padding: 4px 10px; border-radius: 6px; font-size: 0.78rem; display: inline-flex; align-items: center; gap: 4px;">
            <strong style="color: var(--color-primary);">${idx + 1}.</strong> ${item.display_name}: <strong>${item.confidence}%</strong>
          </span>
        `).join('');
      } else {
        top3Container.style.display = 'none';
      }
    }
  }

  // Cross-navigation buttons from Disease Results
  const askAssistantAboutDiseaseBtn = document.getElementById('askAssistantAboutDiseaseBtn');
  if (askAssistantAboutDiseaseBtn) {
    askAssistantAboutDiseaseBtn.addEventListener('click', () => {
      const disease = document.getElementById('resDiseaseName')?.textContent || 'Early Blight';
      switchSection('section-assistant');
      const chatInput = document.getElementById('chatInputField');
      if (chatInput) {
        chatInput.value = `How should I manage ${disease} organically on my farm?`;
        document.getElementById('chatInputForm')?.dispatchEvent(new Event('submit'));
      }
    });
  }

  const checkIrrigationFromDiseaseBtn = document.getElementById('checkIrrigationFromDiseaseBtn');
  if (checkIrrigationFromDiseaseBtn) {
    checkIrrigationFromDiseaseBtn.addEventListener('click', () => {
      switchSection('section-irrigation');
    });
  }

  /* ==========================================================
     5. Crop Recommendation Controller (Location & Climate Aware)
     ========================================================= */
  const refreshCropRecsBtn = document.getElementById('refreshCropRecsBtn');
  const cropRecommendationsList = document.getElementById('cropRecommendationsList');
  const cropRecSoilSummary = document.getElementById('cropRecSoilSummary');
  const cropActiveLocationName = document.getElementById('cropActiveLocationName');
  const cropLocationModeBadge = document.getElementById('cropLocationModeBadge');
  const cropUseLiveLocationBtn = document.getElementById('cropUseLiveLocationBtn');
  const cropRegionPresetSelect = document.getElementById('cropRegionPresetSelect');
  const cropCustomLocationInput = document.getElementById('cropCustomLocationInput');
  const cropApplyCustomLocBtn = document.getElementById('cropApplyCustomLocBtn');
  const cropRecZoneName = document.getElementById('cropRecZoneName');

  async function loadCropRecommendations() {
    if (!cropRecommendationsList) return;

    // Determine whether user is using a custom selected location or the live/current location
    const isCustomSelected = Boolean(state.cropSelectedLocation);
    const activeLoc = state.cropSelectedLocation || state.currentLocation;
    const locName = activeLoc?.displayName || activeLoc?.name || document.getElementById('locationInput')?.value || 'Surat, Gujarat';
    const locLat = activeLoc?.lat;
    const locLon = activeLoc?.lon;

    // Update the UI header in the Crop Recommendation card
    if (cropActiveLocationName) {
      cropActiveLocationName.textContent = locName;
    }
    if (cropLocationModeBadge) {
      if (isCustomSelected) {
        cropLocationModeBadge.textContent = '📍 Custom Selected Location';
        cropLocationModeBadge.style.background = '#E3F2FD';
        cropLocationModeBadge.style.color = '#1565C0';
        cropLocationModeBadge.style.border = '1px solid #90CAF9';
      } else {
        const isGps = activeLoc?.source && activeLoc.source.includes('GPS');
        cropLocationModeBadge.textContent = isGps ? '● Live GPS Detected' : '● Live Auto-Detected';
        cropLocationModeBadge.style.background = '#E8F5E9';
        cropLocationModeBadge.style.color = '#2E7D32';
        cropLocationModeBadge.style.border = '1px solid #A5D6A7';
      }
    }

    const soilData = {
      ph: phInput?.value || 6.4,
      moisture: moistureInput?.value || 68,
      temperature: tempInput?.value || 27,
      rainProb: rainProbInput?.value || 65,
      soilType: document.getElementById('soilTypeSelect')?.value || 'Loamy',
      location: locName,
      lat: locLat,
      lon: locLon
    };

    if (cropRecSoilSummary) {
      cropRecSoilSummary.textContent = `${soilData.soilType} Soil • pH ${soilData.ph} • Moisture ${soilData.moisture}% • ${soilData.temperature}°C`;
    }

    try {
      const data = await window.AgriSmartAPI.recommendCrop(soilData);
      state.currentCropRecs = data;

      if (cropRecZoneName && data.zone_name) {
        cropRecZoneName.textContent = data.zone_name;
      }

      renderCropRecommendations(data.recommendations, data);
    } catch (err) {
      console.error('Crop recommendation error:', err);
    }
  }

  function renderCropRecommendations(crops, meta = {}) {
    if (!cropRecommendationsList || !crops) return;

    cropRecommendationsList.innerHTML = crops.map(crop => {
      const isStar = crop.isRegionalStar || crop.regionalBadge?.includes('Flagship') || crop.regionalBadge?.includes('Star');
      const badgeHtml = crop.regionalBadge ? `
        <span class="crop-regional-pill" title="Tailored to local agro-climatic zone">
          ${crop.regionalBadge}
        </span>
      ` : '';

      return `
      <article class="crop-rank-card ${isStar ? 'crop-card-regional-star' : ''}" aria-label="${crop.name} Rank ${crop.rank}">
        <div class="crop-card-top">
          <div style="display: flex; align-items: center; gap: 0.75rem;">
            <div class="crop-rank-badge ${isStar ? 'star-badge' : ''}">#${crop.rank}</div>
            <div class="crop-name-wrap">
              <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                <h3>${crop.name}</h3>
                ${badgeHtml}
              </div>
              <p style="font-size: 0.85rem; font-style: italic; color: var(--color-text-light);">${crop.botanicalName}</p>
            </div>
          </div>
          <div class="crop-match-pill">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="14" height="14" aria-hidden="true">
              <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
            </svg>
            <span>${crop.matchScore}% Suitability</span>
          </div>
        </div>

        <div class="crop-metrics-strip">
          <div class="crop-metric-item">
            <span class="crop-metric-label">Water Need</span>
            <span class="crop-metric-val">${crop.waterRequirement}</span>
          </div>
          <div class="crop-metric-item">
            <span class="crop-metric-label">Cycle Time</span>
            <span class="crop-metric-val">${crop.harvestDuration}</span>
          </div>
          <div class="crop-metric-item">
            <span class="crop-metric-label">Est. Yield</span>
            <span class="crop-metric-val">${crop.expectedYield}</span>
          </div>
          <div class="crop-metric-item">
            <span class="crop-metric-label">Market Value</span>
            <span class="crop-metric-val" style="color: var(--color-primary);">${crop.profitPotential}</span>
          </div>
        </div>

        <p class="crop-rationale">${crop.rationale}</p>
        <div style="font-size: 0.85rem; font-weight: 700; color: var(--color-primary);">
          Key Advantage: <span style="font-weight: normal; color: var(--color-text-main);">${crop.keyAdvantage}</span>
        </div>
      </article>
      `;
    }).join('');
  }

  // Bind Crop Location Controls
  if (cropUseLiveLocationBtn) {
    cropUseLiveLocationBtn.addEventListener('click', async () => {
      state.cropSelectedLocation = null;
      if (cropRegionPresetSelect) cropRegionPresetSelect.value = 'CURRENT';
      if (cropCustomLocationInput) cropCustomLocationInput.value = '';
      showToast('Acquiring live GPS / network location for crop matching...', 'info');
      await detectGpsLocation();
      await loadCropRecommendations();
    });
  }

  if (cropRegionPresetSelect) {
    cropRegionPresetSelect.addEventListener('change', async () => {
      const selectedVal = cropRegionPresetSelect.value;
      if (selectedVal === 'CURRENT') {
        state.cropSelectedLocation = null;
        showToast('Switched crop engine to current live location', 'info');
        await loadCropRecommendations();
        return;
      }
      showToast(`Evaluating crops for ${selectedVal}...`, 'info');
      try {
        const geocoded = await window.AgriSmartAPI.searchLocation(selectedVal);
        if (geocoded) {
          state.cropSelectedLocation = {
            name: geocoded.name || selectedVal,
            displayName: geocoded.display_name || selectedVal,
            lat: geocoded.latitude,
            lon: geocoded.longitude,
            source: 'Preset Region'
          };
        } else {
          state.cropSelectedLocation = {
            name: selectedVal,
            displayName: selectedVal,
            source: 'Preset Region'
          };
        }
      } catch (err) {
        state.cropSelectedLocation = {
          name: selectedVal,
          displayName: selectedVal,
          source: 'Preset Region'
        };
      }
      await loadCropRecommendations();
      showToast(`Crops matched for ${selectedVal}`, 'success');
    });
  }

  async function applyCustomCropLocation() {
    if (!cropCustomLocationInput) return;
    const query = cropCustomLocationInput.value.trim();
    if (!query) return;

    showToast(`Locating agricultural zone for "${query}"...`, 'info');
    try {
      const geocoded = await window.AgriSmartAPI.searchLocation(query);
      if (geocoded) {
        state.cropSelectedLocation = {
          name: geocoded.name || query,
          displayName: geocoded.display_name || query,
          lat: geocoded.latitude,
          lon: geocoded.longitude,
          source: 'Custom Selected'
        };
      } else {
        state.cropSelectedLocation = {
          name: query,
          displayName: query,
          source: 'Custom Selected'
        };
      }
    } catch (err) {
      state.cropSelectedLocation = {
        name: query,
        displayName: query,
        source: 'Custom Selected'
      };
    }
    if (cropRegionPresetSelect) cropRegionPresetSelect.value = '';
    await loadCropRecommendations();
    showToast(`Crop recommendations customized for "${query}"`, 'success');
  }

  if (cropApplyCustomLocBtn) {
    cropApplyCustomLocBtn.addEventListener('click', applyCustomCropLocation);
  }
  if (cropCustomLocationInput) {
    cropCustomLocationInput.addEventListener('keydown', async (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        await applyCustomCropLocation();
      }
    });
  }

  if (refreshCropRecsBtn) {
    refreshCropRecsBtn.addEventListener('click', async () => {
      showToast('Recomputing crop suitability matrices...', 'info');
      await loadCropRecommendations();
      showToast('Crop recommendations updated', 'success');
    });
  }

  /* ==========================================================
     6. Smart Irrigation Controller
     ========================================================== */
  const irrigationDecisionHero = document.getElementById('irrigationDecisionHero');
  const irrigationDecisionTitle = document.getElementById('irrigationDecisionTitle');
  const irrigationReasoningText = document.getElementById('irrigationReasoningText');
  const irrStatMoisture = document.getElementById('irrStatMoisture');
  const irrStatRain = document.getElementById('irrStatRain');
  const irrNextWindow = document.getElementById('irrNextWindow');
  const toggleManualIrrigationBtn = document.getElementById('toggleManualIrrigationBtn');

  async function loadIrrigationAdvice() {
    const data = {
      moisture: moistureInput?.value || 68,
      rainProb: rainProbInput?.value || (state.currentWeather?.current?.rainProb ?? 35),
      temp: tempInput?.value || (state.currentWeather?.current?.temp ?? 28),
      crop: document.getElementById('cropTypeSelect')?.value || 'Tomato',
      lat: state.currentLocation?.lat,
      lon: state.currentLocation?.lon,
      location: state.currentLocation?.displayName
    };

    try {
      const advice = await window.AgriSmartAPI.getIrrigationAdvice(data);
      state.currentIrrigation = advice;
      renderIrrigationAdvice(advice);
    } catch (err) {
      console.error('Irrigation advice error:', err);
    }
  }

  function renderIrrigationAdvice(advice) {
    if (!irrigationDecisionHero) return;

    if (advice.needed) {
      irrigationDecisionHero.className = 'irrigation-decision-hero needed';
      if (irrigationDecisionTitle) irrigationDecisionTitle.textContent = advice.decision;
    } else {
      irrigationDecisionHero.className = 'irrigation-decision-hero delay';
      if (irrigationDecisionTitle) irrigationDecisionTitle.textContent = advice.decision;
    }

    if (irrigationReasoningText) irrigationReasoningText.innerHTML = advice.reasoning;
    if (irrStatMoisture) irrStatMoisture.textContent = `${advice.metrics.soilMoisture}%`;
    if (irrStatRain) irrStatRain.textContent = advice.metrics.rainForecast24h;
    if (irrNextWindow && advice.schedule) irrNextWindow.textContent = advice.schedule.optimalWindow;
  }

  if (toggleManualIrrigationBtn) {
    toggleManualIrrigationBtn.addEventListener('click', () => {
      toggleManualIrrigationBtn.disabled = true;
      toggleManualIrrigationBtn.innerHTML = `
        <div class="spinner" style="width: 18px; height: 18px; border-width: 2px; display: inline-block;"></div>
        <span>Pumping 15-Minute Sensor Flush...</span>
      `;

      setTimeout(() => {
        showToast('Valve #1 & #3 line flushed with 450 Liters test water', 'success');
        toggleManualIrrigationBtn.disabled = false;
        toggleManualIrrigationBtn.innerHTML = `
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18" aria-hidden="true">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
          <span>Override & Trigger 15-Min Test Flush</span>
        `;
      }, 1500);
    });
  }

  /* ==========================================================
     7. Weather-Based Intelligence Controller
     ========================================================== */
  const weatherHeroTemp = document.getElementById('weatherHeroTemp');
  const weatherHeroDesc = document.getElementById('weatherHeroDesc');
  const weatherHeroHumidity = document.getElementById('weatherHeroHumidity');
  const weatherHeroRain = document.getElementById('weatherHeroRain');
  const weatherHeroWind = document.getElementById('weatherHeroWind');
  const weatherActionBannersContainer = document.getElementById('weatherActionBannersContainer');
  const weatherForecastContainer = document.getElementById('weatherForecastContainer');

  async function loadWeatherAdvice(locationName = null, lat = null, lon = null) {
    const loc = locationName || state.currentLocation?.displayName || 'Surat, Gujarat';
    const latitude = lat !== null && lat !== undefined ? lat : state.currentLocation?.lat;
    const longitude = lon !== null && lon !== undefined ? lon : state.currentLocation?.lon;

    try {
      const data = await window.AgriSmartAPI.getWeatherAdvice(loc, latitude, longitude);
      state.currentWeather = data;
      window.currentWeatherSummary = `${data.current.temp}°C, ${data.current.condition}, ${data.current.rainProb}% rain in ${data.location}`;
      renderWeather(data);
    } catch (err) {
      console.error('Weather advice error:', err);
    }
  }

  function renderWeather(data) {
    if (weatherHeroTemp) weatherHeroTemp.textContent = `${data.current.temp}°C`;
    if (weatherHeroDesc) weatherHeroDesc.textContent = data.current.condition;
    if (weatherHeroHumidity) weatherHeroHumidity.textContent = `${data.current.humidity}%`;
    if (weatherHeroRain) weatherHeroRain.textContent = `${data.current.rainProb}%`;
    if (weatherHeroWind) weatherHeroWind.textContent = `${data.current.windSpeed} km/h`;

    if (weatherHeroLocation) {
      const coordsStr = data.latitude ? ` (${data.latitude.toFixed(2)}°N, ${data.longitude.toFixed(2)}°E)` : '';
      weatherHeroLocation.textContent = `Station: ${data.location}${coordsStr} • Live Telemetry`;
    }
    if (headerLocationText) {
      headerLocationText.textContent = data.location;
    }
    if (headerWeatherVal) {
      headerWeatherVal.textContent = `${data.current.temp}°C • Rain ${data.current.rainProb}%`;
    }

    // Action Banners
    if (weatherActionBannersContainer && data.actionBanners) {
      weatherActionBannersContainer.innerHTML = data.actionBanners.map(banner => `
        <div class="weather-banner ${banner.level}">
          <div class="weather-banner-icon" aria-hidden="true">
            ${getWeatherIconSVG(banner.icon)}
          </div>
          <div class="weather-banner-content">
            <h4>${banner.title}</h4>
            <p>${banner.description}</p>
          </div>
        </div>
      `).join('');
    }

    // 5-Day Forecast
    if (weatherForecastContainer && data.forecast) {
      weatherForecastContainer.innerHTML = data.forecast.map(item => `
        <div class="forecast-card">
          <div class="forecast-day">${item.day}</div>
          <div class="forecast-date">${item.date}</div>
          <div class="forecast-icon" aria-hidden="true">
            ${getWeatherIconSVG(item.icon)}
          </div>
          <div class="forecast-temps">
            <span>${item.tempHigh}°</span>
            <span class="low">${item.tempLow}°</span>
          </div>
          <div style="font-size: 0.8rem; font-weight: 700; color: #0288D1;">💧 ${item.rainProb}% Rain</div>
          <p class="forecast-advisory">${item.advisory}</p>
        </div>
      `).join('');
    }
  }

  function getWeatherIconSVG(iconName) {
    switch (iconName) {
      case 'rain':
      case 'cloud-rain':
        return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="24" height="24"><path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/><path d="M8 19v2M12 19v2M16 19v2"/></svg>`;
      case 'cloud-sun':
        return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="24" height="24"><path d="M12 2v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="M20 12h2"/><path d="m19.07 4.93-1.41 1.41"/><path d="M15.947 12.65a4 4 0 0 0-5.925-4.128"/><path d="M13 22H7a5 5 0 1 1 4.9-6H13a3 3 0 0 1 0 6Z"/></svg>`;
      case 'sun':
        return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="24" height="24"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>`;
      case 'shield-alert':
        return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="24" height="24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`;
      default:
        return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="24" height="24"><path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/></svg>`;
    }
  }

  /* ==========================================================
     8. Sustainability Score Controller
     ========================================================== */
  const sustainabilityGaugeCircle = document.getElementById('sustainabilityGaugeCircle');
  const sustainabilityScoreNum = document.getElementById('sustainabilityScoreNum');
  const sustainabilityPillarsContainer = document.getElementById('sustainabilityPillarsContainer');
  const sustainabilitySuggestionsContainer = document.getElementById('sustainabilitySuggestionsContainer');

  async function loadSustainability() {
    try {
      const data = await window.AgriSmartAPI.getSustainabilityScore();
      renderSustainability(data);
    } catch (err) {
      console.error('Sustainability score error:', err);
    }
  }

  function renderSustainability(data) {
    if (sustainabilityScoreNum) sustainabilityScoreNum.textContent = data.overallScore;

    // Animate circular gauge
    if (sustainabilityGaugeCircle) {
      const circumference = 314.159;
      const offset = circumference * (1 - (data.overallScore / 100));
      sustainabilityGaugeCircle.style.strokeDashoffset = offset;
    }

    // Render pillars
    if (sustainabilityPillarsContainer && data.breakdown) {
      sustainabilityPillarsContainer.innerHTML = data.breakdown.map(pillar => `
        <div class="sustainability-pillar-card">
          <div class="pillar-header">
            <span class="pillar-title">${pillar.pillar}</span>
            <span class="pillar-score">${pillar.score}/100</span>
          </div>
          <div class="confidence-track" style="height: 8px;">
            <div class="confidence-fill" style="width: ${pillar.score}%; background: ${pillar.color};"></div>
          </div>
          <p style="font-size: 0.85rem; color: var(--color-text-muted);">${pillar.summary}</p>
          <div style="font-size: 0.78rem; font-weight: 700; color: var(--color-primary);">${pillar.metric}</div>
        </div>
      `).join('');
    }

    // Render suggestions
    if (sustainabilitySuggestionsContainer && data.suggestions) {
      sustainabilitySuggestionsContainer.innerHTML = data.suggestions.map(sug => `
        <div class="suggestion-card">
          <div class="suggestion-badge">${sug.impact}</div>
          <div style="flex: 1;">
            <h4 style="font-size: 0.98rem; margin-bottom: 0.25rem;">${sug.title}</h4>
            <p style="font-size: 0.88rem;">${sug.description}</p>
          </div>
        </div>
      `).join('');
    }
  }

  /* ==========================================================
     9. Farmer Assistant Chat Controller
     ========================================================== */
  const chatInputForm = document.getElementById('chatInputForm');
  const chatInputField = document.getElementById('chatInputField');
  const chatMessagesStream = document.getElementById('chatMessagesStream');
  const assistantLanguageSelect = document.getElementById('assistantLanguageSelect');

  if (assistantLanguageSelect) {
    assistantLanguageSelect.addEventListener('change', (e) => {
      state.currentLanguage = e.target.value;
      const langNames = { en: 'English', hi: 'Hindi', mr: 'Marathi', te: 'Telugu', es: 'Spanish' };
      showToast(`Assistant switched to ${langNames[e.target.value] || 'English'}`, 'info');
    });
  }

  if (chatInputForm) {
    chatInputForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const question = chatInputField.value.trim();
      if (!question) return;

      // Append user bubble
      appendChatMessage(question, 'user');
      chatInputField.value = '';

      // Show typing indicator
      const typingId = showTypingIndicator();

      try {
        const assistantContext = {
          location: state.currentLocation?.displayName || 'Surat, Gujarat',
          weatherSummary: state.currentWeather ? `${state.currentWeather.current.temp}°C, ${state.currentWeather.current.condition}, ${state.currentWeather.current.rainProb}% rain` : undefined,
          crop: document.getElementById('cropTypeSelect')?.value || 'Tomato',
          diseaseDetected: state.lastAnalysisResult?.disease || undefined,
          irrigationAdvice: state.currentIrrigation?.decision || undefined
        };
        const response = await window.AgriSmartAPI.askAssistant(question, state.currentLanguage, assistantContext);
        removeTypingIndicator(typingId);
        appendChatMessage(response.text, 'bot', response.timestamp);
      } catch (err) {
        removeTypingIndicator(typingId);
        appendChatMessage('I encountered an issue connecting to the agricultural knowledge base. Please try again.', 'bot');
      }
    });
  }

  // Suggestion prompt chips
  document.querySelectorAll('.chat-prompt-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const prompt = chip.getAttribute('data-prompt');
      if (chatInputField) {
        chatInputField.value = prompt;
        chatInputForm.dispatchEvent(new Event('submit'));
      }
    });
  });

  function appendChatMessage(text, sender, time = 'Just now') {
    if (!chatMessagesStream) return;

    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${sender}`;

    // Format newlines and markdown-like bold
    const formattedText = text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br>');

    bubble.innerHTML = `
      <div>${formattedText}</div>
      <div class="chat-time">${time}</div>
    `;

    chatMessagesStream.appendChild(bubble);
    chatMessagesStream.scrollTop = chatMessagesStream.scrollHeight;
  }

  function showTypingIndicator() {
    const id = 'typing-' + Date.now();
    const bubble = document.createElement('div');
    bubble.id = id;
    bubble.className = 'chat-bubble bot';
    bubble.innerHTML = `
      <div class="typing-bubble">
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
      </div>
    `;
    chatMessagesStream.appendChild(bubble);
    chatMessagesStream.scrollTop = chatMessagesStream.scrollHeight;
    return id;
  }

  function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  /* ==========================================================
     10. Agentic Advisor Feed Controller
     ========================================================== */
  const agenticTimelineContainer = document.getElementById('agenticTimelineContainer');
  const triggerAgentCycleBtn = document.getElementById('triggerAgentCycleBtn');
  const agenticFilterChips = document.getElementById('agenticFilterChips');
  const feedCountLabel = document.getElementById('feedCountLabel');
  const agenticUnreadBadge = document.getElementById('agenticUnreadBadge');

  async function loadAgenticFeed() {
    try {
      const events = await window.AgriSmartAPI.getAgenticFeed();
      state.agenticEvents = events;
      renderAgenticTimeline();
    } catch (err) {
      console.error('Agentic feed error:', err);
    }
  }

  function renderAgenticTimeline() {
    if (!agenticTimelineContainer) return;

    const filtered = state.agenticEvents.filter(item => {
      if (state.activeAgentFilter === 'all') return true;
      return item.type === state.activeAgentFilter;
    });

    if (feedCountLabel) {
      feedCountLabel.textContent = `Showing ${filtered.length} recorded events`;
    }

    if (agenticUnreadBadge) {
      agenticUnreadBadge.textContent = state.agenticEvents.length;
    }

    if (filtered.length === 0) {
      agenticTimelineContainer.innerHTML = `
        <div class="card" style="text-align: center; padding: 2rem;">
          <p>No agentic events matching the "${state.activeAgentFilter}" filter.</p>
        </div>
      `;
      return;
    }

    agenticTimelineContainer.innerHTML = filtered.map(evt => `
      <article class="timeline-item ${evt.time === 'Just now' ? 'highlight-new' : ''}" aria-label="Event: ${evt.title}">
        <div class="timeline-top-row">
          <span class="timeline-badge ${evt.badgeClass}">${evt.badge}</span>
          <span class="timeline-time">${evt.time}</span>
        </div>
        <h4 class="timeline-title">${evt.title}</h4>
        <div class="timeline-detail-grid">
          <div class="timeline-detail-row">
            <strong>Observation Trigger:</strong> ${evt.trigger}
          </div>
          <div class="timeline-detail-row">
            <strong>Autonomous Reasoning:</strong> ${evt.reasoning}
          </div>
          <div class="timeline-detail-row">
            <strong>Action Dispatched:</strong> ${evt.actionTaken}
          </div>
        </div>
      </article>
    `).join('');
  }

  // Filter buttons click
  if (agenticFilterChips) {
    agenticFilterChips.addEventListener('click', (e) => {
      const btn = e.target.closest('.feed-filter-btn');
      if (!btn) return;

      document.querySelectorAll('.feed-filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      state.activeAgentFilter = btn.getAttribute('data-filter') || 'all';
      renderAgenticTimeline();
    });
  }

  // Trigger on-demand agent cycle
  if (triggerAgentCycleBtn) {
    triggerAgentCycleBtn.addEventListener('click', async () => {
      triggerAgentCycleBtn.disabled = true;
      triggerAgentCycleBtn.innerHTML = `
        <div class="spinner" style="width: 16px; height: 16px; border-width: 2px; display: inline-block;"></div>
        <span>Evaluating Telemetry Telemetry...</span>
      `;

      try {
        const newEvent = await window.AgriSmartAPI.triggerAgentCheck();
        state.agenticEvents.unshift(newEvent);
        renderAgenticTimeline();
        showToast(`Autonomous Agent: ${newEvent.title}`, 'success');
      } catch (err) {
        showToast('Agent evaluation failed: ' + err.message, 'warning');
      } finally {
        triggerAgentCycleBtn.disabled = false;
        triggerAgentCycleBtn.innerHTML = `
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" width="18" height="18" aria-hidden="true">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
          </svg>
          <span>Trigger Agent Check Now</span>
        `;
      }
    });
  }

  /* ==========================================================
     11. Toast Notification Utility
     ========================================================== */
  const toastContainer = document.getElementById('toastContainer');

  function showToast(message, type = 'info', duration = 3200) {
    if (!toastContainer) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="18" height="18" aria-hidden="true">
        ${type === 'success' 
          ? '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>' 
          : '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>'}
      </svg>
      <span>${message}</span>
    `;

    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 200ms ease';
      setTimeout(() => toast.remove(), 250);
    }, duration);
  }

  /* ==========================================================
     12. Section Activation Lifecycle
     ========================================================== */
  function handleSectionActivation(sectionId) {
    switch (sectionId) {
      case 'section-crop':
        if (!state.currentCropRecs) loadCropRecommendations();
        break;
      case 'section-irrigation':
        if (!state.currentIrrigation) loadIrrigationAdvice();
        break;
      case 'section-weather':
        if (!state.currentWeather) loadWeatherAdvice();
        break;
      case 'section-sustainability':
        loadSustainability();
        break;
      case 'section-agentic':
        if (state.agenticEvents.length === 0) loadAgenticFeed();
        break;
      default:
        break;
    }
  }

  // Initialize Location tracking and primary views on boot
  autoDetectIpLocation();
  if ('geolocation' in navigator) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        window.AgriSmartAPI.reverseGeocodeLocation(pos.coords.latitude, pos.coords.longitude).then(rev => {
          applyLocationUpdate({
            name: rev.city || 'My Farm',
            displayName: rev.display_name || `${pos.coords.latitude.toFixed(3)}°N, ${pos.coords.longitude.toFixed(3)}°E`,
            lat: pos.coords.latitude,
            lon: pos.coords.longitude,
            source: 'High-Precision GPS'
          });
        });
      },
      (err) => console.log('Background GPS passive check:', err.message),
      { enableHighAccuracy: false, timeout: 5000, maximumAge: 300000 }
    );
  }

  loadCropRecommendations();
  loadIrrigationAdvice();
  loadSustainability();
  loadAgenticFeed();

  // Set default sample leaf on first boot for immediate delight
  const defaultSampleBtn = document.querySelector('.sample-chip[data-preset="tomato_blight"]');
  if (defaultSampleBtn) {
    defaultSampleBtn.click();
  }

});
