from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import logging

from config.config import SUBSCRIBERS_FILE, REQUESTS_FILE
from utils.files_utils import add_subscriber, get_subscribers, get_info_requests, add_info_request
from utils.telegram_utils import send_telegram_message

router = Router()
logger = logging.getLogger(__name__)

@router.message(CommandStart())
async def cmd_start(message: Message):
    chat_id = str(message.chat.id)
    subscribers = get_subscribers(SUBSCRIBERS_FILE)

    if chat_id not in subscribers:
        add_subscriber(SUBSCRIBERS_FILE, chat_id)
        logger.info(f"New subscriber added: {chat_id}")
        await send_telegram_message(message.bot.token, chat_id, "Привет! Вы подписались на уведомления.")
    else:
        logger.info(f"Subscriber {chat_id} tried /start again")
        await message.answer("Вы уже подписаны на уведомления.")

@router.message(Command(commands=["info"]))
async def cmd_info(message: Message):
    chat_id = str(message.chat.id)
    info_requests = get_info_requests(REQUESTS_FILE)

    if chat_id not in info_requests:
        add_info_request(REQUESTS_FILE, chat_id)
        logger.info(f"Info request added for chat_id: {chat_id}")
    await message.answer("Ваш запрос принят, скоро пришлю статус по билетам.")