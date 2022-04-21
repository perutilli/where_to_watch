from bs4 import BeautifulSoup
import requests
import pickle

headers = {
    'User-agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582'
    'Content-Type:text/html; charset=utf-8'
}

url = 'https://www.justwatch.com/'
page_resp = requests.get(url, headers=headers)
page = BeautifulSoup(page_resp.text, "lxml")

countries = page.find('div', {"class": "container countries-list"}).find_all('a')

countries_prefixes = list(map(lambda tag :tag['href'], countries))

with open("prefixes.p", "wb") as file:
    pickle.dump(countries_prefixes, file)