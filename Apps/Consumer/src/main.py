import signal
import logging
import threading
from motor.motor_asyncio import AsyncIOMotorClient

from .core.consumer import RabbitMQConsumer
from .config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ConsumerMicroservice')

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
        db = mongo_client.get_database("telemetry_db")
        logger.info("Ligação ao MongoDB configurada com sucesso.")
    except Exception as e:
        logger.error(f"Não foi possível ligar ao MongoDB: {e}")
        return # Encerra se não conseguir ligar à base de dados

    # --- Início do Consumidor RabbitMQ ---
    logger.info("Iniciando a thread do consumidor RabbitMQ...")
    rabbitmq_consumer = RabbitMQConsumer(
        stop_event=stop_event,
        db=db
    )
    rabbitmq_consumer.start()

    # --- Lógica de Encerramento Gracioso ---
    def shutdown_handler(signum, frame):
        logger.info("Sinal de encerramento recebido. A parar o consumidor...")
        stop_event.set()
        if rabbitmq_consumer and rabbitmq_consumer.is_alive():
            rabbitmq_consumer.join() # Espera que a thread do consumidor termine
        mongo_client.close()
        logger.info("Conexão com o MongoDB fechada. Adeus!")

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    
    logger.info("Consumidor em execução. Pressione Ctrl+C para parar.")
    # Mantém a thread principal viva, à espera que a thread do consumidor termine
    if rabbitmq_consumer and rabbitmq_consumer.is_alive():
        rabbitmq_consumer.join()

if __name__ == "__main__":
    main()