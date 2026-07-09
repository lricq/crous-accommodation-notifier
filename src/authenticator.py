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
        self.delay = delay 

    def authenticate_driver(self, driver: WebDriver) -> None:
        logger.info("Authenticating to the CROUS website...")
        sleep(self.delay)

        logger.info("Going to the login gateway...")
        driver.get("https://trouverunlogement.lescrous.fr/mse/discovery/connect")
        sleep(self.delay)

        logger.info("Recherche du vrai bouton d'aiguillage...")
        
        try:
            # On récupère tous les liens de la page
            liens = driver.find_elements(By.TAG_NAME, "a") + driver.find_elements(By.TAG_NAME, "button")
            for lien in liens:
                texte = lien.text.lower()
                href = lien.get_attribute("href") or ""
                
                # GRÂCE AU RADAR : on sait exactement quoi chercher !
                if "connexion" in texte or "oauth2/login" in href:
                    # On évite le lien de mot de passe oublié qui contient aussi le mot "connexion"
                    if "courriel" not in href:
                        driver.execute_script("arguments[0].click();", lien)
                        logger.info(f"Bouton EXACT trouvé et cliqué ! (Texte: '{texte}')")
                        sleep(self.delay)
                        break
        except Exception as e:
            logger.warning(f"Erreur lors du clic : {e}")

        logger.info("Inputting credentials")
        
        try:
            # On cherche les cases avec notre méthode infaillible
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

        # On force le rafraîchissement
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
