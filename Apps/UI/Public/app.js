// --- 1. Inicialização do Mapa (Lisboa) ---
const map = L.map('map').setView([38.7138, -9.1396], 15);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

const markerLayer = L.layerGroup().addTo(map);
const routeLayer = L.layerGroup().addTo(map);

// --- 2. Configuração da API ---
const API_URL = '/api';

// --- 3. Elementos do DOM ---
const filterInput = document.getElementById('filter-input');
const applyFilterBtn = document.getElementById('apply-filter-btn');
const clearFilterBtn = document.getElementById('clear-filter-btn');

// --- 4. Variáveis de Estado Global ---
let allParticipants = [];
let filterText = '';

// --- 5. Event Listeners para o Filtro ---
applyFilterBtn.addEventListener('click', () => {
    filterText = filterInput.value.toLowerCase().trim();
    renderUI();
});

clearFilterBtn.addEventListener('click', () => {
    filterInput.value = '';
    filterText = '';
    renderUI();
});

// Permitir aplicar filtro com Enter
filterInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        filterText = filterInput.value.toLowerCase().trim();
        renderUI();
    }
});

// --- 6. Função de Polling (Fetch) ---
function fetchData() {
    fetch(`${API_URL}/dados`)
        .then(res => res.json())
        .then(data => {
            allParticipants = data.participantes || [];
            renderUI();
        })
        .catch(error => {
            console.error('Erro ao fazer polling:', error);
        });
}

// --- 6.1. Función para cargar y dibujar rutas una sola vez al inicio ---
function loadAndDrawRoutes() {
    fetch(`${API_URL}/rutas`)
        .then(res => res.json())
        .then(data => {
            const rutas = data.rutas || [];
            rutas.forEach(ruta => {
                drawRoute(ruta.id, ruta.points, ruta.name);
            });
        })
        .catch(error => {
            console.error('Erro ao carregar rotas:', error);
        });
}

// --- 6.2. Função para desenhar uma rota no mapa ---
function drawRoute(routeId, points, name) {
    // Offsets para separar as rotas no mapa (em graus)
    const routeOffsets = {
        1: {lat: 0, lon: 0},        // Rota 1: posição original
        2: {lat: 0.005, lon: 0.005}, // Rota 2: ligeiramente deslocada
        3: {lat: -0.005, lon: 0.005} // Rota 3: deslocada noutra direção
    };
    
    const offset = routeOffsets[routeId] || {lat: 0, lon: 0};
    
    // Converter pontos da rota para coordenadas Leaflet com offset
    const latLngs = points.map(point => {
        const lat = 38.7138 + (point[0] / 100) * 0.02 + offset.lat;
        const lon = -9.1396 + (point[1] / 100) * 0.02 + offset.lon;
        return [lat, lon];
    });
    
    // Cores diferentes para cada rota
    const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#6c5ce7'];
    const color = colors[(routeId - 1) % colors.length];
    
    const polyline = L.polyline(latLngs, {
        color: color,
        weight: 3,
        opacity: 1.0
    }).addTo(routeLayer);
    
    polyline.bindPopup(`<b>${name || 'Rota ' + routeId}</b>`);
}

// --- 6.3. Utilitário para manter só um registo por corredor ---
function dedupeByRunner(participantes) {
    const latestByRunner = new Map();
    participantes.forEach((p, idx) => {
        const key = p.runner_id ?? idx; // fallback para evitar perda de itens sem id
        const prev = latestByRunner.get(key);
        const prevTs = prev?.timestampMs ?? -1;
        const curTs = p.timestampMs ?? -1;
        if (!prev || curTs >= prevTs) {
            latestByRunner.set(key, p);
        }
    });
    return Array.from(latestByRunner.values());
}

// --- 7. Função de Desenho (Render) ---
function renderUI() {
    const uniqueParticipants = dedupeByRunner(allParticipants);

    // Aplica o filtro APENAS para o mapa (sobre a lista única)
    const filteredForMap = uniqueParticipants.filter(p => {
        if (!filterText) return true;

        // Suporta filtro por múltiplos IDs: "1, 2, 3"
        const filterIds = filterText.split(',').map(id => id.trim());
        const participantId = String(p.runner_id || '').toLowerCase();

        return filterIds.some(filterId => participantId.includes(filterId));
    });

    // Mapa usa dados filtrados (um marcador por corredor)
    updateMapMarkers(filteredForMap);

    // Tabelas usam a lista única (sem duplicação de corredores) - separadas por rota
    updateRankingTables(uniqueParticipants);
}

