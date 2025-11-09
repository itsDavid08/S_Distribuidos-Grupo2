"""
Gestor de Conexões WebSocket.

Este módulo fornece a classe `ConnectionManager` para gerir o ciclo de vida
das conexões WebSocket ativas (conectar, desconectar) e para transmitir
mensagens para todos os clientes conectados.
"""
import logging
from fastapi import WebSocket
from typing import List

logger = logging.getLogger('RedpandaMicroservice')

class ConnectionManager:
    """Gere conexões WebSocket ativas."""
    def __init__(self):
        """Inicializa o gestor com uma lista vazia de conexões."""
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Aceita uma nova conexão WebSocket e adiciona-a à lista de conexões ativas."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Nova conexão WebSocket: {websocket.client}")

    def disconnect(self, websocket: WebSocket):
        """Remove uma conexão WebSocket da lista de conexões ativas."""
        self.active_connections.remove(websocket)
        logger.info(f"Conexão WebSocket fechada: {websocket.client}")

    async def broadcast(self, message: str):
        """Envia uma mensagem para todas as conexões WebSocket ativas."""
        for connection in self.active_connections:
            await connection.send_text(message)

# Instância única (singleton) do gestor para ser importada por outros módulos.
websocket_manager = ConnectionManager()
