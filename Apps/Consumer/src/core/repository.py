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
    collection = db[settings.COLLECTION_NAME]
    await collection.insert_one(data)
    logger.info(f"Dados guardados em {settings.DB_NAME}.{settings.COLLECTION_NAME}: {data}")