from dir_get.params_yandex_Voronezh_Adler1 import data_Voronezh_Adler1
from dir_get.params_yandex_Moscow_Voronezh28 import data_Moscow_Voronezh28
from dir_get.params_yandex_Moscow_StOskol28 import data_Moscow_StOskol28
from dir_get.params_yandex_SPB_Moscow27 import data_SPB_Moscow27
from datetime import datetime, timedelta
from dir_base import base_train
import requests, json, asyncio


params_city_in_travel = [data_Moscow_Voronezh28, data_Moscow_StOskol28, data_Voronezh_Adler1]

# html.parser- встроенный - никаких дополнительных зависимостей не требуется
# html5lib— самый снисходительный — лучше используйте его, если HTML не работает
# lxml- быстрейший

# user_agent = ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) '
#               'Gecko/20100101 Firefox/50.0')
# headers={'User-Agent': user_agent}


#function---------------------------
async def scraping_yandex():
    response = {}
    try:
        all_travel = []
        for city in params_city_in_travel:
            settings_train = city[0]
            cookies_ya = city[1]
            header_ya = city[2]
            params_ya = city[3]
            response = requests.get('https://travel.yandex.ru/api/trains/genericSearch', cookies=cookies_ya,
                                    params=params_ya, headers=header_ya).json()
            all_trains = response.get('variants')
            # with open("dir_get/data_file_yandex.json", "w", encoding='utf-8') as write_file:
            #     json.dump(all_trains, write_file, indent=4, ensure_ascii=False)
            train_info = []
            new_ticket = False
            for train_id in all_trains:
                train = train_id['forward'][0]

                train_number = train['train']['number']
                time_departure = datetime.strptime(train['departure'], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=3)
                time_arrival = (datetime.strptime(train['arrival'], "%Y-%m-%dT%H:%M:%SZ")
                                + timedelta(hours=3)).strftime("%H:%M:%S %d.%m.%Y")

                if (time_departure > datetime_start(settings_train[0], params_ya) and
                        find_need_train_place(train['tariffs']['classes'], settings_train[1], settings_train[2])):
                    train_company = train['company']['title']
                    if not (await base_train.sql_read_train(train_number, time_departure)):
                        await base_train.sql_add_train(train_number, time_departure)

                    duration = train['duration'] / 60
                    duration_min = int(duration % 60)
                    duration_hour = int(duration // 60)

                    station_from = train['stationFrom']['title']
                    station_to = train['stationTo']['title']
                    seat_info = all_train_place_now(train['tariffs']['classes'])
                    seat_text = seat_info[0]

                    all_seats = seat_info[1]
                    result_find = find_new_train_place(all_seats, await base_train.sql_read_train(train_number, time_departure))
                    new_ticket = result_find[0]
                    new_ticket_text = result_find[1]
                    await base_train.sql_update_train(train_number, time_departure, all_seats)

                    train_info.append({"new_ticket_text": f'{new_ticket_text}',
                                       "date": f'<b>🕗 {time_departure.strftime("%H:%M:%S %d.%m.%Y")}</b> \n',
                                       "text": f'🚅 Поезд №{train_number} {train_company} \n'
                                               f'{station_from} -> {station_to} ({duration_hour}ч {duration_min} мин) \n'
                                               f'{time_arrival}\n'
                                               f'<b>{seat_text}</b>\n'})
                elif await base_train.sql_read_train(train_number, time_departure):
                    await base_train.sql_delete_train(train_number, time_departure)

            all_travel.append([new_ticket, await sort_train_time(train_info, header_ya)])
            await asyncio.sleep(3)
        return all_travel
    except requests.exceptions.ConnectionError:
        print('[!] Please check your connection!')
        return [[True, '[!] Please check your connection!']]
    except TypeError:
        print('[!] Please check captcha!')
        return [[True, f'[!] Please check captcha!\n{response.get("captcha").get("captcha-page")}']]


def datetime_start(hour, params_yandex):
    datetime0 = datetime.strptime(params_yandex['when'], "%Y-%m-%d") + timedelta(hours=hour)
    return datetime0


def find_need_train_place(train_class, price=0, need_seat=0, need_class=0):
    if not need_class:
        need_class = ['sitting', 'platzkarte', 'compartment', 'suite', 'soft']
    if not price:
        price = 1000000

    for class_i in need_class:
        if class_i in train_class:
            if train_class[class_i]['price']['value'] < price and train_class[class_i]['seats'] >= need_seat:
                return True
    return


def all_train_place_now(seats):
    seat_text = ""
    all_seats = [0, 0, 0, 0, 0, 0, 0]
    dict_class_name = {'sitting': 'Сидячие',
                       'platzkarte': 'Плацкарт',
                       'compartment': 'Купе',
                       'suite': 'СВ',
                       'soft': 'Люкс'}
    dict_all_seats = {'sitting': 0,
                      'platzkarte': [1, 2],
                      'compartment': [3, 4],
                      'suite': 5,
                      'soft': 6}

    if seats:
        for key_dict_i in dict_class_name.keys():
            if key_dict_i in seats:
                if key_dict_i == 'platzkarte':
                    seat_price = seats[f'{key_dict_i}']['price']['value']
                    seat_place = seats[f'{key_dict_i}']['seats']
                    places_lower = seats[f'{key_dict_i}']['placesDetails']['lower']['quantity']
                    places_upper = seats[f'{key_dict_i}']['placesDetails']['upper']['quantity']
                    places_lower_side = seats[f'{key_dict_i}']['placesDetails']['lowerSide']['quantity']
                    places_upper_side = seats[f'{key_dict_i}']['placesDetails']['upperSide']['quantity']
                    seat_text += (f'  {dict_class_name.get(key_dict_i)} - {seat_place} '
                                  f'({places_lower} + {places_lower_side}б. ниж/ '
                                  f'{places_upper} + {places_upper_side}б. верх) от {seat_price}\n')
                    all_seats[dict_all_seats.get(key_dict_i)[0]] = places_lower + places_lower_side
                    all_seats[dict_all_seats.get(key_dict_i)[1]] = places_upper + places_upper_side
                elif key_dict_i == 'compartment':
                    seat_price = seats[f'{key_dict_i}']['price']['value']
                    seat_place = seats[f'{key_dict_i}']['seats']
                    places_lower = seats[f'{key_dict_i}']['placesDetails']['lower']['quantity']
                    places_upper = seats[f'{key_dict_i}']['placesDetails']['upper']['quantity']
                    seat_text += (f'  {dict_class_name.get(key_dict_i)} - {seat_place} '
                                  f'({places_lower} ниж/ {places_upper} верх) от {seat_price}\n')
                    all_seats[dict_all_seats.get(key_dict_i)[0]] = places_lower
                    all_seats[dict_all_seats.get(key_dict_i)[1]] = places_upper
                else:
                    seat_price = seats[f'{key_dict_i}']['price']['value']
                    seat_place = seats[f'{key_dict_i}']['seats']
                    seat_text += f'  {dict_class_name.get(key_dict_i)} - {seat_place} от {seat_price}\n'
                    all_seats[dict_all_seats.get(key_dict_i)] = seat_place
    else:
        seat_text = f"   SOLD_OUT\n"
    return [seat_text, all_seats]


def find_new_train_place(all_seats, old_all_seats0):
    new_ticket = False
    all_text = ""
    class_train_name = ['Сидячие', 'Плацкарт нижнее', 'Плацкарт верхнее', 'Купе нижнее', 'Купе верхне', 'СВ', 'ЛЮКС']

    old_all_seats = list(old_all_seats0[0])
    old_all_seats.pop(0)
    old_all_seats.pop(0)
    for i in range(0, 7):
        if all_seats[i] > old_all_seats[i]:
            new_ticket = True
            all_text += f"<b>✅ Появились места - {class_train_name[i]} </b>\n"
    return [new_ticket, all_text]


async def sort_train_time(train_info, headers):
    name_travel = (headers.get("referer")[len("https://travel.yandex.ru/trains/"):].split("/")[0].upper())
    all_text = f'<b>🏡 {name_travel}</b> \n\n'
    if train_info:
        all_text_list = sorted(train_info, key=lambda x: datetime.strptime(x['date'],
                                                                           "<b>🕗 %H:%M:%S %d.%m.%Y</b> \n"),
                               reverse=False)

        for all_text_list_i in all_text_list:
            all_text += ''.join(f'{all_text_i}' for all_text_i in all_text_list_i.values())
    else:
        all_text += 'Поездов нет!\n'
    all_text += 'Если нужна инфа, то вот → /get'
    return all_text


