import os
from http_utils import fetch_page, parse_date
from selenium_utils import SeleniumDriver
from telegram_utils import send_telegram_message
import asyncio


FILE_PATH = "date.txt"
URL = "https://mediumquality.ru/chitateli"
BUTTON_XPATH = "//a[contains(@class, 't-btn') and .//div[@class='t993__btn-text-title' and contains(text(), '21:00')]]"
BOT_TOKEN = "8064023147:AAHdKdUIHo8nCI0K-bm7tZlsivZLhQexwyo"
CHAT_ID = "ВАШ_CHAT_ID"

def read_saved_date(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None

def save_date(filepath, date):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(date)

async def main():
    driver = SeleniumDriver(headless=False)
    html = fetch_page(URL)
    new_date = parse_date(html)
    if not new_date:
        print("Дата не найдена на странице.")
        return

    saved_date = read_saved_date(FILE_PATH)
    if saved_date == new_date:
        print("Дата совпадает, выходим.")
        return

    save_date(FILE_PATH, new_date)
    tickets_available = driver.click_button_and_check(URL, BUTTON_XPATH)
    driver.quit()
    if tickets_available:
        print("Билеты есть.")
        await send_telegram_message(BOT_TOKEN,f"Билеты доступны на {new_date}")
    else:
        print("Билетов нет.")
        await send_telegram_message(BOT_TOKEN, f"Билеты отсутствуют на {new_date}")


if __name__ == "__main__":
    asyncio.run(main())
