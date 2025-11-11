import random
import pika
import json

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


    def main():
        import os
        import time

        rabbitmq_url = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')
        queue_name = os.environ.get('QUEUE_NAME', 'real_time_data')

        while True:
            try:
                connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
                channel = connection.channel()

                channel.queue_declare(queue=queue_name, durable=True)
                
                producer = Producer()
                
                while True:
                    data = producer.get_data()
                    message = json.dumps(data)
                    channel.basic_publish(exchange='',
                                            routing_key=queue_name,
                                            body=message)
                    print(f" [x] Sent {message}")
                    time.sleep(1)
            
            except pika.exceptions.AMQPConnectionError as e:
                print(f"Connection failed: {e}. Retrying in 5 seconds...")
                time.sleep(5)
            except Exception as e:
                print(f"An error occurred: {e}. Retrying in 5 seconds...")
                time.sleep(5)
            finally:
                if 'connection' in locals() and connection.is_open:
                    connection.close()
        
if __name__ == "__main__":
    Producer.main()
        
    
    