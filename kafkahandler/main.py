import logging

from consumer.consumer import KafkaConsumer

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('kafkahandler.log', mode='a'),
                        logging.StreamHandler()
                    ])

if __name__ == "__main__":
    # Инициализация Consumer для указанного топика
    consumer = KafkaConsumer(topic_name="your_topic_name")
    consumer.consume_messages()