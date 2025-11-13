import os
import json

def read_status(filepath):
    """
    Читает дату и флаг из JSON файла.
    Если файл отсутствует или некорректен, возвращает None.
    """
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return None
    return None

def save_status(filepath, date, flag):
    """
    Сохраняет дату и флаг (наличие билетов) в JSON файл.
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({"date": date, "status": flag}, f, ensure_ascii=False)

def add_subscriber(filepath, chat_id):
    """
    Добавляет chat_id в файл подписчиков, если его там еще нет.
    Если файл отсутствует, создаёт новый пустой.
    """
    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("")
    with open(filepath, "r", encoding="utf-8") as f:
        # Загружаем подписчиков в множество для быстрого поиска
        subscribers = set(line.strip() for line in f.readlines())
    if str(chat_id) not in subscribers:
        # Добавляем нового подписчика в файл
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(str(chat_id) + "\n")

def get_subscribers(filepath):
    """
    Возвращает список chat_id всех подписчиков из файла.
    Если файл отсутствует, возвращает пустой список.
    """
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]

def save_last_update_id(filepath, update_id):
    """
    Сохраняет последний обработанный update_id Telegram API в файл.
    """
    with open(filepath, "w") as f:
        f.write(str(update_id))

def load_last_update_id(filepath):
    """
    Загружает последний update_id из файла.
    Если файл отсутствует или содержимое некорректно, возвращает None.
    """
    try:
        with open(filepath, "r") as f:
            return int(f.read())
    except (FileNotFoundError, ValueError):
        return None

def add_info_request(filepath, chat_id):
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(chat_id + "\n")

def get_info_requests(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        return []

def clear_info_requests(filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        pass  # очищаем файл

