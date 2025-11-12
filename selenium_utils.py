from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

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
            options.add_argument("--headless")
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
        print("Страница полностью загружена.")

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
        print("Кнопка нажата.")
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
                print(element.text)
                return False
            else:
                print("Tickets possibly available")
                return True
        except TimeoutException:
            # Если сообщение об ошибке не появилось за timeout — считаем, что билеты могут быть
            print("No error message found, tickets may be available")
            return True

    def quit(self):
        """
        Завершает работу драйвера, закрывая браузер.
        """
        self.driver.quit()
