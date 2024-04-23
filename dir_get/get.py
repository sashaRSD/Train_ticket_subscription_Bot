from bs4 import BeautifulSoup
import requests

def scraping():
    try:
        response = requests.get(url='https://kogdapridut.ru/5-bukv').text
        soup = BeautifulSoup(response, 'lxml')
        text = soup.find('div', class_='content-tile content-costil').find('li').text
        data = text.split('—')
        data[1] = data[1].upper()
        data = ' — '.join(data)
        return data
    except requests.exceptions.ConnectionError:
        print('[!] Please check your connection!')
