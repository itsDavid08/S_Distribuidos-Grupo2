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
from .core.consumer import RedpandaConsumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('RedpandaMicroservice')

stop_consumer_event = threading.Event()
redpanda_consumer: RedpandaConsumer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager para o ciclo de vida da aplicação FastAPI.
    Inicia o consumidor Redpanda no arranque e pára-o de forma graciosa no encerramento.
    """
    global redpanda_consumer
    logger.info("Iniciando a thread do consumidor Redpanda...")
    main_event_loop = asyncio.get_running_loop()
    redpanda_consumer = RedpandaConsumer(stop_event=stop_consumer_event, main_loop=main_event_loop)
    redpanda_consumer.start()
    yield
    logger.info("Aplicação FastAPI está a encerrar. Sinalizando para o consumidor parar...")
    stop_consumer_event.set()
    if redpanda_consumer and redpanda_consumer.consumer_thread.is_alive():
        redpanda_consumer.consumer_thread.join()

app = FastAPI(title="Redpanda Consumer Microservice", lifespan=lifespan)
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)