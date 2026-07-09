import logging
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep

from src.settings import Settings

settings = Settings()
logger = logging.getLogger(__name__)

class Authenticator:
    """Class that handles the authentication to the CROUS website and returns a WebDriver object that is authenticated."""

    def __init__(self, email: str, password: str, delay: int = 4):
        self.email = email
        self.password = password
        self.delay = delay 

    def authenticate_driver(self, driver: WebDriver) -> None:
        logger.info("Authenticating to the CROUS website...")
        sleep(self.delay)

        logger.info("Going to the login gateway...")
        driver.get("https://trouverunlogement.lescrous.fr/mse/discovery/connect")
        sleep(self.delay)

        try:
            logger.info("Checking for intermediate buttons...")
            mse_connect_button = driver.find_element(By.CLASS_NAME, "loginapp-button")
            driver.execute_script("arguments[0].click();", mse_connect_button)
            sleep(self.delay)
        except:
            pass 
            
        try:
            connexion_btn = driver.find_element(By.PARTIAL_LINK_TEXT, "Connexion")
            driver.execute_script("arguments[0].click();", connexion_btn)
            sleep(self.delay)
        except:
            pass

        # --- LA MODIFICATION EST ICI ---
        logger.info("Inputting credentials")
        
        # On cherche les cases par leur type (email, text, password) et non plus par leur nom
        username_input = driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[type='text']")
        password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")

        username_input.send_keys(self.email)
        password_input.send_keys(self.password)

        logger.info("Submitting the form")
        password_input.send_keys(Keys.RETURN)
        sleep(self.delay)
        # -------------------------------

        try:
            self._validate_rules(driver)
        except:
            pass

        driver.get("https://trouverunlogement.lescrous.fr/mse/discovery/connect")
        sleep(self.delay)

        logger.info("Successfully authenticated to the CROUS website")

    def _validate_rules(self, driver: WebDriver) -> None:
        logger.info("Validating the rules of the CROUS website")
        driver.get("https://trouverunlogement.lescrous.fr/tools/36/rules")
        sleep(self.delay)
        
        try:
            validate_button = driver.find_element(By.NAME, "searchSubmit")
            validate_button.click()
            sleep(self.delay)
        except:
            pass

