import time
import threading
import copy
from typing import Any, Dict

class StateManager:
    """
    Gestor de estado thread-safe para armazenar a última mensagem recebida.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._last_message: Dict[str, Any] = {
            "status": "Aguardando dados...",
            "timestamp": int(time.time() * 1000)
        }

    def update_last_message(self, new_state: Dict[str, Any]):
        """Atualiza o estado da última mensagem de forma segura."""
        with self._lock:
            self._last_message = new_state

    def get_last_message(self) -> Dict[str, Any]:
        """Obtém o estado da última mensagem de forma segura."""
        with self._lock:
            return copy.deepcopy(self._last_message)

# Instância única do gestor de estado
manager = StateManager()
