const API_BASE = window.location.origin;

// UI Selectors
const liveVideo = document.getElementById("live-video");
const startCamBtn = document.getElementById("start-camera-btn");
const stopCamBtn = document.getElementById("stop-camera-btn");
const captureBtn = document.getElementById("capture-frame-btn");
const resultImg = document.getElementById("result-image");
const placeholder = document.getElementById("placeholder-text");
const loader = document.getElementById("ai-loader");

let cameraStream = null;

// Initializing Map - Starts at Bengaluru but updates to your real GPS
const map = L.map('field-map').setView([12.9716, 77.5946], 13);
//L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
// Replace the old tileLayer with this high-quality Google Satellite view
L.tileLayer('https://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}', {
    maxZoom: 20,
    subdomains:['mt0','mt1','mt2','mt3'],
    attribution: '&copy; Google Maps'
}).addTo(map);

// 1. Camera Logic
startCamBtn.onclick = async () => {
    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
        liveVideo.srcObject = cameraStream;
        startCamBtn.classList.add("d-none");
        stopCamBtn.classList.remove("d-none");
        captureBtn.disabled = false;
    } catch (err) { alert("Camera error: " + err.message); }
};

stopCamBtn.onclick = () => {
    if (cameraStream) cameraStream.getTracks().forEach(t => t.stop());
    liveVideo.srcObject = null;
    startCamBtn.classList.remove("d-none");
    stopCamBtn.classList.add("d-none");
};

// --- NEW FUNCTIONAL ADDITIONS ---

async function fetchWeedDetails(name) {
    const infoPanel = document.getElementById("weed-info-panel");
    //if (!infoPanel) return;

    try {
        const res = await fetch(`${API_BASE}/api/weeds`);
        const data = await res.json();
        
        // Improved Search: Checks if the detected name is inside the common OR scientific name
        const weed = data.weeds.find(w => 
            name.toLowerCase().trim() === w.scientific_name.toLowerCase().trim() ||
            name.toLowerCase().trim() === w.common_name.toLowerCase().trim() ||
            w.scientific_name.toLowerCase().includes(name.toLowerCase().trim())
        );

        if (weed) {
            infoPanel.innerHTML = `
                <div class="p-2">
                    <h6 class="fw-bold text-success mb-1">${weed.common_name}</h6>
                    <p class="text-muted small mb-2"><i>${weed.scientific_name}</i></p>
                    <p class="mb-3" style="font-size: 0.85rem;">${weed.description}</p>
                    <a href="${weed.external_link}" target="_blank" class="btn btn-sm btn-success w-100">
                        <i class="bi bi-box-arrow-up-right me-1"></i> Wikipedia Details
                    </a>
                </div>`;
        } else {
            infoPanel.innerHTML = `<div class="p-2 text-muted small">No database entry for "${name}".</div>`;
        }
    } catch (err) {
        console.error("Info Panel Error:", err);
        infoPanel.innerHTML = "Failed to load weed information.";
    }
}
// --- ADD THIS HERE ---
function jumpToLocation(lat, lng, name) {
    if (!lat || !lng || lat === "null" || lng === "null") {
        alert("No GPS data available for this detection.");
        return;
    }
    // Smoothly pan the map to the stored coordinates
    map.setView([lat, lng], 18, { animate: true });
    
    // Add a temporary marker or open a popup to highlight it
    L.popup()
        .setLatLng([lat, lng])
        .setContent(`<b>Past Detection:</b><br>${name}`)
        .openOn(map);
}
// --- PASTE THIS RIGHT AFTER fetchWeedDetails ---

