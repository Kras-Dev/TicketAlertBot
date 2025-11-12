from files_utils import add_subscriber, get_subscribers, load_last_update_id, save_last_update_id
import aiohttp

async def process_updates(filepath, bot_token, offset_file):
    """
    Обрабатывает обновления Telegram бота, добавляя новых подписчиков.
    Поддерживает long polling с использованием offset для пропуска уже обработанных обновлений.
    """
    # Последний update_id для смещения offset
    offset = load_last_update_id(offset_file)
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    # Если есть offset, запрашиваем обновления начиная с offset+1, иначе все новые
    params = {"offset": offset + 1} if offset is not None else {}
    # долгий опрос, чтобы снизить количество запросов
    params["timeout"] = 30
    # Загрузка текущих подписчиков
    subscribers = get_subscribers(filepath)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as resp:
                data = await resp.json()
                updates = data.get("result", [])
                max_update_id = offset or 0

                for update in updates:
                    message = update.get("message")
                    if message:
                        text = message.get("text", "")
                        chat = message.get("chat", {})
                        chat_id = str(chat.get("id"))
                        # Если пришла команда /start от пользователя, и его нет в подписчиках
                        if text == "/start" and chat_id and chat_id not in subscribers:
                            add_subscriber(filepath, chat_id)
                            subscribers.append(chat_id)
                            # Отправляем приветственное сообщение
                            await send_telegram_message(bot_token, chat_id, "Привет! Вы подписались на уведомления.")
                    max_update_id = max(max_update_id, update.get("update_id", 0))

                if max_update_id:
                    # Сохраняем последний обработанный update_id для последующих запросов с offset
                    save_last_update_id(offset_file, max_update_id)
        except Exception as e:
            print(f"Ошибка при обработке обновлений: {e}")



async def send_telegram_message(bot_token, chat_id, message):
    """
    Отправляет сообщение в Telegram чат с использованием API sendMessage.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML" # Позволяет использовать HTML-теги в сообщении
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload) as resp:
            if resp.status == 200:
                print("Сообщение в Telegram отправлено.")
            else:
                text = await resp.text()
                print(f"Ошибка при отправке сообщения: {text}")