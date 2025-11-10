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
        connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
        channel = connection.channel()
        
        queue_name = 'queue'
        channel.queue_declare(queue=queue_name)
        
        producer = Producer()
        
        data = producer.get_data()
        message = json.dumps(data)
        channel.basic_publish(exchange='',
                                routing_key=queue_name,
                                body=message)
        print(f" [x] Sent {message}")
        
        connection.close()
        
if __name__ == "__main__":
    Producer.main()
        
    
    