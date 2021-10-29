from dotenv import dotenv_values
import time
import re
from datetime import datetime
from pymongo import MongoClient
from mailer import sendEmail
from logger_config import configLogger
from selenium.webdriver.support import expected_conditions
from automation import initializeDriver, configure, configWait
from selenium.webdriver.common.by import By


logger = configLogger(__name__)


config = dotenv_values(".env")
try:
    mongodb_url = config["mongodb_url"]
    mb_url = config["mb_url"]
except Exception as e:
    logger.exception("Improperly Configured Environment")
    exit(0)

try:
    connection = MongoClient(mongodb_url)
    db = connection.get_database("magicbricks")
    collection = db.get_collection("buttons")
except Exception as e:
    logger.exception("Connection to mongodb failed")
    exit(0)


def closePopup(driver):
    wait = configWait(driver)
    close_btn = wait.until(expected_conditions.element_to_be_clickable(
        (By.XPATH, "//div[@class='m-contact']/div[@id='closeContact']")))
    close_btn.click()


def findNumbers(buttons):
    global configured
    global count
    numButtons = len(buttons)

    for button in buttons:

        temp_c = 0

        if count >= aim:
            break

        button_id = button.get_attribute("id")
        button_id = re.findall(r"\d+", button_id)[0]
        if collection.find_one({"button_id": button_id}):
            continue

        time.sleep(duration)
        button.click()
        logger.info(f"click: view property button - number {count}")

        if not configured:
            try:
                configure(driver, button_id)
                configured = True
            except:
                logger.exception(
                    "unsuccessful attempt: configure property - number 1")
                exit(0)

        collection.insert_one(
            {"button_id": button_id, "timestamp": datetime.now()})
        closePopup(driver)
        logger.info("successfully closed popup")
        count += 1
        temp_c += 1

        if temp_c >= numButtons:

            driver.execute_script(
                "window.scrollTo(0,document.body.scrollHeight)")
            logger.info("scroll: end of html document")
            time.sleep(10)

            temp = driver.find_elements_by_xpath(
                "//button[@class='m-srp-card__btn m-srp-card__btn--primary-o get-phone-min-width']")

            logger.info(f"Number of buttons {numButtons}")
            logger.info(f"Number of buttons after scroll - {len(temp)}")
            if len(temp) == numButtons:
                break
            findNumbers(temp)


def setup():
    driver = initializeDriver()
    logger.info("successful: initialized chromedriver")

    driver.get(mb_url)
    logger.info("successful: get magicbricks.com")

    buttons = driver.find_elements_by_xpath(
        "//button[@class='m-srp-card__btn m-srp-card__btn--primary-o get-phone-min-width']")
    if buttons:
        logger.info(f"successful: found {len(buttons)} buttons")
        return (driver, buttons)
    raise Exception("unsuccessful: no buttons were found")


aim = 125
count = 0
duration = 65
configured = False


try:
    driver, buttons = setup()
    findNumbers(buttons)
except:
    logger.exception(
        "Something went wrong in chromedriver setup or findNumbers()")
    exit(0)


logger.info(f"{count} Numbers collected")
sendEmail(f"{count} Numbers collected (from mb.com)",
          "You would recieve an email containing numbers of the property owners soon.")
logger.info(f"Email sent successfully ({count} Numbers collected)")

time.sleep(20)
driver.quit()
