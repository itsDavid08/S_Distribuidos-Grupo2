// --- 1. Inicialização do Mapa (Lisboa) ---
const map = L.map('map').setView([38.7138, -9.1396], 15);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

const markerLayer = L.layerGroup().addTo(map);

// --- 2. Configuração da API ---
const API_URL = '/api';

// --- 3. Elementos do DOM ---
const tableBody = document.getElementById('ranking-body');
const dataContainer = document.getElementById('data-container');
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
            dataContainer.textContent = JSON.stringify(data, null, 2);
            renderUI();
        })
        .catch(error => {
            console.error('Erro ao fazer polling:', error);
            dataContainer.textContent = 'Erro ao carregar dados.';
        });
}

// --- 7. Função de Desenho (Render) ---
function renderUI() {
    // Aplica o filtro APENAS para o mapa
    const filteredForMap = allParticipants.filter(p => {
        if (!filterText) return true;
        
        // Suporta filtro por múltiplos IDs: "1, 2, 3"
        const filterIds = filterText.split(',').map(id => id.trim());
        const participantId = String(p.runner_id || '').toLowerCase();
        
        return filterIds.some(filterId => participantId.includes(filterId));
    });

    // Mapa usa dados filtrados
    updateMapMarkers(filteredForMap);
    
    // Tabela SEMPRE usa todos os participantes (sem filtro)
    updateRankingTable(allParticipants);
}

// --- 8. Atualização dos Marcadores no Mapa ---
function updateMapMarkers(participantes) {
    markerLayer.clearLayers();
    
    participantes.forEach(p => {
        if (p.positionX !== undefined && p.positionY !== undefined) {
            // Converte posições (0-99) para coordenadas de Lisboa
            const lat = 38.7138 + (p.positionX / 100) * 0.02;
            const lon = -9.1396 + (p.positionY / 100) * 0.02;
            
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

// --- 9. Atualização da Tabela de Ranking ---
function updateRankingTable(participantes) {
    tableBody.innerHTML = '';
    
    if (participantes.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="8">Nenhum participante encontrado</td></tr>';
        return;
    }
    
    // Ordena por velocidade total (magnitude do vetor)
    const sorted = [...participantes].sort((a, b) => {
        const velA = Math.sqrt(Math.pow(a.speedX || 0, 2) + Math.pow(a.speedY || 0, 2));
        const velB = Math.sqrt(Math.pow(b.speedX || 0, 2) + Math.pow(b.speedY || 0, 2));
        return velB - velA;
    });
    
    // Mostra apenas o Top 10
    sorted.slice(0, 10).forEach((p, index) => {
        const velocidadeTotal = Math.sqrt(Math.pow(p.speedX || 0, 2) + Math.pow(p.speedY || 0, 2));
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${p.runner_id || 'N/A'}</td>
            <td>${velocidadeTotal.toFixed(2)}</td>
            <td>${p.speedX || 0}</td>
            <td>${p.speedY || 0}</td>
            <td>${p.positionX || 0}</td>
            <td>${p.positionY || 0}</td>
            <td>
                <button class="btn btn-small copy-btn" onclick="copyRunnerId('${p.runner_id}')">
                    Copiar ID
                </button>
            </td>
        `;
        tableBody.appendChild(row);
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
fetchData();
setInterval(fetchData, 2000);