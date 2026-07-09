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
        self.delay = delay # On donne quelques secondes au bot pour ne pas brusquer la page

    def authenticate_driver(self, driver: WebDriver) -> None:
        logger.info("Authenticating to the CROUS website...")
        sleep(self.delay)

        # Étape 1 : On va directement sur la page de connexion officielle des logements
        logger.info("Going to the login gateway...")
        driver.get("https://trouverunlogement.lescrous.fr/mse/discovery/connect")
        sleep(self.delay)

        # Étape 2 : On essaie de cliquer sur les vieux boutons (s'ils existent encore)
        try:
            logger.info("Checking for intermediate buttons...")
            mse_connect_button = driver.find_element(By.CLASS_NAME, "loginapp-button")
            driver.execute_script("arguments[0].click();", mse_connect_button)
            sleep(self.delay)
        except:
            pass # Si le bouton n'existe plus, on ignore l'erreur
            
        try:
            connexion_btn = driver.find_element(By.PARTIAL_LINK_TEXT, "Connexion")
            driver.execute_script("arguments[0].click();", connexion_btn)
            sleep(self.delay)
        except:
            pass

        # Étape 3 : On remplit le formulaire de connexion
        logger.info("Inputting credentials")
        
        # Le site utilise parfois de nouveaux noms pour les cases, on teste les deux versions
        try:
            username_input = driver.find_element(By.NAME, "username")
        except:
            username_input = driver.find_element(By.NAME, "j_username")
            
        try:
            password_input = driver.find_element(By.NAME, "password")
        except:
            password_input = driver.find_element(By.NAME, "j_password")

        username_input.send_keys(self.email)
        password_input.send_keys(self.password)

        logger.info("Submitting the form")
        password_input.send_keys(Keys.RETURN)
        sleep(self.delay)

        # Étape 4 : Validation du règlement (avec sécurité pour ne pas planter)
        try:
            self._validate_rules(driver)
        except:
            pass

        # Étape 5 : On force la validation
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


