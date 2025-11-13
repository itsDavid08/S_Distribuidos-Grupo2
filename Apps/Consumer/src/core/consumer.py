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
from motor.motor_asyncio import AsyncIOMotorDatabase
from pika.exceptions import AMQPConnectionError

from ..config import settings
from .repository import save_telemetry_data

logger = logging.getLogger('ConsumerMicroservice')

class RabbitMQConsumer(threading.Thread):
    """Encapsula a lógica de consumo de mensagens do RabbitMQ."""

    def __init__(self, stop_event: threading.Event, db: AsyncIOMotorDatabase):
        """Inicializa o consumidor."""
        self.connection = None
        self.channel = None
        self._stop_event = stop_event
        self._db = db
        # Criamos um event loop para esta thread, para correr as operações async do DB
        self._loop = asyncio.new_event_loop()
        super().__init__(target=self.run, daemon=True)

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
        Descodifica o JSON, atualiza o estado global e faz o broadcast
        para os clientes WebSocket de forma thread-safe.
        """
        try:
            # 1. Descodificar a mensagem
            raw_data = json.loads(body.decode('utf-8'))

            # 2. Construir um documento genérico para o MongoDB.
            #    Isto torna o consumidor agnóstico à estrutura dos dados.
            #    Ele simplesmente guarda o que recebe.
            telemetry_doc = {
                "data": raw_data, # Guarda a carga útil original, seja lista ou objeto
                "timestampMs": properties.timestamp
            }

            # 3. Agendar a operação de escrita na base de dados na event loop principal.
            #    Não há validação; os dados são inseridos diretamente.
            asyncio.run_coroutine_threadsafe(save_telemetry_data(self._db, telemetry_doc), self._loop)
            logger.info("Mensagem recebida e agendada para ser guardada no MongoDB.")

        except json.JSONDecodeError:
            logger.error(f"Erro ao descodificar JSON: {body.decode('utf-8')}")
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        """
        O loop principal do consumidor, executado numa thread separada.
        Conecta-se ao RabbitMQ e entra num ciclo de consumo de mensagens
        até que o evento de paragem seja acionado.
        """
        asyncio.set_event_loop(self._loop) # Associa o loop a esta thread

        logger.info(f"Conectando ao RabbitMQ...")
        if not self._connect():
            return

        try:
            self.channel.basic_consume(queue=settings.QUEUE_NAME, on_message_callback=self._process_message)

            while not self._stop_event.is_set():
                self.connection.process_data_events(time_limit=1)
        except (pika.exceptions.StreamLostError, pika.exceptions.AMQPConnectionError) as e:
            logger.error(f"A ligação ao RabbitMQ foi perdida: {e}. A thread do consumidor vai terminar e tentar reconectar.")
            # The main application lifecycle should handle restarting the consumer thread if desired.
        if self.connection and self.connection.is_open:
            self.connection.close()
        logger.info("Thread do consumidor RabbitMQ encerrada.")
