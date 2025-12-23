"""
Módulo do Repositório de Dados.

Este módulo centraliza toda a lógica de interação com a base de dados MongoDB,
seguindo as melhores práticas de separação de responsabilidades.
"""
import logging
from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..config import settings

logger = logging.getLogger('ConsumerMicroservice.Repository')


async def save_telemetry_data(db: AsyncIOMotorDatabase, data: Dict[str, Any]):
    """
    Guarda um documento de dados na coleção 'telemetry'.
    Esta função não realiza validação; ela simplesmente insere o dicionário
    de dados recebido.

    Args:
        db: A instância da base de dados Motor.
        data: O dicionário de dados a ser guardado.
    """
    collection = db.get_collection(settings.COLLECTION_NAME)
    try:
        await collection.insert_one(data)
        logger.info(f"Dados de telemetria guardados no MongoDB: {data}")
    except Exception as e:
        logger.error(f"Erro ao guardar dados no MongoDB: {e}")
        logger.debug(f"Dados que falharam ao guardar: {data}")