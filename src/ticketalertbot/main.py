import os
import sys
import logging
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from config.config import FILE_PATH, SUBSCRIBERS_FILE, REQUESTS_FILE, URL, BUTTON_XPATH
from handlers import routes
from utils.files_utils import get_subscribers, read_status, get_info_requests,\
    save_status
from utils.telegram_utils import fetch_updates, process_updates, notify_subscribers, \
    notify_info_requesters
from utils.http_utils import fetch_page, parse_date
from utils.selenium_utils import SeleniumDriver

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
if BOT_TOKEN is None:
    raise RuntimeError("BOT_TOKEN is not set in environment variables")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s %(levelname)s: %(message)s',
    filename='../../app.log',
    filemode='a',
)

async def main():
    """
    Основная корутина:
    - обрабатывает входящие обновления Telegram (подписки)
    - парсит сайт на предмет новой даты билетов
    - проверяет наличие билетов через Selenium
    - рассылает сообщения подписчикам
    """
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(routes.router)
    # Получаем и обрабатываем накопленные команды /start, /info
    offset = None
    while True:
        updates = await fetch_updates(bot, offset)
        if not updates:
            break
        await process_updates(updates, dp, bot)
        offset = updates[-1].update_id + 1

    status = read_status(FILE_PATH)
    subscribers = get_subscribers(SUBSCRIBERS_FILE)
    info_requests = get_info_requests(REQUESTS_FILE)

    driver = SeleniumDriver(headless=True)
    try:
        html = fetch_page(URL)
        new_date = parse_date(html)
        if not new_date:
            logging.info("Дата не найдена на странице.")
            return

        if not status:
            tickets_available = await asyncio.to_thread(driver.click_button_and_check, URL, BUTTON_XPATH)
            save_status(FILE_PATH, new_date, tickets_available)

            if tickets_available:
                await notify_subscribers(subscribers, f"Билеты доступны на {new_date}", BOT_TOKEN)
            else:
                if info_requests:
                    await notify_info_requesters(info_requests, f"Билетов на {new_date} нет.", BOT_TOKEN)
            return

        if status.get("date") == new_date:
            if status.get("status"):
                tickets_available = await asyncio.to_thread(driver.click_button_and_check, URL, BUTTON_XPATH)
                save_status(FILE_PATH, new_date, tickets_available)

                if tickets_available:
                    await notify_subscribers(subscribers, f"Билеты доступны на {new_date}", BOT_TOKEN)
                else:
                    if info_requests:
                        await notify_info_requesters(info_requests, f"Билетов на {new_date} нет.", BOT_TOKEN)
                return
            else:
                if info_requests:
                    await notify_info_requesters(info_requests, f"Билетов на {new_date} нет.", BOT_TOKEN)
                return

        tickets_available = await asyncio.to_thread(driver.click_button_and_check, URL, BUTTON_XPATH)
        save_status(FILE_PATH, new_date, tickets_available)

        if tickets_available:
            await notify_subscribers(subscribers, f"Билеты доступны на {new_date}", BOT_TOKEN)
        else:
            if info_requests:
                await notify_info_requesters(info_requests, f"Билетов на {new_date} нет.", BOT_TOKEN)

    finally:
        driver.quit()

def run():
    asyncio.run(main())

if __name__ == "__main__":
    run()
