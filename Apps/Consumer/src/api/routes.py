from fastapi import APIRouter, Response, status

from ..core.state import manager as state_manager
from ..websockets.manager import websocket_manager
from ..config import settings

router = APIRouter()

@router.get("/latest-data")
async def get_latest_data(response: Response):
    """Endpoint para retornar o último estado lido."""
    latest_data = state_manager.get_last_message()
    # Se ainda não recebemos dados, o estado terá a chave 'status'
    if "status" in latest_data:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return latest_data

@router.get("/health")
async def health_check():
    """"Health" Check para verificar o estado do serviço."""
    return {"status": "UP", "consumer_group": settings.GROUP_ID}