// --- 8. Atualização dos Marcadores no Mapa ---
function updateMapMarkers(participantes) {
    markerLayer.clearLayers();
    
    participantes.forEach(p => {
        if (p.positionX !== undefined && p.positionY !== undefined) {
            // Offsets para separar as rotas no mapa (mesmos da função drawRoute)
            const routeOffsets = {
                1: {lat: 0, lon: 0},        // Rota 1: posição original
                2: {lat: 0.005, lon: 0.005}, // Rota 2: ligeiramente deslocada
                3: {lat: -0.005, lon: 0.005} // Rota 3: deslocada noutra direção
            };
            
            const routeId = p.route_id || 1;
            const offset = routeOffsets[routeId] || {lat: 0, lon: 0};
            
            // Converte posições para coordenadas de Lisboa com offset da rota
            // positionX e positionY já são valores absolutos (-20 a 22)
            // Aplicar mesma transformação que as rotas
            const lat = 38.7138 + (p.positionX / 100) * 0.02 + offset.lat;
            const lon = -9.1396 + (p.positionY / 100) * 0.02 + offset.lon;
            
            const velocidadeTotal = Math.sqrt(Math.pow(p.speedX || 0, 2) + Math.pow(p.speedY || 0, 2));
            
            const popupContent = `
                <b>ID:</b> ${p.runner_id}<br>
                <b>Posição:</b> (${p.positionX}, ${p.positionY})<br>
                <b>Velocidade:</b> ${velocidadeTotal.toFixed(2)}
            `;
            
            L.marker([lat, lon])
             .addTo(markerLayer)
             .bindPopup(popupContent);
        }
    });
}

// --- 9. Atualización de Tabelas de Ranking por Rota ---
function updateRankingTables(participantes) {
    // Definir segmentos totais por rota (baseado em ROUTES definidas na API)
    const routeSegments = {
        1: 4,  // Rota Quadrada: 5 pontos = 4 segmentos
        2: 3,  // Rota Irregular: 4 pontos = 3 segmentos
        3: 3   // Rota Ascendente: 4 pontos = 3 segmentos
    };
    
    // Agrupar participantes por rota
    const participantsByRoute = {
        1: [],
        2: [],
        3: []
    };
    
    participantes.forEach(p => {
        const routeId = p.route_id || 1;
        if (participantsByRoute[routeId]) {
            participantsByRoute[routeId].push(p);
        }
    });
    
    // Atualizar tabela para cada rota
    [1, 2, 3].forEach(routeId => {
        const tableBodyId = `ranking-body-${routeId}`;
        const tableBody = document.getElementById(tableBodyId);
        const routeParticipants = participantsByRoute[routeId] || [];
        const maxSegments = routeSegments[routeId] || 3;
        
        tableBody.innerHTML = '';
        
        if (routeParticipants.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="8">Nenhum participante nesta rota</td></tr>';
            return;
        }
        
        // Ordenar por progresso (segment/maxSegments) descendente
        const sorted = [...routeParticipants].sort((a, b) => {
            const progressA = (a.current_segment || 0) / maxSegments;
            const progressB = (b.current_segment || 0) / maxSegments;
            return progressB - progressA;
        });
        
        sorted.forEach((p, index) => {
            const velocidadeTotal = Math.sqrt(Math.pow(p.speedX || 0, 2) + Math.pow(p.speedY || 0, 2));
            const segment = p.current_segment || 0;
            const progress = ((segment / maxSegments) * 100).toFixed(1);
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${p.runner_id || 'N/A'}</td>
                <td>${progress}%</td>
                <td>${segment}/${maxSegments}</td>
                <td>${velocidadeTotal.toFixed(2)}</td>
                <td>${(p.positionX || 0).toFixed(2)}</td>
                <td>${(p.positionY || 0).toFixed(2)}</td>
                <td>
                    <button class="btn btn-small copy-btn" onclick="copyRunnerId('${p.runner_id}')">
                        Copiar ID
                    </button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    });
}

// --- 10. Função para Copiar Runner ID ---
function copyRunnerId(runnerId) {
    // Usa a API moderna do Clipboard
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(runnerId).then(() => {
            alert(`ID ${runnerId} copiado!`);
        }).catch(err => {
            console.error('Erro ao copiar:', err);
            fallbackCopyTextToClipboard(runnerId);
        });
    } else {
        // Fallback para navegadores antigos
        fallbackCopyTextToClipboard(runnerId);
    }
}

// Fallback para navegadores que não suportam Clipboard API
function fallbackCopyTextToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.top = '0';
    textArea.style.left = '0';
    textArea.style.opacity = '0';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        alert(`ID ${text} copiado!`);
    } catch (err) {
        console.error('Erro ao copiar:', err);
        alert('Erro ao copiar ID');
    }
    
    document.body.removeChild(textArea);
}

// --- 11. Iniciar o Loop de Polling ---
loadAndDrawRoutes(); // Cargar y dibujar rutas una sola vez al inicio
fetchData();
setInterval(fetchData, 2000);