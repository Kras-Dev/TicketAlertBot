import aiohttp
import logging
from aiogram import Dispatcher
from aiogram.types import Update

from config.config import REQUESTS_FILE
from utils.files_utils import clear_info_requests

logger = logging.getLogger(__name__)

async def fetch_updates(bot, offset=None):
    # Получаем обновления через метод getUpdates с заданным offset (если есть)
    updates = await bot.get_updates(offset=offset, timeout=1)
    return updates

async def process_updates(updates, dp: Dispatcher, bot):
    # Проходим по списку апдейтов и шагаем их в обработчики aiogram
    for update in updates:
        # Преобразуем dict в aiogram Update объект
        if isinstance(update, dict):
            update_obj = Update(**update)
        else:
            update_obj = update
        await dp.feed_update(bot, update_obj)

async def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload) as resp:
            if resp.status == 200:
                logger.info(f"Message sent to {chat_id}.")
            else:
                text = await resp.text()
                logger.error(f"Error sending message to {chat_id}: {text}")

async def notify_subscribers(subscribers, message, bot_token):
    for chat_id in subscribers:
        await send_telegram_message(bot_token, chat_id, message)

async def notify_info_requesters(info_requests, message, bot_token):
    for chat_id in info_requests:
        await send_telegram_message(bot_token, chat_id, message)
    clear_info_requests(REQUESTS_FILE)

async def notify_based_on_status(tickets_available, new_date, subscribers, info_requests, bot_token):
    if tickets_available == "timeout":
        logging.info("Timeout occured while checking tickets - возможна временная ошибка, попробуйте позже")
        await notify_subscribers(subscribers, "Timeout occured", bot_token)
        if info_requests:
            await notify_info_requesters(info_requests, "Timeout occured", bot_token)
    elif tickets_available:
        await notify_subscribers(subscribers, f"Билеты доступны на {new_date}", bot_token)
    else:
        if info_requests:
            await notify_info_requesters(info_requests, f"Билетов на {new_date} нет.", bot_token)
