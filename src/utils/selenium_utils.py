import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)

class SeleniumDriver:
    """
    Класс-обёртка для Selenium WebDriver Chrome с опцией headless.
    Реализует методы для загрузки страниц и взаимодействия с элементами.
    """
    def __init__(self, headless=False):
        """
        Конструктор, инициализирует драйвер Chrome с опцией headless.
        """
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument(
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36')
        self.driver = webdriver.Chrome(options=options)

    def get_dynamic_html(self, url, timeout=30):
        """
        Загружает страницу и ждёт, пока появится тег <body>.
        Возвращает полный HTML страницы.
        """
        self.driver.get(url)
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        return self.driver.page_source

    def wait_for_page_load(self, timeout=120):
        """
        Ждёт полной загрузки страницы (document.readyState == "complete").
        """
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def click_button_and_check(self, url, button_xpath, wait_timeout=120, check_timeout=30):
        """
        Переходит на страницу, ждёт кликабельности кнопки по XPATH, кликает её.
        Затем ждёт открытия нового окна и проверяет наличие сообщения об отсутствии билетов.
        Возвращает True, если билеты возможно есть, иначе False.
        """
        self.driver.get(url)
        wait = WebDriverWait(self.driver, wait_timeout)
        # Ждём, пока кнопка по XPATH станет кликабельной
        button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
        button.click()
        # Ждём, что откроется новое окно (например, всплывающее)
        wait.until(lambda d: len(d.window_handles) > 1)
        new_window = [win for win in self.driver.window_handles if win != self.driver.current_window_handle][0]
        # Переключаемся на новое окно
        self.driver.switch_to.window(new_window)
        # Ждём, пока страница и тело загрузятся
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        try:
            # Проверяем, есть ли элемент с сообщением об ошибке
            element = WebDriverWait(self.driver, check_timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.custom-error-dialog-header"))
            )
            # Смотрим, содержит ли ошибка текст о том, что билетов нет
            if "ВСЕ БИЛЕТЫ В БРОНИ ИЛИ РАСПРОДАНЫ" in element.text:
                return False
            else:
                return True
        except TimeoutException:
            self.driver.save_screenshot("src/config/files/screenshot.png")
            # Если сообщение об ошибке не появилось за timeout — считаем, что билеты могут быть
            logger.info("Сообщение об ошибке не обнаружено, могут быть доступны билеты")
            return "timeout"

    def quit(self):
        """
        Завершает работу драйвера, закрывая браузер.
        """
        self.driver.quit()
