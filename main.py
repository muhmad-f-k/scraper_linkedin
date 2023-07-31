# Selenium WebDriver is used for automating web application testing
from selenium import webdriver
# Allows you to locate elements by their attributes
from selenium.webdriver.common.by import By
# Allows you to wait for a certain condition to occur before proceeding with code execution
from selenium.webdriver.support.ui import WebDriverWait
# Collection of pre-built conditions to use with WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# Loads environment variables from a .env file into system's environment variables
from dotenv import load_dotenv
import os  # Provides a way of using operating system dependent functionality
import pickle  # Implements binary protocols for serializing and de-serializing Python object structures
import time  # Provides various time-related functions


# Define LinkedIn class
class LinkedIn:
    LOGIN_URL = "https://www.linkedin.com/login"  # LinkedIn login URL
    # Path to store/load cookies
    COOKIE_PATH = os.path.join(os.getcwd(), 'cookies.pkl')

    def __init__(self):  # Class constructor
        load_dotenv()  # Load environment variables
        self.driver = webdriver.Chrome()  # Initiate Chrome WebDriver
        # Get LinkedIn username from environment variable
        self.username = os.getenv('LINKEDIN_USERNAME')
        # Get LinkedIn password from environment variable
        self.password = os.getenv('LINKEDIN_PASSWORD')

    def load_cookies(self):  # Method to load cookies
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

    def save_cookies(self):  # Method to save cookies
        cookies = self.driver.get_cookies()  # Get cookies from WebDriver
        with open(self.COOKIE_PATH, 'wb') as f:  # Open the file to write in binary mode
            pickle.dump(cookies, f)  # Dump cookies into file
        print('Cookies saved')

    def login(self):  # Method to perform login action
        self.driver.get(self.LOGIN_URL)  # Open LinkedIn login page

        # If no cookies are loaded, perform login operation manually
        if not self.load_cookies():
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.ID, "username"))).send_keys(self.username)  # Wait until username field is present and input username
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.ID, "password"))).send_keys(self.password)  # Wait until password field is present and input password
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(
                (By.XPATH, '//button[@class="btn__primary--large from__button--floating"]'))).click()  # Wait until login button is clickable and click
            self.save_cookies()  # Save cookies after successful login

    def extract_text(self, url):  # Method to extract text from a specific url
        self.driver.get(url)  # Open the url
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id]')))  # Wait until the specified element is present
        element = self.driver.find_element(
            By.XPATH, '//*[@id]//div/div[4]/div[1]/div/span')  # Find the specified element and store it in variable
        print(element.text)  # Print the text of the specified element

    def quit(self):  # Method to quit WebDriver
        print("Browser session ended")
        self.driver.quit()  # Quit the WebDriver session


# Instantiate LinkedIn class
linkedin = LinkedIn()

# Enclose in try-finally block to ensure cleanup even if exception occurs
try:
    linkedin.login()  # Perform login action
    linkedin.extract_text(
        'https://www.linkedin.com/search/results/content/?keywords=recruiter&sortBy=%22date_posted%22')  # Extract text from specified URL
    time.sleep(10)  # Pause execution for 20 seconds
finally:
    linkedin.quit()  # Quit WebDriver session
