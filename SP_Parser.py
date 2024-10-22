import random
import cianparser
import time
import requests
from bs4 import BeautifulSoup

from cianparser.constants import METRO_STATIONS

saintp_parser = cianparser.CianParser(location="Санкт-Петербург")


def get_cian_listings_count(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Проверяем статус код
    except requests.RequestException as e:
        print(f"Ошибка при отправке запроса: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    count_tag = soup.find('h5', class_='_93444fe79c--color_text-primary-default--vSRPB _93444fe79c--lineHeight_20px--fX7_V _93444fe79c--fontWeight_bold--BbhnX _93444fe79c--fontSize_14px--reQMB _93444fe79c--display_block--KYb25 _93444fe79c--text--e4SBY _93444fe79c--text_letterSpacing__normal--tfToq')

    if count_tag:
        count_text = count_tag.text
        count = ''.join(filter(str.isdigit, count_text))
        return int(count)
    else:
        print("Не удалось найти количество объявлений на странице.")
        return None


def parse_flats(deal_type="sale", max_pages=45):
    """
    Парсинг объявлений с сайта Циан по продаже или аренде квартир.
    :param deal_type: Тип сделки - 'sale' для продажи, 'rent_long' для аренды.
    :param max_pages: Максимальное количество страниц для парсинга.
    :return: Словарь всех объявлений, где ключ - это URL объявления.
    """
    all_flats_data = {}
    rooms = [1, 2, 3, 4, 5, 'studio']
    floors = [(i, i + 1) for i in range(1, 23, 2)]
    floors.append((23, 1000))
    stations = [station[0] for station in METRO_STATIONS["Петербургский"]]

    page_limit = 15  # Максимальное количество страниц в одном запросе
    for start_page in range(1, max_pages + 1, page_limit):
        end_page = min(start_page + page_limit - 1, max_pages)

        for station in stations:
            additional_settings = {
                "start_page": start_page,
                "end_page": end_page,
                "metro": "Петербургский",
                "metro_station": station,
            }

            url = saintp_parser.get_request_url(deal_type=deal_type, rooms=tuple(rooms),
                                                accommodation_type="flat", additional_settings=additional_settings)
            print("URL:", url)
            listings_count = get_cian_listings_count(url)
            if listings_count is None:
                print(f"Не удалось получить количество объявлений для станции {station}. Пропускаем.")
                continue

            print(f"Количество объявлений для станции {station}: {listings_count}")

            if listings_count > 5000:
                for room in rooms:
                    for floor in floors:
                        additional_settings.update({"min_floor": floor[0], "max_floor": floor[1]})
                        parse_flats_for_station(start_page, end_page, station, deal_type, room, additional_settings,
                                                all_flats_data)
            else:
                for room in rooms:
                    parse_flats_for_station(start_page, end_page, station, deal_type, room, additional_settings,
                                            all_flats_data)

    return all_flats_data


def parse_flats_for_station(start_page, end_page, station, deal_type, room, additional_settings, all_flats_data):
    """
    Парсинг квартир для конкретной станции метро и диапазона страниц.
    :param start_page: Начальная страница.
    :param end_page: Конечная страница.
    :param station: Станция метро.
    :param deal_type: Тип сделки ('sale' или 'rent_long').
    :param room: Количество комнат.
    :param additional_settings: Дополнительные параметры для запроса.
    :param all_flats_data: Словарь для сохранения всех данных (ключ - url).
    """
    print(f"Парсинг с {start_page}-й по {end_page}-ю страницы. room: {room}, station: {station}")

    flats = saintp_parser.get_flats(deal_type=deal_type, rooms=room, with_saving_csv=True,
                                    additional_settings=additional_settings, with_extra_data=True)
    print(f"Количество объявлений для страниц {start_page}-{end_page}: {len(flats)}")

    for flat in flats:
        url = flat.get("url")
        if url and url not in all_flats_data:
            all_flats_data[url] = flat

    time.sleep(random.uniform(1, 15))


if __name__ == "__main__":
    sale_flats_data = parse_flats(deal_type="sale", max_pages=45)
    rent_flats_data = parse_flats(deal_type="rent_long", max_pages=45)

    all_flats_data = {**sale_flats_data, **rent_flats_data}
    print(len(all_flats_data))
    print(all_flats_data)
