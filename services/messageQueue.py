import pika

class MessageQueueService:
    def __init__(self, queue_name: str, host: str):
        self.queue_name = queue_name
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host,credentials=pika.PlainCredentials('admin', 'admin')))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)


    def publish_message(self, message: str):
        self.channel.basic_publish(exchange='', routing_key=self.queue_name, body=message)

    def consume_message(self, callback):
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=callback)
        self.channel.start_consuming()
