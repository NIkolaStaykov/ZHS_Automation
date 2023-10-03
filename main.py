import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from datetime import datetime as time
import json
import re

timeout = 40  # seconds of timeout for the webdriver to wait for an element to be present


class ReservationAutomation:
    def __init__(self, config_path, driver_options=None, args=None):
        self.user_data = {}
        self.read_config(config_path)

        self.driver = None
        self.new_offers = None
        self.seen_offers = []
        self.setup_chrome_driver(driver_options, args)

    def read_config(self, config_path):
        config = json.load(open(config_path, "r"))
        self.user_data = config

    def setup_chrome_driver(self, driver_options=None, args=None):
        args = args or []
        driver_options = driver_options or {}

        chrome_options = Options()

        for (k, v) in driver_options.items():
            chrome_options.add_experimental_option(k, v)
        for arg in args:
            chrome_options.add_argument(arg)

        # create the initial window
        self.driver = webdriver.Chrome(options=chrome_options)

    def load_course_registration_page(self, course_name):
        # Load list with courses
        self.driver.get("https://www.buchung.zhs-muenchen.de/angebote/aktueller_zeitraum_0/index.html")

        # Wait for the page to load
        WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.XPATH, f'//a[contains(., "{course_name}")]')))
        hrefs = self.driver.find_element(By.XPATH, f'//a[contains(.,"{course_name}")]').click()
        return True

    def make_reservations(self):
        for course in self.user_data["courses"]:
            self.load_course_registration_page(course)
            self.make_reservation(course)


def main():
    config_path = "config.json"

    driver_options = {"useAutomationExtension": False,
                      "excludeSwitches": ["enable-automation"],
                      "prefs": {"credentials_enable_service": False,
                                "profile.password_manager_enabled": False}
                      }
    args = ["window-size=1920x1080", "--log-level=3"]
    bot = ReservationAutomation(config_path, driver_options, args)
    bot.make_reservations()


if __name__ == "__main__":
    main()
