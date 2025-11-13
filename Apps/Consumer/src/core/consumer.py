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
from pika.exceptions import AMQPConnectionError

from ..config import settings
from ..websockets.manager import websocket_manager
from .state import manager as app_state

logger = logging.getLogger('ConsumerMicroservice')

class RabbitMQConsumer:
    """Encapsula a lógica de consumo de mensagens do RabbitMQ."""

    def __init__(self, stop_event: threading.Event, main_loop: asyncio.AbstractEventLoop):
        """Inicializa o consumidor."""
        self.connection = None
        self.channel = None
        self._stop_event = stop_event
        self._main_loop = main_loop
        self.consumer_thread = threading.Thread(target=self.run, daemon=True)

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
            data = json.loads(body.decode('utf-8'))
            new_state = {
                "data": data,
                "timestamp_ms": properties.timestamp,
                "content_type": properties.content_type,
            }
            app_state.update_last_message(new_state)
            
            asyncio.run_coroutine_threadsafe(websocket_manager.broadcast(json.dumps(new_state)), self._main_loop)

            logger.info("Mensagem recebida e transmitida via WebSocket.")
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

    def start(self):
        """Inicia a thread do consumidor."""
        self.consumer_thread.start()
