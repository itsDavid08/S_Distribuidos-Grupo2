import signal
import logging
import threading
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from .core.consumer import RabbitMQConsumer
from .config import settings
from .metrics import start_metrics_server

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ConsumerMicroservice')

async def ensure_database_and_collection(db):
    """
    Garante que a coleção existe; se não existir, cria-a.
    Isto força também a criação da base de dados caso ainda não exista.
    """
    collections = await db.list_collection_names()
    if settings.COLLECTION_NAME not in collections:
        await db.create_collection(settings.COLLECTION_NAME)
        # Opcional: criar índice pelo campo 'timestampMs'
        try:
            await db[settings.COLLECTION_NAME].create_index('timestampMs')
        except Exception:
            # Ignora erros de criação de índice (ex.: índice já existe)
            pass
        logger.info(f"Coleção criada: {settings.DB_NAME}.{settings.COLLECTION_NAME}")
    else:
        logger.info(f"Coleção existente: {settings.DB_NAME}.{settings.COLLECTION_NAME}")

def main():
    """
    Função principal que configura e inicia o microserviço consumidor.
    """
    stop_event = threading.Event()
    
    # --- Configuração da Conexão MongoDB ---
    logger.info("A ligar ao MongoDB...")
    try:
        # A string de conexão é construída a partir das variáveis de ambiente
        mongo_connection_string = f"mongodb://{settings.MONGO_USER}:{settings.MONGO_PASS}@{settings.MONGO_URL}"
        mongo_client = AsyncIOMotorClient(mongo_connection_string)
        db = mongo_client.get_database(settings.DB_NAME)
        logger.info("Ligação ao MongoDB configurada com sucesso.")
    except Exception as e:
        logger.error(f"Não foi possível ligar ao MongoDB: {e}")
        return # Encerra se não conseguir ligar à base de dados

    # --- Início do Servidor de Métricas Prometheus ---
    logger.info(f"A iniciar o servidor de métricas na porta {settings.METRICS_PORT}...")
    start_metrics_server(settings.METRICS_PORT)

    # --- Início do Consumidor RabbitMQ ---
    logger.info("Iniciando a thread do consumidor RabbitMQ...")
    rabbitmq_consumer = RabbitMQConsumer(
        stop_event=stop_event,
        db=None  # será inicializado no loop dedicado
    )
    rabbitmq_consumer.start()

    # --- Lógica de Encerramento Gracioso ---
    def shutdown_handler():
        logger.info("Sinal de encerramento recebido. A parar o consumidor...")
        stop_event.set()
        if rabbitmq_consumer and rabbitmq_consumer.is_alive():
            rabbitmq_consumer.join()
        logger.info("Conexões fechadas. Adeus!")

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    logger.info("Consumidor em execução. Pressione Ctrl+C para parar.")
    if rabbitmq_consumer and rabbitmq_consumer.is_alive():
        rabbitmq_consumer.join()

if __name__ == "__main__":
    main()