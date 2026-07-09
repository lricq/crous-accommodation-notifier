import argparse
import logging
from typing import List

import telepot
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver

from src.authenticator import Authenticator
from src.parser import Parser
from src.models import UserConf
from src.notification_builder import NotificationBuilder
from src.settings import Settings
from src.telegram_notifier import TelegramNotifier

logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)
logger = logging.getLogger("accommodation_notifier")


def load_users_conf() -> List[UserConf]:
    return [
        # --- Strasbourg ---
        UserConf(
            conf_title="Stras",
            telegram_id=settings.MY_TELEGRAM_ID,
            search_url="https://trouverunlogement.lescrous.fr/tools/47/search?maxPrice=50000&occupationModes=alone&bounds=7.745103836059571_48.58881489147136_7.791967391967774_48.56218114207007&locationName=Strasbourg", 
            ignored_ids=[],
        ), # <--- CETTE VIRGULE EST TRÈS IMPORTANTE !
        
        # --- Lyon ---
        UserConf(
            conf_title="Lyon 2",
            telegram_id=settings.MY_TELEGRAM_ID,
            search_url="https://trouverunlogement.lescrous.fr/tools/47/search?minArea=10&occupationModes=alone&bounds=4.816989123583336_45.7528507798946_4.863852679491539_45.72475587562574&locationName=Lyon", 
            ignored_ids=[],
        )
    ]


def create_driver(headless: bool = True) -> WebDriver:
    # Set up Chrome options
    chrome_options = Options()
    if headless:
        logging.info("Running in headless mode")
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-gpu")
    else:
        logging.info("Running in non-headless mode")

    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")

    # --- LE FAMEUX DÉGUISEMENT ---
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36")
    # -----------------------------

    # Initialize the WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    
    # LIGNE À RAJOUTER : On dit au bot d'attendre jusqu'à 10 secondes si la page est lente
    driver.implicitly_wait(10)
    
    return driver
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the script in headless mode or not."
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Run the script without headless mode",
    )

    args = parser.parse_args()

    settings = Settings()
    bot = telepot.Bot(token=settings.TELEGRAM_BOT_TOKEN)
    bot.getMe()  # test if the bot is working

    user_confs = load_users_conf()

    driver = create_driver(headless=not args.no_headless)
    
    # --- ON AJOUTE NOTRE DÉTECTEUR INFAILLIBLE ICI ---
    try:
        Authenticator(settings.MSE_EMAIL, settings.MSE_PASSWORD).authenticate_driver(driver)
    except Exception as erreur:
        logging.error("🚨 LE BOT EST BLOQUÉ ! Voici ce qu'il voit à l'écran :")
        logging.error(f"L'adresse de la page : {driver.current_url}")
        logging.error(f"Le titre de la page : {driver.title}")
        
        # On demande au bot de nous cracher le code source (ça ne plante jamais !)
        try:
            html = driver.page_source
            logging.error(f"--- CODE HTML DE LA PAGE ---\n{html[:4000]}\n------------------------")
        except:
            logging.error("Impossible de lire le code HTML.")
            
        driver.quit()
        raise erreur
    # -------------------------------------------------

    parser = Parser(driver)
    notification_builder = NotificationBuilder()
    notifier = TelegramNotifier(bot)

    for conf in user_confs:
        logging.info(f"Handling configuration : {conf}")
        search_results = parser.get_accommodations(conf.search_url)  # type: ignore
        notification = notification_builder.search_results_notification(search_results)
        if notification:
            notifier.send_notification(conf.telegram_id, notification)

    driver.quit()
