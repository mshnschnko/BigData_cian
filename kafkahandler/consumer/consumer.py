from confluent_kafka import Consumer, KafkaError
import logging
import os

class KafkaConsumer:
    def __init__(self, topic_name, group_id="consumer-group"):
        # Получаем конфигурацию из переменных окружения
        kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

        # Конфигурация для Kafka Consumer
        self.consumer_config = {
            'bootstrap.servers': kafka_bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'  # Начинаем с самого начала, если нет смещения
        }

        # Инициализируем Consumer
        self.consumer = Consumer(self.consumer_config)
        self.topic_name = topic_name
        self.consumer.subscribe([self.topic_name])

    def consume_messages(self):
        try:
            while True:
                msg = self.consumer.poll(1.0)  # Ожидание сообщения (1 секунда)
                
                if msg is None:
                    continue  # Нет нового сообщения, продолжаем ожидание
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        logging.info(f"Достигнут конец раздела {msg.topic()} [{msg.partition()}] при оффсете {msg.offset()}")
                    else:
                        logging.error(f"Ошибка при получении сообщения: {msg.error()}")
                    continue

                # Обрабатываем сообщение
                logging.info(f"Получено сообщение: {msg.value().decode('utf-8')}")
                
        except Exception as e:
            logging.error(f"Ошибка в Consumer: {e}")
        finally:
            self.consumer.close()
            logging.info("Consumer закрыт")
