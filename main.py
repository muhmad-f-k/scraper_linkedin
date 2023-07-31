# Import necessary modules
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import os
import pickle
import time
import json
import random

# Define LinkedIn class


class LinkedIn:

    LOGIN_URL = "https://www.linkedin.com/login"  # LinkedIn login URL
    # Path to store/load cookies
    COOKIE_PATH = os.path.join(os.getcwd(), 'cookies.pkl')

    # Class constructor
    def __init__(self):
        load_dotenv()  # Load environment variables
        # Get LinkedIn username from environment variable
        self.username = os.getenv('LINKEDIN_USERNAME')
        # Get LinkedIn password from environment variable
        self.password = os.getenv('LINKEDIN_PASSWORD')

        # Instantiate Chrome Options object
        self.chromeOptions = webdriver.ChromeOptions()
        self.prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.plugins": 1,
            "profile.managed_default_content_settings.popups": 2,
            "profile.managed_default_content_settings.geolocation": 2,
            "profile.managed_default_content_settings.media_stream": 2,
        }
        self.chromeOptions.add_experimental_option(
            "prefs", self.prefs)  # Add preferences to Chrome Options
        # self.chromeOptions.add_argument("--headless")  # Run in headless mode
        self.chromeOptions.add_argument("--no-sandbox")  # Disable sandbox mode
        # Disable features that might betray automation
        self.chromeOptions.add_argument("--disable-blink-features")
        # Disable 'automation' toolbar
        self.chromeOptions.add_argument(
            "--disable-blink-features=AutomationControlled")
        self.chromeOptions.add_argument("--disable-dev-shm-usage")
        self.chromeOptions.add_argument("disable-infobars")  # Disable infobars
        self.chromeOptions.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')  # Set user agent
        self.driver = webdriver.Chrome(
            options=self.chromeOptions)  # Initiate Chrome WebDriver

    # Method to load cookies
    def load_cookies(self):
        try:
            with open(self.COOKIE_PATH, 'rb') as f:  # Open the file to read in binary mode
                cookies = pickle.load(f)  # Load cookies from file
            for cookie in cookies:  # Iterate over each cookie
                self.driver.add_cookie(cookie)  # Add cookie to WebDriver
            print('Cookies loaded')
        except FileNotFoundError:  # Exception handling for file not found error
            print('No cookies found')
            return False

        return True

    # Method to save cookies
    def save_cookies(self):
        cookies = self.driver.get_cookies()  # Get cookies from WebDriver
        with open(self.COOKIE_PATH, 'wb') as f:  # Open the file to write in binary mode
            pickle.dump(cookies, f)  # Dump cookies into file
        print('Cookies saved')

    # Method to perform login action
    def login(self):
        self.driver.get(self.LOGIN_URL)  # Open LinkedIn login page

        if not self.load_cookies():  # If no cookies are loaded, perform login operation manually
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.ID, "username"))).send_keys(self.username)  # Wait until username field is present and input username
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.ID, "password"))).send_keys(self.password)  # Wait until password field is present and input password
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                (By.XPATH, '//button[@class="btn__primary--large from__button--floating"]'))).click()  # Wait until login button is clickable and click
            self.save_cookies()  # Save cookies after successful login

    # Extract text from a specified URL
    def extract_text(self):
        # Load keywords from json file
        with open('keywords.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            keywords = data['keywords']

        # Choose a random keyword
        keyword = random.choice(keywords)

        # Construct the URL
        url = f'https://www.linkedin.com/search/results/content/?keywords={keyword}&sortBy=%22date_posted%22'

        self.driver.get(url)  # Open the specified URL
        SCROLL_PAUSE_TIME = 2  # Time to pause between scrolls
        scroll_count = 0  # Initialize scroll counter

        while scroll_count < 7:  # Scroll the page 7 times
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")  # Scroll to bottom of page
            time.sleep(SCROLL_PAUSE_TIME)  # Wait for page to load
            scroll_count += 1  # Increment scroll counter

        # After the complete page is loaded, then find the elements
        elements = self.driver.find_elements(
            By.CSS_SELECTOR, 'div > div.feed-shared-update-v2__description-wrapper.mr2 > div.feed-shared-inline-show-more-text.feed-shared-update-v2__description.feed-shared-inline-show-more-text--minimal-padding > div > span > span > span')
        for i, element in enumerate(elements):  # Iterate over each element
            print(element.text)  # Print the text of the element
            print("___________")
            print(i)

    # Method to quit WebDriver
    def quit(self):
        print("Browser session ended")
        self.driver.quit()  # Quit the WebDriver session


# Instantiate LinkedIn class
linkedin = LinkedIn()

# Enclose in try-finally block to ensure cleanup even if exception occurs
try:
    linkedin.login()  # Perform login action
    linkedin.extract_text()  # Extract text from specified URL
    time.sleep(20)  # Pause execution for 20 seconds
finally:
    linkedin.quit()  # Quit WebDriver session
