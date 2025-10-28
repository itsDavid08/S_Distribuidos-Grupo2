import time
from ..websockets.manager import ConnectionManager

# --- Armazenamento e Gestor de Conexões ---

# Estado da última mensagem recebida do Redpanda
LAST_MESSAGE_STATE = {"status": "Aguardando dados de Redpanda...", "timestamp": int(time.time() * 1000)}

# Gestor de conexões WebSocket
manager = ConnectionManager()

def update_last_message(new_state: dict):
    global LAST_MESSAGE_STATE
    LAST_MESSAGE_STATE = new_state
