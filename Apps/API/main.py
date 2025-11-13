import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URL = os.getenv("MONGO_URL", "mongo-service")
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASS = os.getenv("MONGO_PASS")
DB_NAME = os.getenv("DB_NAME", "projeto_sd")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "dados_corrida")

try:
    client = MongoClient(f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_URL}:27017/")
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    print(f"Ligado ao MongoDB (BD: {DB_NAME}, Coleção: {COLLECTION_NAME})!")
except Exception as e:
    print(f"Erro ao ligar ao MongoDB: {e}")
    raise

@app.get("/dados")
def get_dados():
    """
    Devolve os 20 registos mais recentes de todos os corredores.
    """
    try:
        participantes = list(collection.find({}, {
            "id": 1,
            "positionX": 1,
            "positionY": 1,
            "speedX": 1,
            "speedY": 1,
            "_id": 0
        }).sort("_id", -1).limit(20))
        
        return {"participantes": participantes}
    except Exception as e:
        return {"erro": str(e)}

@app.get("/corredor/{runner_id}")
def get_corredor(runner_id: int):
    """
    Devolve a última posição de um corredor específico.
    """
    try:
        corredor = collection.find_one(
            {"id": runner_id},
            {"id": 1, "positionX": 1, "positionY": 1, "speedX": 1, "speedY": 1, "_id": 0},
            sort=[("_id", -1)]
        )
        return corredor if corredor else {"erro": "Corredor não encontrado"}
    except Exception as e:
        return {"erro": str(e)}