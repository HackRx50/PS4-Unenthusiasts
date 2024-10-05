import pika

class MessageQueueService:
    def __init__(self, queue_name: str, host: str):
        self.queue_name = queue_name
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()

    def publish_message(self, message: str):
        self.channel.basic_publish(exchange='', routing_key=self.queue_name, body=message)

    def consume_message(self, callback):
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()