async function updateHistory() {
    const historyList = document.getElementById("history-list");
    if (!historyList) return;

    try {
        const res = await fetch(`${API_BASE}/api/detections/recent`);
        const data = await res.json();
        
        if (data.history && data.history.length > 0) {
            historyList.innerHTML = data.history.map(h => `
                <div class="list-group-item border-0 border-bottom py-2 bg-transparent history-item" 
                     onclick="jumpToLocation(${h.lat}, ${h.lng}, '${h.main_weeds}')" 
                     style="cursor: pointer;">
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="fw-bold text-success" style="font-size: 0.85rem;">
                            <i class="bi bi-flower1 me-1"></i>${h.main_weeds}
                        </span>
                        <span class="badge bg-light text-dark border" style="font-size: 0.7rem;">
                            ${h.total_detections} found
                        </span>
                    </div>
                    <div class="text-muted" style="font-size: 0.7rem;">
                        <i class="bi bi-clock me-1"></i>${h.timestamp}
                    </div>
                </div>
            `).join('');
        } else {
            historyList.innerHTML = '<div class="p-3 text-center text-muted small">No recent activity</div>';
        }
    } catch (err) {
        console.error("History Error:", err);
    }
}
const weedIcon = L.divIcon({
    html: '<i class="bi bi-flower1" style="color: #2d6a4f; font-size: 24px; text-shadow: 0 0 3px white;"></i>',
    className: 'custom-weed-icon',
    iconSize: [24, 24],
    iconAnchor: [12, 12]
});
// --- REST OF YOUR CODE CONTINUES HERE ---
// 2. AI Processing & Mapping
async function analyzeMedia(blob) {
    if (loader) loader.classList.replace("d-none", "d-flex");

    navigator.geolocation.getCurrentPosition(async (pos) => {
        const myLat = pos.coords.latitude;
        const myLng = pos.coords.longitude;

        const formData = new FormData();
        formData.append("file", blob, "upload.jpg");
        formData.append("lat", myLat); 
        formData.append("lng", myLng);

        try {
            const res = await fetch(`${API_BASE}/process`, { method: "POST", body: formData });
            const data = await res.json();
            
            if (data.status === "success") {
                resultImg.src = `${API_BASE}${data.processed_url}?t=${Date.now()}`;
                resultImg.classList.remove("d-none");
                if (placeholder) placeholder.classList.add("d-none");

                if (data.detections && data.detections.length > 0) {
                    const top = data.detections[0];
                    
                    // CRITICAL: MOVE THE MAP to your actual real-time location
                    map.setView([myLat, myLng], 16); 
                    //L.marker([myLat, myLng]).addTo(map)
                    L.marker([myLat, myLng], { icon: weedIcon }).addTo(map)
                        .bindPopup(`<b>${top.name}</b> detected at your location`)
                        .openPopup();

                    // Update UI Components
                    updateGauge(top.confidence, top.name);
                    fetchWeedDetails(top.name);
                }
                renderResults(data.detections);
                updateHistory();
            }
        } catch (err) {
            console.error("Mapping Error:", err);
        } finally {
            if (loader) loader.classList.replace("d-flex", "d-none");
        }
    }, (error) => {
        alert("Please enable Location services in your browser settings.");
        if (loader) loader.classList.replace("d-flex", "d-none");
    });
}

function updateGauge(score, label) {
    const val = Math.round(score * 100);
    const gVal = document.getElementById("gauge-value");
    const gLab = document.getElementById("gauge-label");
    const gProg = document.getElementById("gauge-progress");
    if(gVal) gVal.innerText = val + "%";
    if(gLab) gLab.innerText = label;
    // Animates the green confidence ring
    if(gProg) gProg.style.strokeDashoffset = 251.2 - (val / 100) * 251.2;
}

function renderResults(dets) {
    const div = document.getElementById("conf-scores");
    if (!div) return;
    // Creates clickable badges that open weed info
    div.innerHTML = dets.map(d => `
        <button class="btn btn-outline-success btn-sm me-2 mb-2" onclick="fetchWeedDetails('${d.name}')">
            ${d.name} ${(d.confidence*100).toFixed(0)}%
        </button>`).join('') || "No weeds detected.";
}

// Button Triggers
captureBtn.onclick = () => {
    const canvas = document.getElementById("capture-canvas");
    if (!canvas) return;
    canvas.width = liveVideo.videoWidth;
    canvas.height = liveVideo.videoHeight;
    canvas.getContext("2d").drawImage(liveVideo, 0, 0);
    canvas.toBlob(blob => analyzeMedia(blob), "image/jpeg");
};

document.getElementById("image-detect-btn").onclick = () => {
    const input = document.getElementById("image-input");
    if (input.files[0]) analyzeMedia(input.files[0]);
};
// Load history when the page first opens
document.addEventListener("DOMContentLoaded", updateHistory);

// Map Fullscreen Toggle Logic
document.getElementById('map-expand-btn').onclick = () => {
    const mapDiv = document.getElementById('field-map');
    if (!document.fullscreenElement) {
        mapDiv.requestFullscreen().catch(err => {
            alert(`Error attempting to enable full-screen mode: ${err.message}`);
        });
    } else {
        document.exitFullscreen();
    }
};

// Ensure the map resizes correctly when entering/exiting fullscreen
document.addEventListener('fullscreenchange', () => {
    setTimeout(() => {
        map.invalidateSize();
    }, 200);
});