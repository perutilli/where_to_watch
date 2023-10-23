from bs4 import BeautifulSoup
import requests
from utilities import get_soup

# headers = {
#     'User-agent':
#     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582'
#     'Content-Type:text/html; charset=utf-8'
# }

# url = 'https://www.justwatch.com/us/tv-show/curb-your-enthusiasm'
# page_resp = requests.get(url, headers=headers)
# page = BeautifulSoup(page_resp.text, "lxml")

# streams = page.find('div', {"class": "price-comparison--block"}).find('div', {"class": "price-comparison__grid__row price-comparison__grid__row--stream"})

# images = list(map(lambda tag : tag.attrs['title'], streams.find_all('img')))

# print(images)

def search_show(show_name: str, prefix: str):
    """ 
    Supposing the first result is the right one 
    search_string = search?q=show_name
    spaces should be replaced with %20
    show row: <ion-row class="title-list-row__row md hydrated">
    <div class="title-list search-content title-list--CLS-block"
    """

    search_str = f'search?q={show_name.replace(" ", "%20")}'
    url = f'{prefix}{search_str}'
    results_page = get_soup(url)
    result = results_page.find('div', {"id": "base"})
    return result

if __name__ == '__main__':
    result = search_show('game of thrones', 'https://justwatch.com/it/')
    print(result)


