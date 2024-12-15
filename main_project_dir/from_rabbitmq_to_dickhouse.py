import pika
import json
from clickhouse_driver import Client as ClickHouseClient
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройки RabbitMQ
rabbitmq_host = '31.134.161.250'
rabbitmq_user = 'rmuser'
rabbitmq_password = 'rmpassword'
rabbitmq_queue = 'test'

credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
connection_params = pika.ConnectionParameters(rabbitmq_host, 5672, '/', credentials)
connection = pika.BlockingConnection(connection_params)
channel = connection.channel()

channel.queue_declare(queue=rabbitmq_queue)

# Настройки ClickHouse
clickhouse_client = ClickHouseClient(
    host='31.134.161.250',
    port=9000,
    user='default',
    password='',
    database='default'
)


def insert_data(table_name, data):
    """Вставляет данные в указанную таблицу."""
    if not data:
        return

    batch_size = 1000  # Размер пакета для вставки
    query = f"""
    INSERT INTO {table_name} ({', '.join(data[0].keys())})
    VALUES
    """
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        values = ", ".join([f"('{row['company_id']}', '{row['timestamp']}', {row['open']}, {row['high']}, {row['low']}, {row['close']}, {row['volume']})" if table_name == 'candles' else
                            f"('{row['company_id']}', '{row['timestamp']}', {row['price']}, {row['volume']}, '{row['side']}')" if table_name == 'trades' else
                            f"('{row['company_id']}', '{row['timestamp']}', {row['bid_price']}, {row['bid_volume']}, {row['ask_price']}, {row['ask_volume']})" for row in batch])
        clickhouse_client.execute(query + values)


def callback(ch, method, properties, body):
    """Обработчик сообщений из RabbitMQ."""
    message = json.loads(body)
    if 'open' in message:
        insert_data('candles', [message])
    elif 'side' in message:
        insert_data('trades', [message])
    elif 'bid_price' in message:
        insert_data('order_book', [message])
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    channel.basic_consume(queue=rabbitmq_queue, on_message_callback=callback, auto_ack=False)
    logger.info('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == "__main__":
    main()
