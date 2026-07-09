import logging
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.settings import Settings

settings = Settings()
logger = logging.getLogger(__name__)

class Authenticator:
    """Class that handles the authentication to the CROUS website."""

    def __init__(self, email: str, password: str, delay: int = 8):
        self.email = email
        self.password = password
        self.delay = delay

    def authenticate_driver(self, driver: WebDriver) -> None:
        logger.info("Authenticating to the CROUS website...")
        sleep(self.delay)

        logger.info("Going to the login gateway...")
        driver.get("https://trouverunlogement.lescrous.fr/mse/discovery/connect")
        sleep(self.delay)

        logger.info("Vérification de l'aiguillage...")
        url_avant_clic = driver.current_url
        
        # --- LA FRAPPE CHIRURGICALE EST ICI ---
        try:
            # On cible directement le nom de code du bouton blanc de ta capture 2
            dispatcher_btn = driver.find_element(By.NAME, "login[app]")
            driver.execute_script("arguments[0].click();", dispatcher_btn)
            logger.info("Bouton 'S'identifier avec MesServices' cliqué !")
        except Exception as e:
            logger.warning(f"Impossible de cliquer sur l'aiguillage : {e}")
        # --------------------------------------

        logger.info("Attente de la redirection vers le formulaire...")
        for _ in range(15): 
            if driver.current_url != url_avant_clic and "login_challenge" not in driver.current_url:
                break
            sleep(1)
        sleep(self.delay)

        logger.info("Recherche intelligente des cases du formulaire...")
        
        try:
            tous_les_inputs = driver.find_elements(By.TAG_NAME, "input")
            
            username_input = None
            password_input = None
            
            for inp in tous_les_inputs:
                typ = inp.get_attribute("type")
                nom = str(inp.get_attribute("name")).lower()
                
                if typ in ["email", "text"] and typ != "hidden" and "username" in nom:
                    username_input = inp
                if typ == "password" and "password" in nom:
                    password_input = inp

            if not username_input or not password_input:
                for inp in tous_les_inputs:
                    if not username_input and inp.get_attribute("type") in ["email", "text"]:
                        username_input = inp
                    if not password_input and inp.get_attribute("type") == "password":
                        password_input = inp

            if not username_input or not password_input:
                raise Exception("Cases introuvables sur la page de destination.")

            logger.info("Cases trouvées ! Remplissage en cours...")
            username_input.send_keys(self.email)
            password_input.send_keys(self.password)

            logger.info("Tentative d'approche du videur (CAPTCHA)...")
            try:
                WebDriverWait(driver, 5).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[title*='reCAPTCHA']")))
                captcha_box = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".recaptcha-checkbox-border")))
                driver.execute_script("arguments[0].click();", captcha_box)
                logger.info("Case 'Je ne suis pas un robot' cliquée !")
                sleep(4) 
                driver.switch_to.default_content()
            except Exception as e:
                logger.warning("Le bot n'a pas pu cliquer sur le CAPTCHA (il n'y en a peut-être pas ou il est bloqué).")
                driver.switch_to.default_content()

            logger.info("Validation du formulaire...")
            try:
                submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
                driver.execute_script("arguments[0].click();", submit_btn)
            except:
                password_input.send_keys(Keys.RETURN)
            sleep(self.delay)
            
        except Exception as e:
            logger.error(f"Échec : {e}")
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
