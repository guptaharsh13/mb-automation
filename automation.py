from otpAutomation import getOtp
from dotenv import dotenv_values
from logger_config import configLogger

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common import exceptions
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from pyvirtualdisplay import Display


automationLogger = configLogger(__name__)


config = dotenv_values(".env")
try:
    python_env = config["python_env"]
    user_agent = config["user_agent"]
    mb_url = config["mb_url"]
    email_id = config["email_id"]
except Exception as e:
    automationLogger.exception("Improperly Configured Environment")
    exit(0)


# we may also set webdriver.chrome.driver in env
def initializeDriver():
    chrome_options = Options()

    if python_env == "production":

        display = Display(visible=0, size=(1920, 1080))
        display.start()

        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("window-size=1920x1080")
        chrome_options.add_argument(f"user-agent={user_agent}")

    chrome_options.add_argument("disable-notifications")
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    driver.implicitly_wait(20)

    return driver


def configure(driver, button_id):
    name_value = "Roy Bob"
    name = driver.find_element_by_id(f"username{button_id}")
    name.send_keys(name_value)
    automationLogger.info(f"Automatic input: name - {name_value}")

    email_input = driver.find_element_by_id(f"userEmail{button_id}")
    email_input.send_keys(email_id)
    automationLogger.info(f"Automatic input: email - {email_id}")

    country_code = Select(driver.find_element_by_id(
        f"selectCountry_mobile_{button_id}"))
    country_code.select_by_visible_text("USA +1")
    automationLogger.info("Automatic select: country code - USA +1")

    mobile_number = 3213995857
    mobile = driver.find_element_by_id(f"userMobile{button_id}")
    mobile.send_keys(mobile_number)
    automationLogger.info(f"Automatic input: mobile number - {mobile_number}")

    contact_btn = driver.find_element_by_id("showContactButtonTextMob")
    contact_btn.click()
    automationLogger.info("successfully requested otp on email")

    c = 0
    otp_found = False
    while c <= 1:
        otp = getOtp()
        if not otp == -1:
            otp_found = True
            break
        driver.find_element_by_xpath("//div[@id='smsCodeSent']/a").click()
        automationLogger.info("click: Resend otp")
        c += 1

    if not otp_found:
        raise Exception("Could not find otp")

    otp_input = driver.find_element_by_id("smsNo")
    otp_input.send_keys(otp)
    automationLogger.info(f"Automatic input: otp - {otp}")

    verify_btn = driver.find_element_by_xpath(
        "//input[@id='smsNo']//parent::div//following-sibling::div/a")
    verify_btn.click()
    automationLogger.info("requested otp verification (may be successful)")

    wait = configWait(driver)

    rating = wait.until(expected_conditions.element_to_be_clickable(
        (By.XPATH, "//span[@class='npsCloseBtn']")))
    rating.click()
    automationLogger.info("Rating popup closed successfully")


def configWait(driver):
    wait = WebDriverWait(driver, 30, poll_frequency=1, ignored_exceptions=[
        exceptions.ElementClickInterceptedException,
        exceptions.ElementNotInteractableException,
        exceptions.ElementNotSelectableException,
        exceptions.ElementNotVisibleException,
        exceptions.NoSuchElementException,
        exceptions.TimeoutException
    ])
    return wait
