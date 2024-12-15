import os
from datetime import timedelta, datetime
from tqdm import tqdm
from tinkoff.invest import CandleInterval, Client
from tinkoff.invest.utils import now
from config import TOKEN
from clickhouse_driver import Client as ClickHouseClient
import time
import logging


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

clickhouse_client = ClickHouseClient(
    host='31.134.161.250',
    port=9000,
    user='default',
    password='',
    database='default'
)


def get_all_companies(client) -> list:
    """Получает все компании (акции) доступные через API."""
    shares = client.instruments.shares()
    return shares.instruments


def get_candles(figi, client, interval=CandleInterval.CANDLE_INTERVAL_HOUR, start_date=None, end_date=None):
    """Получает исторические данные свечей для заданного FIGI за указанный период."""
    if start_date is None:
        start_date = now() - timedelta(days=365 * 1)  # По умолчанию за последние 5 лет
    if end_date is None:
        end_date = now()

    candles = []
    current_date = start_date

    while current_date < end_date:
        next_date = min(current_date + timedelta(days=30), end_date)  # Запрос данных за 30 дней
        retries = 3
        while retries > 0:
            try:
                candles_chunk = client.get_all_candles(
                    figi=figi,
                    from_=current_date,
                    to=next_date,
                    interval=interval,
                )
                candles.extend(candles_chunk)
                current_date = next_date  # Переходим к следующему периоду только после успешного запроса
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                retries -= 1
                if retries == 0:
                    reset_time = getattr(e, 'metadata', {}).ratelimit_reset
                    logger.warning(f"Rate limit exceeded. Waiting for {reset_time} seconds.")
                    time.sleep(reset_time)
                else:
                    time.sleep(1)  # Задержка перед повторной попыткой

    return candles


def get_last_trades(figi, client, start_date=None, end_date=None):
    """Получает последние сделки для заданного FIGI за указанный период."""
    if start_date is None:
        start_date = now() - timedelta(days=365 * 1)  # По умолчанию за последние 5 лет
    if end_date is None:
        end_date = now()

    last_trades = []
    current_date = start_date

    while current_date < end_date:
        next_date = min(current_date + timedelta(days=30), end_date)  # Запрос данных за 30 дней
        retries = 3
        while retries > 0:
            try:
                trades_chunk = client.market_data.get_last_trades(
                    figi=figi,
                    from_=current_date,
                    to=next_date
                )
                last_trades.extend(trades_chunk.trades)
                current_date = next_date  # Переходим к следующему периоду только после успешного запроса
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                retries -= 1
                if retries == 0:
                    reset_time = getattr(e, 'metadata', {}).ratelimit_reset
                    logger.warning(f"Rate limit exceeded. Waiting for {reset_time} seconds.")
                    time.sleep(reset_time)
                else:
                    time.sleep(1)  # Задержка перед повторной попыткой

    return last_trades


def get_close_prices(figi, client, start_date=None, end_date=None):
    """Получает исторические данные цен закрытия для заданного FIGI за указанный период."""
    if start_date is None:
        start_date = now() - timedelta(days=365 * 1)  # По умолчанию за последние 5 лет
    if end_date is None:
        end_date = now()

    close_prices = []
    current_date = start_date

    while current_date < end_date:
        next_date = min(current_date + timedelta(days=30), end_date)  # Запрос данных за 30 дней
        retries = 3
        while retries > 0:
            try:
                candles_chunk = client.market_data.get_candles(
                    figi=figi,
                    from_=current_date,
                    to=next_date,
                    interval=CandleInterval.CANDLE_INTERVAL_DAY
                )
                close_prices.extend([candle.close.units + candle.close.nano / 1e9 for candle in candles_chunk.candles])
                current_date = next_date  # Переходим к следующему периоду только после успешного запроса
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                retries -= 1
                if retries == 0:
                    reset_time = getattr(e, 'metadata', {}).ratelimit_reset
                    logger.warning(f"Rate limit exceeded. Waiting for {reset_time} seconds.")
                    time.sleep(reset_time)
                else:
                    time.sleep(1)  # Задержка перед повторной попыткой

    return close_prices


