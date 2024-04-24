from dir_get.params_yandex import params_yandex, cookies_yandex, headers_yandex
from datetime import datetime, timedelta
from dir_base import base_train
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
            if train_class[class_i]['price']['value'] < price and train_class[class_i]['seats'] >= need_seat:
                return True
    return


def all_train_place(seats):
    seat = ""
    all_seats = [0, 0, 0, 0, 0, 0, 0, 0]
    if seats:
        if 'sitting' in seats:
            seat_price = seats['sitting']['price']['value']
            seat_place = seats['sitting']['seats']
            seat += f'  Сидячие - {seat_place} от {seat_price}\n'
            all_seats[0] = seat_place
        if 'platzkarte' in seats:
            seat_price = seats['platzkarte']['price']['value']
            seat_place = seats['platzkarte']['seats']
            places_lower = seats['platzkarte']['placesDetails']['lower']['quantity']
            places_upper = seats['platzkarte']['placesDetails']['upper']['quantity']
            seat += f'  Плацкарт - {seat_place} ({places_lower} ниж/ {places_upper} верх) от {seat_price}\n'
            all_seats[1] = places_lower
            all_seats[2] = places_upper
        if 'compartment' in seats:
            seat_price = seats['compartment']['price']['value']
            seat_place = seats['compartment']['seats']
            places_lower = seats['compartment']['placesDetails']['lower']['quantity']
            places_upper = seats['compartment']['placesDetails']['upper']['quantity']
            seat += f'  Купе - {seat_place} ({places_lower} ниж/ {places_upper} верх) от {seat_price}\n'
            all_seats[3] = places_lower
            all_seats[4] = places_upper
        if 'suite' in seats:
            seat_price = seats['suite']['price']['value']
            seat_place = seats['suite']['seats']
            places_lower = seats['suite']['placesDetails']['lower']['quantity']
            places_upper = seats['suite']['placesDetails']['upper']['quantity']
            seat += f'  СВ - {seat_place} ({places_lower} ниж/ {places_upper} верх) от {seat_price}\n'
            all_seats[5] = places_lower
            all_seats[6] = places_upper
        if 'soft' in seats:
            seat_price = seats['soft']['price']['value']
            seat_place = seats['soft']['seats'] / 2
            seat += f' Люкс - {seat_place} от {seat_price}\n'
            all_seats[7] = seat_place
    else:
        seat = f"   SOLD_OUT\n"
    return [seat, all_seats]


def find_new_train_place(all_seats, old_all_seats):
    new_ticket = False
    all_text = ""
    for old_seats_class in old_all_seats:
        if all_seats[0] > old_seats_class[1]:
            new_ticket = True
            all_text += "<b>✅ Новые места - Сидячие</b>\n"
        if all_seats[1] > old_seats_class[2]:
            new_ticket = True
            all_text += "<b>✅ Новые места - Плацкарт нижнее</b>\n"
        if all_seats[2] > old_seats_class[3]:
            new_ticket = True
            all_text += "<b>✅ Новые места - Плацкарт верхнее</b>\n"
        if all_seats[3] > old_seats_class[4]:
            new_ticket = True
            all_text += "<b>✅ Новые места - Купе нижнее</b>\n"
        if all_seats[4] > old_seats_class[5]:
            new_ticket = True
            all_text += "<b>✅ Новые места - Купе верхнее</b>\n"
        if all_seats[5] > old_seats_class[6]:
            new_ticket = True
            all_text += "<b>✅ Новые места - СВ нижнее</b>\n"
        if all_seats[6] > old_seats_class[7]:
            new_ticket = True
            all_text += "<b>✅ Новые места - СВ верхнее</b>\n"
        if all_seats[7] > old_seats_class[8]:
            new_ticket = True
            all_text += "<b>✅ Новые места - ЛЮКС</b>\n"
    return [new_ticket, all_text]


async def scraping_yandex():
    try:
        response = requests.get('https://travel.yandex.ru/api/trains/genericSearch',
                                params=params_yandex, cookies=cookies_yandex, headers=headers_yandex).json()
        all_trains = response.get('variants')
        # with open("dir_get/data_file_yandex.json", "w", encoding='utf-8') as write_file:
        #     json.dump(all_trains, write_file, indent=4, ensure_ascii=False)
        all_text = ''
        new_ticket = False
        for train_id in all_trains:
            train = train_id['forward'][0]

            time_departure = datetime.strptime(train['departure'], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=3)
            time_arrival = (datetime.strptime(train['arrival'], "%Y-%m-%dT%H:%M:%SZ")
                            + timedelta(hours=3)).strftime("%H:%M:%S %d.%m.%Y")

            if time_departure > datetime_start(18) and find_train_place(train['tariffs']['classes'], 12000, 2):
                train_number = train['train']['number']
                train_company = train['company']['title']
                if not (await base_train.sql_read_train(train_number)):
                    await base_train.sql_add_train(train_number)

                duration = train['duration'] / 60
                duration_min = int(duration % 60)
                duration_hour = int(duration // 60)

                station_from = train['stationFrom']['title']
                station_to = train['stationTo']['title']
                seat_info = all_train_place(train['tariffs']['classes'])
                seat = seat_info[0]
                all_seats = seat_info[1]
                result_find = find_new_train_place(all_seats, await base_train.sql_read_train(train_number))
                new_ticket = result_find[0]
                all_text += result_find[1]
                await base_train.sql_update_train(train_number, all_seats)

                all_text += (f'<b>🕗 {time_departure.strftime("%H:%M:%S %d.%m.%Y")}</b> \n'
                             f'🚂 Поезд №{train_number} {train_company} \n'
                             f'{station_from} -> {station_to} ({duration_hour}ч {duration_min} мин) \n'
                             f'{time_arrival}\n'
                             f'<b>{seat}</b>\n')
        if not all_text:
            all_text = 'Поездов нет!\n'
        all_text += 'Если нужна инфа, то вот → /get'
        return [new_ticket, all_text]
    except requests.exceptions.ConnectionError:
        print('[!] Please check your connection!')
        return '[!] Please check your connection!'
