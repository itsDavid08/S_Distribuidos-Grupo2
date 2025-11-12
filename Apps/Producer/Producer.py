import os
import random
import pika
import json
import time


class Producer:
    def __init__(self):
        self.positionX = 0
        self.positionY = 0
        self.speedX = 0
        self.speedY = 0

    def get_position(self):
        self.positionX = random.randint(0, 99)
        self.positionY = random.randint(0, 99)

    def get_speed(self):
        self.speedX = random.randint(0, 99)
        self.speedY = random.randint(0, 99)

    def get_data(self):
        self.get_position()
        self.get_speed()
        data = [self.positionX, self.positionY, self.speedX, self.speedY]
        return data
    
    def connect_rabbitmq(self):
        url = os.getenv("RABBITMQ_URL", "amqp://localhost")
        user = os.getenv("RABBITMQ_USER", "guest")
        password = os.getenv("RABBITMQ_PASS", "guest")

        # Monta os parâmetros de conexão
        credentials = pika.PlainCredentials(user, password)
        parameters = pika.ConnectionParameters(host=url.replace("amqp://", ""), credentials=credentials)
        return pika.BlockingConnection(parameters)

class Main:    

    def main():
        producer = Producer()
        connection = producer.connect_rabbitmq()
        channel = connection.channel()
        
        queue_name = 'queue'
        channel.queue_declare(queue=queue_name)
        
        
        
        message = json.dumps(producer.get_data())
        channel.basic_publish(exchange='',
                                routing_key=queue_name,
                                body=message)
        print(f" [x] Sent {message}")
        
        connection.close()
        
if __name__ == "__main__":
    while True:
        try:
            Main.main()
        except Exception as e:
            print(f"An error occurred: {e}")
        time.sleep(5)
        
    
