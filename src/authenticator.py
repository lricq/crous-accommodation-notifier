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

        # --- NOUVELLE ÉTAPE : LE PASSAGE DE L'AIGUILLAGE ---
        logger.info("Recherche du bouton d'aiguillage (Dispatcher)...")
        
        # 1. On tente de cliquer sur les textes les plus courants du nouveau site
        mots_cles = ["MesServices", "S'identifier", "Connexion", "Se connecter", "etudiant.gouv"]
        for mot in mots_cles:
            try:
                bouton = driver.find_element(By.PARTIAL_LINK_TEXT, mot)
                driver.execute_script("arguments[0].click();", bouton)
                sleep(self.delay)
                logger.info(f"Bouton contenant '{mot}' trouvé et cliqué !")
                break # Le clic a marché, on sort de la boucle
            except:
                pass

        # 2. On tente avec les noms de code techniques au cas où
        try:
            bouton_tech = driver.find_element(By.CSS_SELECTOR, ".loginapp-button, #idp-mse, button[value='mse'], a.fr-btn")
            driver.execute_script("arguments[0].click();", bouton_tech)
            sleep(self.delay)
        except:
            pass
        # ---------------------------------------------------

        logger.info("Inputting credentials")
        
        try:
            username_input = driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[type='text']")
            password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")

            username_input.send_keys(self.email)
            password_input.send_keys(self.password)

            logger.info("Submitting the form")
            password_input.send_keys(Keys.RETURN)
            sleep(self.delay)
        except Exception as e:
            logger.error("Échec : Le bot n'a pas réussi à passer l'aiguillage.")
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
