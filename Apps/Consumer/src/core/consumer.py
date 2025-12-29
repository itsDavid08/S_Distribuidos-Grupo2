"""
Módulo do Consumidor RabbitMQ.

Este módulo define a classe `RabbitMQConsumer`, responsável por se conectar
ao RabbitMQ, consumir mensagens de uma fila específica, processá-las e
transmiti-las para os clientes WebSocket conectados.
"""
import asyncio
import json
import logging
import threading
import pika
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
from pika.exceptions import AMQPConnectionError
import time

from ..config import settings
from ..metrics import MESSAGES_PROCESSED, PROCESSING_TIME, LAST_MESSAGE_TIMESTAMP
from .repository import save_telemetry_data
from .state import manager

logger = logging.getLogger('ConsumerMicroservice')

class RabbitMQConsumer(threading.Thread):
    """Encapsula a lógica de consumo de mensagens do RabbitMQ."""

    def __init__(self, stop_event: threading.Event, db: AsyncIOMotorDatabase):
        """Inicializa o consumidor."""
        self.connection = None
        self.channel = None
        self._stop_event = stop_event
        # Loop assíncrono será criado e iniciado num fio dedicado
        self._loop = None
        self._loop_thread = None
        self._db_loop_ready = threading.Event()
        self._db = db
        self._db_client = None  # cliente Motor será criado no loop dedicado
        super().__init__(target=self.run, daemon=True)

    def _start_db_loop(self):
        """Cria e inicia um event loop de asyncio num fio dedicado (mesmo fio em que é criado)."""
        def _runner():
            # Criar e associar o loop a ESTE fio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._loop = loop

            async def _init_db():
                # Criar cliente e BD no mesmo loop que será usado durante toda a vida do serviço
                mongo_connection_string = f"mongodb://{settings.MONGO_USER}:{settings.MONGO_PASS}@{settings.MONGO_URL}"
                self._db_client = AsyncIOMotorClient(mongo_connection_string)
                self._db = self._db_client.get_database(settings.DB_NAME)

                # Garantir coleção e índice
                collections = await self._db.list_collection_names()
                if settings.COLLECTION_NAME not in collections:
                    await self._db.create_collection(settings.COLLECTION_NAME)
                    try:
                        await self._db[settings.COLLECTION_NAME].create_index('timestampMs')
                    except Exception:
                        pass
                    logger.info(f"Coleção criada: {settings.DB_NAME}.{settings.COLLECTION_NAME}")
                else:
                    logger.info(f"Coleção existente: {settings.DB_NAME}.{settings.COLLECTION_NAME}")

            # Inicializar DB antes de começar o loop
            loop.run_until_complete(_init_db())

            # Sinalizar que o loop+DB estão prontos
            self._db_loop_ready.set()

            # Correr para sempre até ser parado
            loop.run_forever()
            # Encerramento limpo do loop
            loop.close()
        self._loop_thread = threading.Thread(target=_runner, name="db-event-loop", daemon=True)
        self._loop_thread.start()
        # Esperar até o loop e a DB estarem prontos
        self._db_loop_ready.wait()

    def _stop_db_loop(self):
        """Pára o event loop dedicado e junta o fio."""
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._loop_thread and self._loop_thread.is_alive():
            self._loop_thread.join(timeout=3)
        # Fechar cliente MongoDB
        if self._db_client:
            self._db_client.close()
            self._db_client = None

    def _connect(self):
        """Tenta conectar-se ao RabbitMQ."""
        while not self._stop_event.is_set():
            try:
                credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASS)
                parameters = pika.ConnectionParameters('rabbit-service', 5672, '/', credentials)
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=settings.QUEUE_NAME, durable=True)
                logger.info(f"Consumidor RabbitMQ conectado e a consumir da fila: {settings.QUEUE_NAME}")
                return True
            except AMQPConnectionError as e:
                logger.error(f"Não foi possível conectar ao RabbitMQ: {e}. A tentar novamente em 5 segundos...")
                if self.connection and self.connection.is_open:
                    self.connection.close()
                self._stop_event.wait(5) # Use stop_event.wait for a non-blocking sleep
        
        return False # Return False if stop_event was set

    def _process_message(self, ch, method, properties, body):
        """
        Processa uma única mensagem recebida do RabbitMQ.
        Descodifica o JSON, atualiza o estado global e agenda a escrita no MongoDB
        de forma thread-safe usando o event loop dedicado.
        """
        start_time = time.time()
        
        try:
            with PROCESSING_TIME.time():
                # Descodificar a mensagem
                raw_data = json.loads(body.decode('utf-8'))

                # Mapear a lista para campos explícitos
                telemetry_doc = {
                    "runner_id": raw_data[0],
                    "positionX": raw_data[1],
                    "positionY": raw_data[2],
                    "speedX": raw_data[3],
                    "speedY": raw_data[4],
                    "timestampMs": getattr(properties, "timestamp", None)
                }

                # Atualizar o estado global (para WebSockets/API)
                manager.update_last_message(telemetry_doc)

                if not self._loop or not self._loop.is_running():
                    logger.error("Event loop de DB não está a correr; não é possível guardar no MongoDB.")
                else:
                    # Agendar escrita no loop assíncrono dedicado
                    future = asyncio.run_coroutine_threadsafe(
                        save_telemetry_data(self._db, telemetry_doc),
                        self._loop
                    )
                    # Registar caso a futura falhe
                    def _done(fut):
                        try:
                            fut.result()
                        except Exception as ex:
                            logger.error(f"Falha ao inserir no MongoDB: {ex}")
                    future.add_done_callback(_done)

                    # Incrementa contador
                    MESSAGES_PROCESSED.inc()
                    
                    # Atualiza timestamp
                    LAST_MESSAGE_TIMESTAMP.set(time.time())
                    
                    # Regista duração
                    duration = time.time() - start_time
                    PROCESSING_TIME.observe(duration)
                    
                    logger.info("Mensagem recebida e agendada para ser guardada no MongoDB.")

        except json.JSONDecodeError:
            logger.error(f"Erro ao descodificar JSON: {body.decode('utf-8')}")
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        """
        Loop principal do consumidor, executado num fio separado.
        Inicia o loop dedicado de DB, conecta ao RabbitMQ e processa eventos
        até que o evento de paragem seja acionado.
        """
        # Iniciar o event loop dedicado ao acesso ao MongoDB (no fio certo)
        self._start_db_loop()
        logger.info("Event loop de DB iniciado.")

        logger.info("Conectando ao RabbitMQ...")
        if not self._connect():
            self._stop_db_loop()
            return

        try:
            self.channel.basic_consume(queue=settings.QUEUE_NAME, on_message_callback=self._process_message)
            while not self._stop_event.is_set():
                self.connection.process_data_events(time_limit=1)
        except (pika.exceptions.StreamLostError, pika.exceptions.AMQPConnectionError) as e:
            logger.error(f"A ligação ao RabbitMQ foi perdida: {e}. A thread do consumidor vai terminar.")
        finally:
            if self.connection and self.connection.is_open:
                self.connection.close()
            self._stop_db_loop()
            logger.info("Thread do consumidor RabbitMQ encerrada.")
