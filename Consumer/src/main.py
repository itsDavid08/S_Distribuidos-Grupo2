"""
Ponto de entrada principal para a aplicação FastAPI.

Este módulo inicializa a aplicação FastAPI, configura o logging,
gere o ciclo de vida (lifespan) para iniciar e parar o consumidor
Redpanda em segundo plano, e inclui as rotas da API.
"""

import asyncio
import logging
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI

from .api.routes import router as api_router
from .core.consumer import RabbitMQConsumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('RabbitMQMicroservice')

stop_consumer_event = threading.Event()
rabbitmq_consumer: RabbitMQConsumer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager para o ciclo de vida da aplicação FastAPI.
    Inicia o consumidor RabbitMQ no arranque e pára-o de forma graciosa no encerramento.
    """
    global rabbitmq_consumer
    logger.info("Iniciando a thread do consumidor RabbitMQ...")
    main_event_loop = asyncio.get_running_loop()
    rabbitmq_consumer = RabbitMQConsumer(stop_event=stop_consumer_event, main_loop=main_event_loop)
    rabbitmq_consumer.start()
    yield
    logger.info("Aplicação FastAPI está a encerrar. Sinalizando para o consumidor parar...")
    stop_consumer_event.set()
    if rabbitmq_consumer and rabbitmq_consumer.consumer_thread.is_alive():
        rabbitmq_consumer.consumer_thread.join()

app = FastAPI(title="RabbitMQ Consumer Microservice", lifespan=lifespan)
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)