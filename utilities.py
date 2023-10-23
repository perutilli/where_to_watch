from bs4 import BeautifulSoup
import requests

headers = {
    'User-agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582'
    'Content-Type:text/html; charset=utf-8'
}

def get_soup(url: str):
    page_resp = requests.get(url)#, headers=headers)
    page = BeautifulSoup(page_resp.text, "lxml")
    bytes = page_resp.text.encode("utf-8")
    with open("out.html", "wb") as f:
        f.write(bytes)
    return page