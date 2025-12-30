import os
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
STEPS_PER_SEGMENT = 20      # menos passos por segmento => saltos maiores
SLEEP_SECONDS = 1        # intervalo entre mensagens
SPEED_BOOST = 10.0       # multiplica o delta de posição para aumentar a velocidade aparente

# Rotas pre-definidas na Madeira (Latitude, Longitude)
ROUTES = [
    # Rota 1: Funchal (Lido -> Marina -> Zona Velha)
    [
        (32.6370, -16.9350),
        (32.6390, -16.9280),
        (32.6420, -16.9180),
        (32.6470, -16.9080),
        (32.6480, -16.8990)
    ],
    # Rota 2: Pico do Arieiro -> Pico Ruivo
    [
        (32.7350, -16.9280),
        (32.7420, -16.9320),
        (32.7500, -16.9380),
        (32.7590, -16.9420)
    ],
    # Rota 3: Ponta de São Lourenço
    [
        (32.7430, -16.7020),
        (32.7450, -16.6950),
        (32.7480, -16.6880),
        (32.7500, -16.6820)
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
        self.steps_per_segment = STEPS_PER_SEGMENT  # Passos para interpolar entre pontos
        self.current_step = 0
        
        self.start_new_race()

    def start_new_race(self):
        self.current_route = random.choice(ROUTES)
        self.current_segment = 0
        self.current_step = 0
        # Posição inicial
        self.positionX = self.current_route[0][0]
        self.positionY = self.current_route[0][1]
        logging.info(f"Runner {self.runner_id} started new race.")

    def update_physics(self):
        # Verificar se a corrida acabou
        if self.current_segment >= len(self.current_route) - 1:
            self.start_new_race()
            return

        # Pontos do segmento atual
        p1 = self.current_route[self.current_segment]
        p2 = self.current_route[self.current_segment + 1]

        # Interpolação linear
        t = self.current_step / float(self.steps_per_segment)
        new_x = p1[0] + (p2[0] - p1[0]) * t
        new_y = p1[1] + (p2[1] - p1[1]) * t

        # Atualizar velocidade (delta) e aplicar boost
        self.speedX = (new_x - self.positionX) * SPEED_BOOST
        self.speedY = (new_y - self.positionY) * SPEED_BOOST
        # Atualizar posição usando o delta amplificado
        self.positionX += self.speedX
        self.positionY += self.speedY

        self.current_step += 1
        
        # Avançar segmento se necessário
        if self.current_step > self.steps_per_segment:
            self.current_segment += 1
            self.current_step = 0

    def get_data(self):
        self.update_physics()
        data = [self.runner_id, self.positionX, self.positionY, self.speedX, self.speedY]
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
