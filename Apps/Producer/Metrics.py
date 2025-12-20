from prometheus_client import start_http_server, Counter, Gauge, Histogram
import logging

logger = logging.getLogger(__name__)

# contador de mensagens criadas
MESSAGES_CREATED = Counter(
    'producer_messages_created_total',
    'Total de mensagens criadas pelo produtor'
)

# histograma para medir latencia de criacao de mensagens
CREATION_TIME = Histogram(
    'total_message_creation_duration_seconds',
    'Tempo gasto produzindo uma mensagem'
)

# gauge para a ultima vez que uma mensagem é criada
LAST_MESSAGE_TIMESTAMP = Gauge(
    'producer_last_message_created_timestamp_seconds',
    'Timestamp da ultima mensagem gerada'
)

