const map = L.map('map').setView([52.5186, 13.3761], 16);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

const markerLayer = L.layerGroup().addTo(map);

// CORRECCIÓN: URL directa de la API
const API_URL = 'http://api-service:8000';

function fetchData() {
    fetch(`${API_URL}/dados`)
        .then(res => res.json())
        .then(data => {
            document.getElementById('data-container').textContent = JSON.stringify(data, null, 2);
            updateMapMarkers(data.participantes || []);
        })
        .catch(error => {
            console.error('Erro ao fazer polling:', error);
            document.getElementById('data-container').textContent = 'Erro ao carregar dados.';
        });
}

function updateMapMarkers(participantes) {
    markerLayer.clearLayers();
    
    participantes.forEach(p => {
        if (p.positionX && p.positionY) {
            // Convierte posiciones a coordenadas geográficas
            const lat = 52.5 + (p.positionX / 100) * 0.1;
            const lon = 13.3 + (p.positionY / 100) * 0.1;
            
            L.marker([lat, lon])
             .addTo(markerLayer)
             .bindPopup(`Pos: (${p.positionX}, ${p.positionY})<br>Vel: (${p.speedX}, ${p.speedY})`);
        }
    });
}

// Inicia polling
fetchData();
setInterval(fetchData, 2000);