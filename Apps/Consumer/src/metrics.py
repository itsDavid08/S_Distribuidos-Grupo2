from prometheus_client import start_http_server, Counter, Gauge, Histogram
import logging

logger = logging.getLogger(__name__)

# --- Métricas ---

# Contador para o número total de mensagens processadas
MESSAGES_PROCESSED = Counter(
    'consumer_messages_processed_total',
    'Total de mensagens processadas pelo consumidor'
)

# Histograma para medir a latência do processamento de mensagens
PROCESSING_TIME = Histogram(
    'consumer_message_processing_duration_seconds',
    'Tempo gasto a processar uma mensagem'
)

# Gauge para a última vez que uma mensagem foi processada
LAST_MESSAGE_TIMESTAMP = Gauge(
    'consumer_last_message_processed_timestamp_seconds',
    'Timestamp da última mensagem processada'
)

def start_metrics_server(port: int):
    """Inicia um servidor HTTP para expor as métricas do Prometheus."""
    try:
        start_http_server(port)
        logger.info(f"Servidor de métricas Prometheus iniciado na porta {port}")
    except Exception as e:
        logger.error(f"Não foi possível iniciar o servidor de métricas: {e}")
