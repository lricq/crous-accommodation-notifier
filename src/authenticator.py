import logging
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep

from src.settings import Settings

settings = Settings()
logger = logging.getLogger(__name__)

class Authenticator:
    """Class that handles the authentication to the CROUS website."""

    def __init__(self, email: str, password: str, delay: int = 5):
        self.email = email
        self.password = password
        self.delay = delay # J'ai augmenté d'une petite seconde pour être sûr que la page charge bien

    def authenticate_driver(self, driver: WebDriver) -> None:
        logger.info("Authenticating to the CROUS website...")
        sleep(self.delay)

        logger.info("Going to the login gateway...")
        driver.get("https://trouverunlogement.lescrous.fr/mse/discovery/connect")
        sleep(self.delay)

        logger.info("Recherche du vrai bouton d'aiguillage...")
        try:
            # On cible UNIQUEMENT les vrais boutons de l'État (fr-btn) ou l'identifiant technique MSE
            boutons = driver.find_elements(By.CSS_SELECTOR, "a.fr-btn, button.fr-btn, #idp-mse, button.loginapp-button")
            for btn in boutons:
                # On vérifie que ce n'est pas le bouton FranceConnect
                if "franceconnect" not in btn.get_attribute("class").lower():
                    driver.execute_script("arguments[0].click();", btn)
                    logger.info("Vrai bouton cliqué !")
                    sleep(self.delay)
                    break
        except:
            pass

        logger.info("Inputting credentials")
        
        try:
            # On cherche les cases avec une méthode ultra-large et robuste
            username_input = driver.find_element(By.CSS_SELECTOR, "input[name*='username'], input[id*='username'], input[type='email']")
            password_input = driver.find_element(By.CSS_SELECTOR, "input[name*='password'], input[id*='password'], input[type='password']")

            username_input.send_keys(self.email)
            password_input.send_keys(self.password)

            logger.info("Submitting the form")
            password_input.send_keys(Keys.RETURN)
            sleep(self.delay)
        except Exception as e:
            logger.error("Échec : Le bot ne trouve pas les cases.")
            raise e

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
