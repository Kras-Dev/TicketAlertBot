import requests
from bs4 import BeautifulSoup

def fetch_page(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_date(html):
    soup = BeautifulSoup(html, "html.parser")
    months = ("ЯНВАРЯ","ФЕВРАЛЯ","МАРТА","АПРЕЛЯ","МАЯ","ИЮНЯ","ИЮЛЯ",
              "АВГУСТА","СЕНТЯБРЯ","ОКТЯБРЯ","НОЯБРЯ","ДЕКАБРЯ")
    for tag in soup.find_all("strong"):
        text = tag.get_text(strip=True)
        if any(month in text for month in months):
            return text
    return None
