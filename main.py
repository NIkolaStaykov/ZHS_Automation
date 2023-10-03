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

timeout = 3  # seconds of timeout for the webdriver to wait for an element to be present


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

    def load_course_registration_page(self, course_name, course_data):
        print(f"Loading course registration page for {course_name}")
        # Load list with courses
        self.driver.get("https://www.buchung.zhs-muenchen.de/angebote/aktueller_zeitraum_0/index.html")

        # Wait for the page to load
        try:
            WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.XPATH, f'//a[contains(., "{course_name}")]')))
        except:
            print("Course not found")
            return
        self.driver.find_element(By.XPATH, f'//a[contains(.,"{course_name}")]').click()

        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_any_elements_located((By.XPATH, '//input')))
        except:
            print("Booking not awailable yet")
            return

        booking_buttons = self.driver.find_elements(By.XPATH, '//input[@value="buchen"]')
        if len(booking_buttons) == 1 or course_data == {}:
            booking_buttons[0].click()
            self.driver.switch_to.window(self.driver.window_handles[1])
        else:
            print("Multiple bookings available")

    def login(self):
        login_data = self.user_data["login"]
        WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, '//input')))
        self.driver.find_element(By.XPATH, '//div[@id="bs_pw_anmlink"]').click()

        self.driver.find_element(By.XPATH, '//input[contains(@name, "mail")]').send_keys(login_data["mail"])
        self.driver.find_element(By.XPATH, '//input[@type="password"]').send_keys(login_data["password"])
        self.driver.find_element(By.XPATH, '//input[@value="weiter zur Buchung"]').click()

    def fill_bank_data(self):
        # Wait for the page to load
        WebDriverWait(self.driver, timeout).until(EC.visibility_of_any_elements_located((By.XPATH, '//select')))

        # semester_box = self.driver.find_element(By.XPATH, '//div[contains(., "semester")]/following-sibling::div')
        # semester_box.find_element(By.XPATH, '//input').click()
        # semester_box.find_element(By.XPATH, '//input').send_keys("5")

        nationality_box = self.driver.find_element(By.XPATH, '//div[contains(., "Nationalität")]/following-sibling::div')
        nationality_box.find_element(By.XPATH, 'select').send_keys(self.user_data["login"]["country"])

        iban_box = self.driver.find_element(By.XPATH, '//div[contains(., "IBAN")]/following-sibling::div')
        iban_box.find_element(By.XPATH, 'input').send_keys(self.user_data["bank"]["IBAN"]+'\n')

        bic_box = self.driver.find_element(By.XPATH, '//div[contains(., "BIC")]/following-sibling::div')
        bic_box.find_element(By.XPATH, 'input').send_keys(self.user_data["bank"]["BIC"])

        self.driver.find_element(By.XPATH, '//a[contains(., "Teilnahmebedingungen")]/preceding-sibling::input').click()

    def make_reservations(self):
        for (course_name, course_data) in self.user_data["courses"].items():
            self.load_course_registration_page(course_name, course_data)
            self.login()
            self.fill_bank_data()
            self.driver.find_element(By.XPATH, '//input[contains(@value, "Buchung")]').click()
            self.driver.find_element(By.XPATH, '//input[contains(@value, "buchen")]').click()
            print(f"Successfully booked {course_name}")


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
