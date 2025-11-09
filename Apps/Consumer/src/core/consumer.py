"""
Módulo do Consumidor Redpanda.

Este módulo define a classe `RedpandaConsumer`, responsável por se conectar
ao Redpanda, consumir mensagens de um tópico específico, processá-las e
transmiti-las para os clientes WebSocket conectados.
"""
import asyncio
import json
import logging
import threading
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

from ..config import REDPANDA_BROKERS, TOPIC_NAME, GROUP_ID
from ..websockets.manager import websocket_manager
from .state import app_state

logger = logging.getLogger('RedpandaMicroservice')

class RedpandaConsumer:
    """Encapsula a lógica de consumo de mensagens do Redpanda."""

    def __init__(self, stop_event: threading.Event, main_loop: asyncio.AbstractEventLoop):
        """Inicializa o consumidor."""
        self.consumer = None
        self._stop_event = stop_event
        self._main_loop = main_loop
        self.consumer_thread = threading.Thread(target=self.run, daemon=True)

    def _connect(self):
        """Tenta conectar-se ao Redpanda."""
        try:
            # Tenta estabelecer a conexão com o broker Kafka/Redpanda.
            # Define um timeout para evitar bloqueio infinito na inicialização
            # se o broker não estiver disponível.
            self.consumer = KafkaConsumer(
                TOPIC_NAME,
                bootstrap_servers=REDPANDA_BROKERS,
                auto_offset_reset='latest',
                group_id=GROUP_ID,
                value_deserializer=lambda x: x.decode('utf-8'),
                consumer_timeout_ms=1000
            )
            logger.info(f"Consumidor Redpanda conectado e subscrito à topic: {TOPIC_NAME}")
            return True
        except NoBrokersAvailable:
            logger.error(f"Não foi possível conectar ao Redpanda em {REDPANDA_BROKERS}. O consumidor não será iniciado.")
            return False

    def _process_message(self, message):
        """
        Processa uma única mensagem recebida do Redpanda.
        Descodifica o JSON, atualiza o estado global e faz o broadcast
        para os clientes WebSocket de forma thread-safe.
        """
        try:
            data = json.loads(message.value)
            new_state = {
                "data": data,
                "timestamp_ms": message.timestamp,
                "topic": message.topic,
                "partition": message.partition
            }
            app_state.update_last_message(new_state)
            
            # Submete a corrotina de broadcast para o loop de eventos principal
            # da aplicação de forma segura a partir da thread do consumidor.
            future = asyncio.run_coroutine_threadsafe(websocket_manager.broadcast(json.dumps(new_state)), self._main_loop)
            future.result()  # Espera pela conclusão para garantir o envio

            logger.info(f"Mensagem recebida e transmitida via WebSocket. Partição: {message.partition}")
        except json.JSONDecodeError:
            logger.error(f"Erro ao descodificar JSON: {message.value}")
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")

    def run(self):
        """
        O loop principal do consumidor, executado numa thread separada.
        Conecta-se ao Redpanda e entra num ciclo de consumo de mensagens
        até que o evento de paragem seja acionado.
        """
        logger.info(f"Conectando ao Redpanda em {REDPANDA_BROKERS}...")
        if not self._connect():
            return

        while not self._stop_event.is_set():
            for message in self.consumer:
                if self._stop_event.is_set():
                    break
                self._process_message(message)
            
            self._stop_event.wait(0.1)

        if self.consumer:
            self.consumer.close()
        logger.info("Thread do consumidor Redpanda encerrada.")

    def start(self):
        """Inicia a thread do consumidor."""
        self.consumer_thread.start()
