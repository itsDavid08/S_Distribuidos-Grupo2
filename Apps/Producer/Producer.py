import os
import math
import random
import pika
import json
import time
import logging
import threading
from prometheus_client import start_http_server
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from Metrics import (
    MESSAGES_CREATED,
    CREATION_TIME,
    LAST_MESSAGE_TIMESTAMP
)

# Parâmetros fixos para aumentar velocidade (ajuste aqui se precisar mais/menos)
SLEEP_SECONDS = 0.1        # intervalo entre mensagens
MAX_STEPS_PER_SEGMENT = 1000  # impede passos minúsculos que parecem posição parada

# Rotas pre-definidas na Madeira (Latitude, Longitude)
ROUTES = [
    # Rota 1
    [
        (0 , 0),
        (10, 0),
        (10, 10),
        (0 , 10),
        (0 , 0)
    ],
    # Rota 2
    [
        (0, 0), 
        (15, 10),
        (16, -17),
        (-20, -15)
    ],
    # Rota 3
    [
        (-5, -5),
        (10, 3), 
        (15, 12),
        (22, 13)
    ]
]

class Producer:
    def __init__(self):
        self.positionX = 0.0
        self.positionY = 0.0
        self.speedX = 0.0
        self.speedY = 0.0

        # Usar siempre un ID aleatorio; ignorar RUNNER_ID para evitar conversiones inválidas
        self.runner_id = random.randint(1, 2_147_483_647)
        
        # Configuração da corrida
        self.current_route = []
        self.current_segment = 0
        self.steps_per_segment = 0
        self.current_step = 0
        self.target_speed_kmh = 0 # Velocidade alvo para esta corrida
        
        self.start_new_race()

    def start_new_race(self):
        self.current_route = random.choice(ROUTES)
        self.current_segment = 0
        self.current_step = 0
        
        # Velocidade aumentada (60-100 km/h) para garantir < 5 min e movimento visível
        self.target_speed_kmh = random.uniform(60, 100)
        
        # Calcular passos necessários para o primeiro segmento com base na velocidade
        self._calculate_segment_steps()

        # Posição inicial (X=Latitude, Y=Longitude) para compatibilidade com Leaflet
        # ROUTES é lista de (Lat, Long) -> p[0]=Lat, p[1]=Long
        self.positionX = self.current_route[0][0]
        self.positionY = self.current_route[0][1]
        
        logging.info(f"Runner {self.runner_id} started. Target Speed: {self.target_speed_kmh:.2f} km/h")

    def _calculate_segment_steps(self):
        """Calcula quantos passos são necessários para percorrer o segmento atual à velocidade alvo."""
        if self.current_segment >= len(self.current_route) - 1:
            return

        p1 = self.current_route[self.current_segment]
        p2 = self.current_route[self.current_segment + 1]
        
        # Distância Euclidiana aproximada em graus
        # 1 grau de latitude ~= 111 km
        d_lat = p2[0] - p1[0]
        d_lon = p2[1] - p1[1]
        dist_deg = math.sqrt(d_lat**2 + d_lon**2)
        dist_km = dist_deg * 111.0
        
        # Velocidade em km/s (km/h / 3600)
        speed_kms = self.target_speed_kmh / 3600.0
        
        # Tempo necessário para percorrer o segmento (em segundos)
        if speed_kms > 0:
            duration_seconds = dist_km / speed_kms
        else:
            duration_seconds = 1
            
        # Número de passos = Duração / Tempo por passo (SLEEP_SECONDS)
        # Garante pelo menos 1 passo para evitar divisão por zero
        steps = max(1, int(duration_seconds / SLEEP_SECONDS))
        self.steps_per_segment = min(steps, MAX_STEPS_PER_SEGMENT)

    def update_physics(self):
        # Verificar se a corrida acabou
        if self.current_segment >= len(self.current_route) - 1:
            self.start_new_race()
            return

        # Pontos do segmento atual
        p1 = self.current_route[self.current_segment]
        p2 = self.current_route[self.current_segment + 1]

        # Interpolação linear (limitada para evitar extrapolação quando chegamos ao fim)
        t = min(1.0, self.current_step / float(self.steps_per_segment))
        
        # Calcular Lat/Lon atuais
        lat = p1[0] + (p2[0] - p1[0]) * t
        lon = p1[1] + (p2[1] - p1[1]) * t
        
        # Atribuição: X=Latitude, Y=Longitude (Para compatibilidade direta com Leaflet [Lat, Lon])
        new_x = lat
        new_y = lon

        # Atualizar velocidade (graus por tick) 
        # Multiplicado por 100.000 para ser legível na tabela da UI (ex: 2.5 em vez de 0.000025)
        self.speedX = (new_x - self.positionX) * 100000
        self.speedY = (new_y - self.positionY) * 100000
        
        # Atualizar posição para o ponto exato da rota
        self.positionX = new_x
        self.positionY = new_y

        self.current_step += 1
        
        # Avançar segmento se necessário
        if self.current_step >= self.steps_per_segment:
            self.current_segment += 1
            self.current_step = 0
            self._calculate_segment_steps()

    def get_data(self):
        self.update_physics()
        data = {
            "runner_id": self.runner_id,
            "positionX": self.positionX,
            "positionY": self.positionY,
            "speedX": self.speedX,
            "speedY": self.speedY,
            "timestampMs": int(time.time() * 1000)
        }
        return data
    
    def connect_rabbitmq(self):
        """Establishes a connection to RabbitMQ with retry logic."""
        user = os.getenv("RABBITMQ_USER", "guest")
        password = os.getenv("RABBITMQ_PASS", "guest")
        host = os.getenv("RABBITMQ_HOST", "localhost")
        
        while True:
            try:
                logging.info(f"Connecting to RabbitMQ at {host}...")
                credentials = pika.PlainCredentials(user, password)
                parameters = pika.ConnectionParameters(host, 5672, '/', credentials)
                connection = pika.BlockingConnection(parameters)
                logging.info("Successfully connected to RabbitMQ.")
                return connection
            except pika.exceptions.AMQPConnectionError as e:
                logging.error(f"Failed to connect to RabbitMQ: {e}. Retrying in 5 seconds...")
                time.sleep(5)


