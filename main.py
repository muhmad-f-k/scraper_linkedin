# Import necessary modules
import asyncio
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
import pickle
import time
import json
import random


class LinkedIn:
    LOGIN_URL = "https://www.linkedin.com/login"  # LinkedIn login URL
    # Path to store/load cookies
    COOKIE_PATH = os.path.join(os.getcwd(), 'cookies.pkl')

    # Class constructor
    def __init__(self):
        load_dotenv()  # Load environment variables
        # Load LinkedIn username
        self.username = os.getenv('LINKEDIN_USERNAME')
        # Load LinkedIn password
        self.password = os.getenv('LINKEDIN_PASSWORD')

        # Initialize Chrome options
        self.chromeOptions = webdriver.ChromeOptions()
        # Define Chrome preferences to disable unnecessary popups and notifications
        self.prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.plugins": 1,
            "profile.managed_default_content_settings.popups": 2,
            "profile.managed_default_content_settings.geolocation": 2,
            "profile.managed_default_content_settings.media_stream": 2,
            # "profile.managed_default_content_settings.images": 2,# Enable this feature only  in headless mode
        }
        # Add preferences to Chrome options
        # self.chromeOptions.add_argument("--headless")  # Run in headless mode
        self.chromeOptions.add_experimental_option("prefs", self.prefs)
        # Disable sandbox mode for Chrome
        self.chromeOptions.add_argument("--no-sandbox")
        # Disable some features to make automation less detectable
        self.chromeOptions.add_argument("--disable-blink-features")
        self.chromeOptions.add_argument(
            "--disable-blink-features=AutomationControlled")
        self.chromeOptions.add_argument("--disable-dev-shm-usage")
        # Disable infobars
        self.chromeOptions.add_argument("disable-infobars")
        # Set user agent to look like a regular browser
        self.chromeOptions.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')
        # Initialize Chrome WebDriver with the defined options
        self.driver = webdriver.Chrome(options=self.chromeOptions)

    # Method to load cookies from file
    def load_cookies(self):
        try:
            # Try to open the cookie file
            with open(self.COOKIE_PATH, 'rb') as f:
                # Load cookies from the file
                cookies = pickle.load(f)
            # Add each cookie to the WebDriver
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            print('Cookies loaded')
        except FileNotFoundError:
            print('No cookies found')
            return False

        return True

    # Method to save cookies to file
    def save_cookies(self):
        # Get cookies from WebDriver
        cookies = self.driver.get_cookies()
        # Open the cookie file to write
        with open(self.COOKIE_PATH, 'wb') as f:
            # Save cookies to the file
            pickle.dump(cookies, f)
        print('Cookies saved')

    # Asynchronous method to login
    async def login(self):
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            # Run the synchronous login implementation in a separate thread
            await loop.run_in_executor(executor, self._login_impl)

    # Synchronous method to login
    def _login_impl(self):
        # Open the LinkedIn login page
        self.driver.get(self.LOGIN_URL)
        # Try to load cookies
        if not self.load_cookies():
            # If cookies can't be loaded, manually enter the username and password
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.ID, "username"))).send_keys(self.username)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.ID, "password"))).send_keys(self.password)
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                (By.XPATH, '//button[@class="btn__primary--large from__button--floating"]'))).click()
            # Save the cookies after logging in
            self.save_cookies()

    # Asynchronous method to extract text
    async def extract_text(self):
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            # Run the synchronous text extraction implementation in a separate thread
            await loop.run_in_executor(executor, self._extract_text_impl)

    # Synchronous method to extract text
    def _extract_text_impl(self):
        # Open the keywords.json file
        with open('keywords.json', 'r', encoding='utf-8') as f:
            # Load keywords from the file
            data = json.load(f)
            keywords = data['keywords']

        # Choose a random keyword
        keyword = random.choice(keywords)
        # Construct the search URL
        url = f'https://www.linkedin.com/search/results/content/?keywords={keyword}&sortBy=%22date_posted%22'
        # Open the search URL
        self.driver.get(url)
        SCROLL_PAUSE_TIME = 2
        scroll_count = 0

        # Scroll the page to load the search results
        while scroll_count < 7:
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            scroll_count += 1

        # Get the text elements from the search results
        elements = self.driver.find_elements(
            By.CSS_SELECTOR, 'div > div.feed-shared-update-v2__description-wrapper.mr2 > div.feed-shared-inline-show-more-text.feed-shared-update-v2__description.feed-shared-inline-show-more-text--minimal-padding > div > span > span > span')
        for i, element in enumerate(elements):
            # Print each text element - Just for testing purposes
            print(element.text)
            print("___________")
            print(i)

    # Asynchronous method to quit WebDriver
    async def quit(self):
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            # Run the synchronous quit implementation in a separate thread
            await loop.run_in_executor(executor, self._quit_impl)

    # Synchronous method to quit WebDriver
    def _quit_impl(self):
        print("Browser session ended")
        self.driver.quit()


# Instantiate LinkedIn class
linkedin = LinkedIn()

# Get the current event loop
loop = asyncio.get_event_loop()
try:
    # Run the login method
    loop.run_until_complete(linkedin.login())
    # Run the text extraction method
    loop.run_until_complete(linkedin.extract_text())
    # Wait for 20 seconds
    time.sleep(20)
finally:
    # Always quit the WebDriver to clean up
    loop.run_until_complete(linkedin.quit())
