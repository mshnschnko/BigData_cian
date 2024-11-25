import random
import json
import cianparser
import time
import requests
import configparser

from bs4 import BeautifulSoup
from cianparser.constants import METRO_STATIONS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException


# with open('data_proxies.txt', 'r') as file:
#     lines = [line.strip() for line in file.readlines()]
#
# ip_addresses = [line.split("//")[1].split(":")[0] for line in lines]
#
# print(ip_addresses)

# Чтение конфигурации
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

# Создание парсера для Санкт-Петербурга
saintp_parser = cianparser.CianParser(location="Санкт-Петербург")


# Функция для сохранения данных
def save_data(all_flats_data, filename="flats_data.json"):
    """Сохранение данных в файл JSON."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(all_flats_data, file, ensure_ascii=False, indent=4)


def get_cian_listings_count_sel(url, deal_type):
    # Устанавливаем опции для WebDriver (например, headless режим, если нужен)
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Запуск браузера в фоновом режиме
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    chrome_options.page_load_strategy = 'eager'

    # Укажите путь к ChromeDriver
    # service = Service('/path/to/chromedriver')  # Замените на путь к вашему ChromeDriver

    try:
        # Инициализация WebDriver
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        # Ждём, чтобы страница успела загрузиться (можно настроить таймер или использовать WebDriverWait)
        # time.sleep(3)  # Простой вариант с задержкой; замените на WebDriverWait при необходимости

        # Получаем HTML-код страницы с помощью Selenium
        page_content = driver.page_source

        # Используем BeautifulSoup для парсинга
        soup = BeautifulSoup(page_content, 'html.parser')

        # Извлечение числа объявлений с использованием BeautifulSoup
        count_elem = soup.find('h5', class_='_93444fe79c--color_text-primary-default--vSRPB')
        if count_elem:
            count_text = count_elem.get_text(strip=True)
            count = int(''.join(filter(str.isdigit, count_text)))
            return count
        else:
            print("Не удалось найти элемент с количеством объявлений на странице.")
            return None
    except WebDriverException as e:
        print(f"Ошибка при работе с WebDriver: {e}")
        return None
    finally:
        # Закрытие браузера после завершения работы
        driver.quit()


def get_cian_listings_count(url, deal_type):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        # Извлечение числа объявлений
        count_elem = soup.find('h5', class_='_93444fe79c--color_text-primary-default--vSRPB')
        if count_elem:
            count_text = count_elem.get_text(strip=True)
            count = int(''.join(filter(str.isdigit, count_text)))
            return count
        else:
            print("Не удалось найти элемент с количеством объявлений на странице.")
            return None
    except requests.RequestException as e:
        print(f"Ошибка при отправке запроса: {e}")
        return None


# Основная функция для парсинга квартир
def parse_flats(deal_type="sale", max_pages=45, metro_line='Красная'):
    all_flats_data = {}
    rooms = [1, 2, 3, 4, 5, 'studio']
    floors = [(i, i + 1) for i in range(1, 23, 2)]
    floors.append((23, 1000))
    stations = [station[0] for station in METRO_STATIONS["Петербургский"] if station[2] == metro_line]

    page_limit = 12
    try:
        for start_page in range(1, max_pages + 1, page_limit):
            end_page = min(start_page + page_limit - 1, max_pages)

            for station in stations:
                print(f"Начало парсинга для станции {station} со страницы {start_page} по {end_page}")
                additional_settings = {
                    "start_page": start_page,
                    "end_page": end_page,
                    "metro": "Петербургский",
                    "metro_station": station,
                }

                url = saintp_parser.get_request_url(deal_type=deal_type, rooms=tuple(rooms),
                                                    accommodation_type="flat", additional_settings=additional_settings)
                print("URL", url)
                listings_count = get_cian_listings_count(url, deal_type)
                if listings_count is None:
                    print(f"Не удалось получить количество объявлений для станции {station}. Пропускаем.")
                    continue

                print(f"Количество объявлений для станции {station}: {listings_count}")

                if listings_count > 5000:
                    for room in rooms:
                        for floor in floors:
                            additional_settings.update({"min_floor": floor[0], "max_floor": floor[1]})
                            print(f'ЭТАЖИ от {floor[0]} до {floor[1]}')
                            parse_flats_for_station(start_page, end_page, station, deal_type, room, additional_settings,
                                                    all_flats_data, )
                            time.sleep(random.uniform(300, 600))
                            print(f"Текущая длина all_flats_data: {len(all_flats_data)}")
                else:
                    for room in rooms:
                        parse_flats_for_station(start_page, end_page, station, deal_type, room, additional_settings,
                                                all_flats_data)
                        time.sleep(random.uniform(300, 600))
                        print(f"Текущая длина all_flats_data: {len(all_flats_data)}")

    except Exception as e:
        print(f"Ошибка парсинга: {e}")
    finally:
        save_data(all_flats_data)
        print("Завершение работы парсинга.")

    return all_flats_data


# Функция для парсинга квартир для конкретной станции метро
def parse_flats_for_station(start_page, end_page, station, deal_type, room, additional_settings, all_flats_data):
    print(f"Парсинг для станции {station} и комнат {room} с {start_page}-й по {end_page}-ю страницы.")
    # print('Словарь ебаный я его всё ебал:', all_flats_data)
    try:
        flats = saintp_parser.get_flats(deal_type=deal_type, rooms=room, with_saving_csv=True,
                                        additional_settings=additional_settings, with_extra_data=True)
        print(f"Количество объявлений для станции {station}, комната {room}, парсим со страницы {start_page}"
              f" до страницы {end_page}, количество объявлений {len(flats)}")

        for flat in flats:
            # print('Словарь ебаный я его всё ебал:', all_flats_data)
            url = flat.get("url")
            # print(all_flats_data)
            if url and url not in all_flats_data:
                # print('Словарь ебаный я его всё ебал:', all_flats_data)
                all_flats_data[url] = flat

        # time.sleep(random.uniform(1, 5))  # Задержка для предотвращения блокировки

    except Exception as e:
        print(f"Ошибка при парсинге станции {station}, комната {room}: {e}")
    finally:
        # Сохранение данных в случае ошибки
        if all_flats_data:  # Проверка на наличие данных
            save_data(all_flats_data)
        else:
            print("Словарь all_flats_data пустой, данные не будут сохранены.")


def run_parser_for_deal(config_section):
    """
    Запускает парсер с параметрами, указанными в выбранной секции конфига.
    :param config_section: Название секции в config.ini.
    """
    try:
        deal_type = config[config_section].get('deal_type', 'sale')
        max_pages = int(config[config_section].get('max_pages', 45))
        metro_line = config[config_section].get('metro_line', 'Красная')

        print(
            f"Запуск парсинга для секции {config_section}: deal_type={deal_type}, max_pages={max_pages}, metro_line={metro_line}")
        parse_flats(deal_type=deal_type, max_pages=max_pages, metro_line=metro_line)

    except KeyError as e:
        print(f"Ошибка: не удалось найти ключ в конфигурации {config_section}: {e}")


def run_parser():
    for section in config.sections():
        print(f"Запуск парсинга для секции: {section}")
        run_parser_for_deal(section)


# Запуск основного процесса для всех секций конфигурации, кроме DEFAULT
if __name__ == "__main__":
    run_parser()
