import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Response, status

from ..core.state import manager, LAST_MESSAGE_STATE
from ..config import GROUP_ID

router = APIRouter()

@router.get("/latest-data")
async def get_latest_data(response: Response):
    """Endpoint para retornar o último estado lido."""
    # Se ainda não recebemos dados, o estado terá a chave 'status'
    if "status" in LAST_MESSAGE_STATE:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return LAST_MESSAGE_STATE

@router.get("/health")
async def health_check():
    """"Health" Check para verificar o estado do serviço."""
    return {"status": "UP", "consumer_group": GROUP_ID}

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Endpoint WebSocket para receber dados em tempo real."""
    await manager.connect(websocket)
    try:
        # Envia o último estado conhecido assim que o cliente se conecta
        await websocket.send_text(json.dumps(LAST_MESSAGE_STATE))
        while True:
            # Mantém a conexão aberta para receber possíveis mensagens do cliente
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)