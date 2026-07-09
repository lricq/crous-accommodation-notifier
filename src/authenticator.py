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

    def __init__(self, email: str, password: str, delay: int = 8):
        self.email = email
        self.password = password
        self.delay = delay # On augmente à 8 secondes car la page de connexion est lente

    def authenticate_driver(self, driver: WebDriver) -> None:
        logger.info("Authenticating to the CROUS website...")
        sleep(self.delay)

        logger.info("Going to the login gateway...")
        driver.get("https://trouverunlogement.lescrous.fr/mse/discovery/connect")
        sleep(self.delay)

        logger.info("Vérification de l'aiguillage...")
        try:
            liens = driver.find_elements(By.TAG_NAME, "a") + driver.find_elements(By.TAG_NAME, "button")
            for lien in liens:
                texte = lien.text.lower()
                href = lien.get_attribute("href") or ""
                if "connexion" in texte or "oauth2/login" in href:
                    if "courriel" not in href and "logo" not in lien.get_attribute("class").lower():
                        driver.execute_script("arguments[0].click();", lien)
                        logger.info(f"Bouton d'aiguillage cliqué ! (Texte: '{texte}')")
                        sleep(self.delay)
                        break
        except:
            pass

        logger.info("Recherche intelligente des cases du formulaire...")
        
        try:
            # Le bot va lister absolument TOUTES les cases de la page
            tous_les_inputs = driver.find_elements(By.TAG_NAME, "input")
            
            for inp in tous_les_inputs:
                logger.info(f"🔍 Case trouvée à l'écran - Type: '{inp.get_attribute('type')}', Nom: '{inp.get_attribute('name')}'")

            # On cherche la bonne case pour l'email
            username_input = None
            for inp in tous_les_inputs:
                typ = inp.get_attribute("type")
                if typ in ["email", "text"] and typ != "hidden":
                    username_input = inp
                    break
                    
            # On cherche la case du mot de passe
            password_input = None
            for inp in tous_les_inputs:
                if inp.get_attribute("type") == "password":
                    password_input = inp
                    break

            if not username_input or not password_input:
                raise Exception("Cases introuvables sur cette page.")

            logger.info("Cases trouvées ! Remplissage en cours...")
            username_input.send_keys(self.email)
            password_input.send_keys(self.password)

            logger.info("Validation du formulaire...")
            password_input.send_keys(Keys.RETURN)
            sleep(self.delay)
            
        except Exception as e:
            logger.error(f"Échec : {e}")
            raise e

        try:
            self._validate_rules(driver)
        except:
            pass

        # On force la reconnexion
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
