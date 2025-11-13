import os
import random
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
        # Tenta obter dados reais da DB
        participantes = list(collection.find({}, {
            "id": 1,
            "positionX": 1,
            "positionY": 1,
            "speedX": 1,
            "speedY": 1,
            "_id": 0
        }).sort("_id", -1).limit(20))
        
        # Se não houver dados, gera aleatórios
        if not participantes:
            participantes = gerar_dados_random(5)
            print("Nenhum dado na BD. A gerar dados aleatórios...")
        
        return {"participantes": participantes}
    except Exception as e:
        # Em caso de erro de conexão com DB, retorna dados aleatórios
        print(f"Erro ao aceder à BD: {e}. A usar dados aleatórios.")
        return {"participantes": gerar_dados_random(5)}

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
        
        # Se não encontrar na DB, gera dados aleatórios para esse corredor
        if not corredor:
            corredor = {
                "id": runner_id,
                "positionX": random.randint(0, 99),
                "positionY": random.randint(0, 99),
                "speedX": random.randint(0, 99),
                "speedY": random.randint(0, 99)
            }
            print(f"Corredor {runner_id} não encontrado. A gerar dados aleatórios...")
        
        return corredor
    except Exception as e:
        return {"erro": str(e)}