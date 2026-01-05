import os
import random
import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from metrics import start_metrics_server, REQUESTS_TOTAL, REQUEST_LATENCY, DB_CONNECTION_STATUS

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    # Inicia o servidor de métricas na porta 8001
    start_metrics_server(8001)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    REQUEST_LATENCY.labels(endpoint=request.url.path).observe(process_time)
    REQUESTS_TOTAL.labels(
        method=request.method, 
        endpoint=request.url.path, 
        status_code=response.status_code
    ).inc()
    
    return response

MONGO_HOST = os.getenv("MONGO_HOST", "mongo-service")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASS = os.getenv("MONGO_PASS")
DB_NAME = os.getenv("DB_NAME", "projeto_sd")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "dados_corrida")
MONGO_AUTH_SOURCE = os.getenv("MONGO_AUTH_SOURCE", "admin")  # importante para usuario root

try:
    uri = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{DB_NAME}?authSource={MONGO_AUTH_SOURCE}"
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    # Verifica conectividade
    client.admin.command("ping")
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    DB_CONNECTION_STATUS.set(1)
    logger.info(f"Ligado ao MongoDB (BD: {DB_NAME}, Coleção: {COLLECTION_NAME})!")
except Exception as e:
    DB_CONNECTION_STATUS.set(0)
    logger.error(f"Erro ao ligar ao MongoDB: {e}")
    raise

def gerar_dados_random(num_participantes=5):
    """
    Gera dados aleatórios de corredores para testes.
    Retorna uma lista de participantes com id, posições e velocidades.
    """
    participantes = []
    for i in range(1, num_participantes + 1):
        participantes.append({
            "id": i,
            "positionX": random.randint(0, 99),
            "positionY": random.randint(0, 99),
            "speedX": random.randint(0, 99),
            "speedY": random.randint(0, 99)
        })
    return participantes

@app.get("/dados")
def get_dados():
    """
    Devolve dados de corredores.
    Se a DB estiver vazia, gera dados aleatórios.
    """
    try:
        # Tenta obter dados reais da DB ordenados por timestamp (mais recentes primeiro)
        participantes = list(collection.find({}, {
            "runner_id": 1,
            "route_id": 1,
            "positionX": 1,
            "positionY": 1,
            "speedX": 1,
            "speedY": 1,
            "timestampMs": 1,
            "_id": 0
        }).sort("timestampMs", -1).limit(100))
        
        # Se não houver dados, gera aleatórios
        if not participantes:
            participantes = gerar_dados_random(5)
            logger.info("Nenhum dado na BD. A gerar dados aleatórios...")
        
        return {"participantes": participantes}
    except Exception as e:
        # Em caso de erro de conexão com DB, retorna dados aleatórios
        logger.error(f"Erro ao aceder à BD: {e}. A usar dados aleatórios.")
        return {"participantes": gerar_dados_random(5)}

@app.get("/rutas")
def get_rutas():
    """
    Devolve todas as rutas predefinidas.
    Estas são as mesmas rotas que os corredores usam.
    """
    rutas = [
        {"id": 1, "points": [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]], "name": "Ruta Cuadrada"},
        {"id": 2, "points": [[0, 0], [15, 10], [16, -17], [-20, -15]], "name": "Ruta Irregular"},
        {"id": 3, "points": [[-5, -5], [10, 3], [15, 12], [22, 13]], "name": "Ruta Ascendente"}
    ]
    return {"rutas": rutas}

@app.get("/corredor/{runner_id}")
def get_corredor(runner_id: int):
    """
    Devolve a última posição de um corredor específico.
    """
    try:
        corredor = collection.find_one(
            {"runner_id": runner_id},
            {"runner_id": 1, "route_id": 1, "positionX": 1, "positionY": 1, "speedX": 1, "speedY": 1, "timestampMs": 1, "_id": 0},
            sort=[("timestampMs", -1)]  # Ordena por timestamp descendente
        )
        
        # Se não encontrar na DB, gera dados aleatórios para esse corredor
        if not corredor:
            corredor = {
                "runner_id": runner_id,
                "positionX": random.randint(0, 99),
                "positionY": random.randint(0, 99),
                "speedX": random.randint(0, 99),
                "speedY": random.randint(0, 99)
            }
            logger.info(f"Corredor {runner_id} não encontrado. A gerar dados aleatórios...")
        
        return corredor
    except Exception as e:
        return {"erro": str(e)}