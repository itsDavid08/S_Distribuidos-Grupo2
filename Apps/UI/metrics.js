const client = require('prom-client');

// Cria um registo para as métricas
const register = new client.Registry();

// Adiciona métricas padrão (CPU, Memória, Event Loop, etc.)
client.collectDefaultMetrics({ register });

// --- Métricas Personalizadas ---

// Contador para o número total de requisições
const HTTP_REQUESTS_TOTAL = new client.Counter({
    name: 'ui_http_requests_total',
    help: 'Total de requisições HTTP recebidas pela UI',
    labelNames: ['method', 'route', 'status_code'],
    registers: [register]
});

// Histograma para a latência das requisições
const HTTP_REQUEST_DURATION_SECONDS = new client.Histogram({
    name: 'ui_http_request_duration_seconds',
    help: 'Duração das requisições HTTP em segundos',
    labelNames: ['method', 'route', 'status_code'],
    buckets: [0.1, 0.3, 0.5, 1, 3, 5], // Buckets de tempo (s)
    registers: [register]
});

module.exports = {
    register,
    HTTP_REQUESTS_TOTAL,
    HTTP_REQUEST_DURATION_SECONDS
};