if __name__ == "__main__":
    # ADICIONA ISTO: Inicia o servidor de métricas na porta 8001
    def start_metrics():
        start_http_server(8001)
        logging.info("Servidor de métricas Prometheus iniciado na porta 8001")
    
    # Inicia o servidor numa thread separada
    metrics_thread = threading.Thread(target=start_metrics, daemon=True)
    metrics_thread.start()
    
    producer = Producer()
    connection = None
    channel = None
    queue_name = os.getenv("QUEUE_NAME", "queue")
    
    while True:
        try:
            if not connection or connection.is_closed:
                connection = producer.connect_rabbitmq()
                channel = connection.channel()
                channel.queue_declare(queue=queue_name, durable=True)

            with CREATION_TIME.time():
                message_data = producer.get_data()
                message_body = json.dumps(message_data)
            
                properties = pika.BasicProperties(
                    content_type='application/json',
                    delivery_mode=2, # make message persistent
                    timestamp=int(time.time() * 1000)
                )

                channel.basic_publish(
                    exchange='',
                    routing_key=queue_name,
                    body=message_body,
                    properties=properties
                )
            MESSAGES_CREATED.inc()
            LAST_MESSAGE_TIMESTAMP.set(time.time())
            
            logging.info(f"Sent message: {message_body}")

        except pika.exceptions.AMQPConnectionError as e:
            logging.error(f"Connection lost: {e}. Reconnecting...")
            if connection and not connection.is_closed:
                connection.close()
            connection = None # Force reconnection in the next loop
            time.sleep(5) # Wait before trying to reconnect
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            # Close connection on other errors as well to be safe
            if connection and not connection.is_closed:
                connection.close()
            connection = None
            time.sleep(5)
            
        time.sleep(SLEEP_SECONDS)
