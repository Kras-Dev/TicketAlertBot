from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class SeleniumDriver:
    def __init__(self, headless=False):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options)

    def get_dynamic_html(self, url, timeout=30):
        self.driver.get(url)
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        return self.driver.page_source

    def wait_for_page_load(self, timeout=120):
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        print("Страница полностью загружена.")

    def click_button_and_check(self, url, button_xpath, wait_timeout=120, check_timeout=30):
        self.driver.get(url)
        wait = WebDriverWait(self.driver, wait_timeout)

        button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
        button.click()
        print("Кнопка нажата.")

        wait.until(lambda d: len(d.window_handles) > 1)
        new_window = [win for win in self.driver.window_handles if win != self.driver.current_window_handle][0]
        self.driver.switch_to.window(new_window)

        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        try:
            element = WebDriverWait(self.driver, check_timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.custom-error-dialog-header"))
            )
            if "ВСЕ БИЛЕТЫ В БРОНИ ИЛИ РАСПРОДАНЫ" in element.text:
                print(element.text)
                return False
            else:
                print("Tickets possibly available")
                return True
        except TimeoutException:
            print("No error message found, tickets may be available")
            return True

    def quit(self):
        self.driver.quit()
