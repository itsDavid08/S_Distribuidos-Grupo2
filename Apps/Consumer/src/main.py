import signal
import logging
import threading
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from .core.consumer import RabbitMQConsumer
from .config import settings

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

    # Deixar a criação do cliente/BD para o loop dedicado do consumidor
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