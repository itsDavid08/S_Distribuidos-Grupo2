from prometheus_client import start_http_server, Counter, Gauge, Histogram
import logging

logger = logging.getLogger(__name__)

# --- Métricas ---

# Contador para o número total de requisições
REQUESTS_TOTAL = Counter(
    'api_requests_total',
    'Total de requisições recebidas pela API',
    ['method', 'endpoint', 'status_code']
)

# Histograma para medir a latência das requisições
REQUEST_LATENCY = Histogram(
    'api_request_duration_seconds',
    'Tempo gasto a processar uma requisição',
    ['endpoint']
)

# Gauge para o estado da conexão com a BD
DB_CONNECTION_STATUS = Gauge(
    'api_db_connection_status',
    'Estado da conexão ao MongoDB (1 = conectado, 0 = desconectado)'
)

def start_metrics_server(port: int):
    """Inicia um servidor HTTP para expor as métricas do Prometheus."""
    try:
        start_http_server(port)
        logger.info(f"Servidor de métricas Prometheus iniciado na porta {port}")
    except Exception as e:
        logger.error(f"Não foi possível iniciar o servidor de métricas: {e}")
