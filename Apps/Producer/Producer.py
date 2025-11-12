import os
import random
import pika
import json
import time
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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
        """Establishes a connection to RabbitMQ with retry logic."""
        rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
        
        while True:
            try:
                logging.info(f"Connecting to RabbitMQ at {rabbitmq_url}...")
                parameters = pika.URLParameters(rabbitmq_url)
                connection = pika.BlockingConnection(parameters)
                logging.info("Successfully connected to RabbitMQ.")
                return connection
            except pika.exceptions.AMQPConnectionError as e:
                logging.error(f"Failed to connect to RabbitMQ: {e}. Retrying in 5 seconds...")
                time.sleep(5)


if __name__ == "__main__":
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
            
        time.sleep(5)
