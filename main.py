import os

from http_utils import fetch_page, parse_date
from selenium_utils import SeleniumDriver
from telegram_utils import send_telegram_message, process_updates
from files_utils import save_date, read_saved_date, get_subscribers
import asyncio
from dotenv import load_dotenv

load_dotenv()

OFFSET_FILE = "offset.txt"
FILE_PATH = "date.txt"
URL = "https://mediumquality.ru/chitateli"
BUTTON_XPATH = "//a[contains(@class, 't-btn') and .//div[@class='t993__btn-text-title' and contains(text(), '21:00')]]"
SUBSCRIBERS_FILE = "subscribers.txt"
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def main():
    """
    Основная корутина:
    - обрабатывает входящие обновления Telegram (подписки)
    - парсит сайт на предмет новой даты билетов
    - проверяет наличие билетов через Selenium
    - рассылает сообщения подписчикам
    """
    # Обрабатываем входящие обновления в телеграме (подписки новых пользователей)
    await process_updates(SUBSCRIBERS_FILE, BOT_TOKEN, OFFSET_FILE )
    # Запускаем Selenium-драйвер в headless режиме для работы с динамическим сайтом
    driver = SeleniumDriver(headless=True)
    html = fetch_page(URL)
    new_date = parse_date(html)
    if not new_date:
        print("Дата не найдена на странице.")
        return

    saved_date = read_saved_date(FILE_PATH)
    subscribers = get_subscribers(SUBSCRIBERS_FILE)
    if saved_date == new_date:
        print("Дата совпадает, выходим.")
        for chat_id in subscribers:
            await send_telegram_message(BOT_TOKEN, chat_id, f"Билеты отсутствуют на {new_date}")
        return

    save_date(FILE_PATH, new_date)
    tickets_available = driver.click_button_and_check(URL, BUTTON_XPATH)
    driver.quit()


    if tickets_available:
        print("Билеты есть.")
        for chat_id in subscribers:
            await send_telegram_message(BOT_TOKEN, chat_id, f"Билеты доступны на {new_date}")
    else:
        print("Билетов нет.")
        for chat_id in subscribers:
            await send_telegram_message(BOT_TOKEN, chat_id, f"Билеты отсутствуют на {new_date}")


if __name__ == "__main__":
    asyncio.run(main())
