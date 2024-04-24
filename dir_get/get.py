from dir_get.params_yandex import params_yandex, cookies_yandex, headers_yandex
from datetime import datetime, timedelta
import requests, json


# html.parser- встроенный - никаких дополнительных зависимостей не требуется
# html5lib— самый снисходительный — лучше используйте его, если HTML не работает
# lxml- быстрейший

# user_agent = ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) '
#               'Gecko/20100101 Firefox/50.0')
# headers={'User-Agent': user_agent}


def datetime_start(hour):
    datetime0 = datetime.strptime(params_yandex['when'], "%Y-%m-%d") + timedelta(hours=hour)
    return datetime0


def find_train_place(train_class, price=0, need_seat=0, need_class=0):
    if need_class:
        class_name = need_class
    else:
        class_name = ['sitting', 'platzkarte', 'compartment', 'suite', 'soft']

    if not price:
        price = 1000000

    for class_i in class_name:
        if class_i in train_class:
            if train_class[class_i]['price']['value'] < price and train_class[class_i]['seats'] > need_seat:
                return True
    return


def all_train_place(seats):
    seat = ""
    if seats:
        if 'sitting' in seats:
            seat_price = seats['sitting']['price']['value']
            seat_place = seats['sitting']['seats']
            seat += f'  Сидячие - {seat_place} от {seat_price}\n'
        if 'platzkarte' in seats:
            seat_price = seats['platzkarte']['price']['value']
            seat_place = seats['platzkarte']['seats']
            places_lower = seats['platzkarte']['placesDetails']['lower']['quantity']
            places_upper = seats['platzkarte']['placesDetails']['upper']['quantity']
            seat += f'  Плацкарт - {seat_place} ({places_lower} ниж/ {places_upper} верх) от {seat_price}\n'
        if 'compartment' in seats:
            seat_price = seats['compartment']['price']['value']
            seat_place = seats['compartment']['seats']
            places_lower = seats['compartment']['placesDetails']['lower']['quantity']
            places_upper = seats['compartment']['placesDetails']['upper']['quantity']
            seat += f'  Купе - {seat_place} ({places_lower} ниж/ {places_upper} верх) от {seat_price}\n'
        if 'suite' in seats:
            seat_price = seats['suite']['price']['value']
            seat_place = seats['suite']['seats']
            places_lower = seats['suite']['placesDetails']['lower']['quantity']
            places_upper = seats['suite']['placesDetails']['upper']['quantity']
            seat += f'  СВ - {seat_place} ({places_lower} ниж/ {places_upper} верх) от {seat_price}\n'
        if 'soft' in seats:
            seat_price = seats['soft']['price']['value']
            seat_place = seats['soft']['seats'] / 2
            seat += f' Люкс - {seat_place} от {seat_price}\n'
    else:
        seat = f"   SOLD_OUT\n"
    return seat


def scraping_yandex():
    try:
        response = requests.get('https://travel.yandex.ru/api/trains/genericSearch',
                                params=params_yandex, cookies=cookies_yandex, headers=headers_yandex).json()
        all_trains = response.get('variants')
        # with open("dir_get/data_file_yandex.json", "w", encoding='utf-8') as write_file:
        #     json.dump(all_trains, write_file, indent=4, ensure_ascii=False)
        all_text = ''
        for train_id in all_trains:
            train = train_id['forward'][0]

            time_departure = datetime.strptime(train['departure'], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=3)
            time_arrival = (datetime.strptime(train['arrival'], "%Y-%m-%dT%H:%M:%SZ")
                            + timedelta(hours=3)).strftime("%H:%M:%S %d.%m.%Y")

            if time_departure > datetime_start(18) and find_train_place(train['tariffs']['classes'], 12000, 2):
                train_number = train['train']['number']
                train_company = train['company']['title']

                duration = train['duration'] / 60
                duration_min = int(duration % 60)
                duration_hour = int(duration // 60)

                station_from = train['stationFrom']['title']
                station_to = train['stationTo']['title']
                seat = all_train_place(train['tariffs']['classes'])

                all_text += (f'{time_departure.strftime("%H:%M:%S %d.%m.%Y")} \n'
                             f'Поезд №{train_number} {train_company} \n'
                             f'{station_from} -> {station_to} ({duration_hour}ч {duration_min} мин) \n'
                             f'{time_arrival}\n'
                             f'{seat}\n')
        if not all_text:
            all_text = 'Поездов нет!\n'
        all_text += 'Если нужна инфа, то вот → /get'
        return all_text
    except requests.exceptions.ConnectionError:
        print('[!] Please check your connection!')
        return '[!] Please check your connection!'
