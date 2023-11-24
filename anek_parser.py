import requests
from bs4 import BeautifulSoup
import re

def get_random_aneks():
    headers = {
        'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.109 Safari/537.36 OPR/84.0.4316.52'
    }

    url = 'https://www.anekdot.ru/random/anekdot/'
    r = requests.get(url=url, headers=headers)

    soup = BeautifulSoup(r.text, 'html.parser')

    anecdot = soup.find_all('div', class_="text")
    # print(type(anecdot[0]))
    anecdot = [re.sub('<.*?>', '', '``' + str(article).replace('<br/>', '\n') + '``') for article in anecdot]
    # print(anecdot)
    return anecdot

get_random_aneks()