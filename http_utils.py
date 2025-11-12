import requests
from bs4 import BeautifulSoup

def fetch_page(url):
    """
    Делает HTTP GET запрос по URL и возвращает HTML страницы.
    Вызывает исключение, если запрос неудачен.
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_date(html):
    """
    Парсит переданный HTML, ищет дату в тегах <strong>,
    сравнивая строки с названиями месяцев на русском.
    """
    soup = BeautifulSoup(html, "html.parser")
    months = ("ЯНВАРЯ","ФЕВРАЛЯ","МАРТА","АПРЕЛЯ","МАЯ","ИЮНЯ","ИЮЛЯ",
              "АВГУСТА","СЕНТЯБРЯ","ОКТЯБРЯ","НОЯБРЯ","ДЕКАБРЯ")
    # Перебираем теги <strong> и ищем текст с одним из месяцев
    for tag in soup.find_all("strong"):
        text = tag.get_text(strip=True)
        if any(month in text for month in months):
            return text
    return None
