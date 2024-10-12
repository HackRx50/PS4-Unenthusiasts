import pika
import uuid

class MessageQueueService:
    def __init__(self, queue_name: str, host: str):
        self.queue_name = queue_name
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host,credentials=pika.PlainCredentials('admin', 'admin')))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)


    def publish_message(self, message: str,msg_id:str):
        print(f"Publishing message: {message}",msg_id)
        # msg_id = str(uuid.uuid4())
        print(msg_id)
        properties = pika.BasicProperties(message_id=msg_id)
        self.channel.basic_publish(exchange='', routing_key=self.queue_name, body=message, properties=properties)
        print(f"Message published: {message}")
        # self.channel.basic_publish(exchange='', routing_key=self.queue_name, body=message)

    def consume_message(self, callback):
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=callback)
        self.channel.start_consuming()
