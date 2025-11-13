import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # путь к папке со скриптом
FILES_DIR = os.path.join(BASE_DIR, "files")            # папка files в проекте

# создать папку files, если она не существует
os.makedirs(FILES_DIR, exist_ok=True)

OFFSET_FILE = os.path.join(FILES_DIR, "offset.txt")
FILE_PATH = os.path.join(FILES_DIR, "date.json")
SUBSCRIBERS_FILE = os.path.join(FILES_DIR, "subscribers.txt")
REQUESTS_FILE = os.path.join(FILES_DIR, "info_requests.txt")
LOG_FILE = os.path.join(FILES_DIR, "app.log")
screenshot_path = os.path.join(FILES_DIR, "screenshot.png")


URL = "https://mediumquality.ru/chitateli"
BUTTON_XPATH = "//a[contains(@class, 't-btn') and .//div[@class='t993__btn-text-title' and contains(text(), '21:00')]]"