def get_order_book(figi, client, depth=20):
    """Получает стакан заявок для заданного FIGI."""
    retries = 3
    while retries > 0:
        try:
            order_book = client.market_data.get_order_book(
                figi=figi,
                depth=depth
            )
            return order_book
        except Exception as e:
            logger.error(f"Error: {e}")
            retries -= 1
            if retries == 0:
                reset_time = getattr(e, 'metadata', {}).ratelimit_reset
                logger.warning(f"Rate limit exceeded. Waiting for {reset_time} seconds.")
                time.sleep(reset_time)
            else:
                time.sleep(1)  # Задержка перед повторной попыткой
    return None


def insert_company(figi, name, ticker):
    """Вставляет информацию о компании в таблицу companies."""
    name = name.replace("'", "''")  # Замена кавычек на подчеркивания
    query = """
    INSERT INTO companies (company_id, name, ticker)
    VALUES
    """
    values = f"('{figi}', '{name}', '{ticker}')"
    clickhouse_client.execute(query + values)


def candles_to_dict(figi, candles):
    """Преобразует данные свечей в словари."""
    return [
        {
            'company_id': figi,
            'timestamp': candle.time.strftime('%Y-%m-%d %H:%M:%S'),
            'open': candle.open.units + candle.open.nano / 1e9,
            'high': candle.high.units + candle.high.nano / 1e9,
            'low': candle.low.units + candle.low.nano / 1e9,
            'close': candle.close.units + candle.close.nano / 1e9,
            'volume': candle.volume
        }
        for candle in candles
    ]


def trades_to_dict(figi, trades):
    """Преобразует данные сделок в словари."""
    return [
        {
            'company_id': figi,
            'timestamp': trade.time.strftime('%Y-%m-%d %H:%M:%S'),
            'price': trade.price.units + trade.price.nano / 1e9,
            'volume': trade.quantity,
            'side': 'buy' if trade.direction == 1 else 'sell'
        }
        for trade in trades
    ]


def order_book_to_dict(figi, order_book):
    """Преобразует данные стакана заявок в словари."""
    if order_book.bids and order_book.asks:
        bid_price = order_book.bids[0].price.units + order_book.bids[0].price.nano / 1e9
        bid_volume = order_book.bids[0].quantity
        ask_price = order_book.asks[0].price.units + order_book.asks[0].price.nano / 1e9
        ask_volume = order_book.asks[0].quantity
        return [
            {
                'company_id': figi,
                'timestamp': now().strftime('%Y-%m-%d %H:%M:%S'),
                'bid_price': bid_price,
                'bid_volume': bid_volume,
                'ask_price': ask_price,
                'ask_volume': ask_volume
            }
        ]
    else:
        logger.warning(f"Order book for {figi} is empty or incomplete. Skipping insertion.")
        return []


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


def main():
    with Client(TOKEN) as client:
        companies = get_all_companies(client)
        logger.info(f'COMPANIES[0]\n{companies[0]}')
        logger.info(f'LEN(COMPANIES)\n{len(companies)}')

        for company in tqdm(companies):
            figi = company.figi
            name = company.name
            ticker = company.ticker

            # Вставляем информацию о компании в таблицу companies
            insert_company(figi, name, ticker)

            # 1. Волатильность инструмента от времени
            candles = get_candles(figi, client)
            candles_dict = candles_to_dict(figi, candles)
            insert_data('candles', candles_dict)
            if len(candles) > 0:
                logger.info(f'\nCANDLES[0]\n{candles[0]}')

            # 2. Влияние крупных сделок на цену
            last_trades = get_last_trades(figi, client)
            trades_dict = trades_to_dict(figi, last_trades)
            insert_data('trades', trades_dict)
            logger.info(f'\nLAST_TRADES\n{last_trades}')

            # 3. Предсказуемость цены закрытия
            close_prices = get_close_prices(figi, client)
            # Анализ предсказуемости цены закрытия
            logger.info(f'\nCLOSE_PRICES\n{close_prices}')

            # 4. Дисбаланс между заявками на покупку и продажу
            order_book = get_order_book(figi, client)
            order_book_dict = order_book_to_dict(figi, order_book)
            insert_data('order_book', order_book_dict)
            logger.info(f'\nORDER_BOOK\n{order_book}')

            # Здесь можно добавить логику для сохранения или анализа данных
            logger.info(f"Processed {name} ({ticker})")


if __name__ == "__main__":
    main()
