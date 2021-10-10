import easyimap
from dotenv import dotenv_values
from bs4 import BeautifulSoup
import time
from logger_config import configLogger


def findOtp():
    global imapper
    global found
    emails = imapper.unseen(10)
    if emails:
        for email in emails:
            if email.from_addr == "support@magicbricks.com":
                soup = BeautifulSoup(email.body, "lxml")
                otp = soup.find("strong").get_text()
                found = True
                otpLogger.info("otp found successfully")
                return int(otp)
    otpLogger.debug("otp could not be found successfully (return -1)")
    return -1


def keepTrying():
    global found
    temp = time.time()
    while not found and (time.time() - temp <= 185):
        time.sleep(1)
        otpLogger.debug("function called: findOtp()")
        otp = findOtp()
        if not otp == -1:
            return otp
    otpLogger.error(
        "unsuccesful attempt: otp from email (return -1)")
    return -1


imapper = None
found = False
otpLogger = configLogger(__name__)


def getOtp():
    global imapper
    global found
    config = dotenv_values(".env")
    try:
        imapper = easyimap.connect(
            "imap.gmail.com", config["email_id"], config["password"])
        otpLogger.info("imap connection for otp successful")
    except Exception as e:
        otpLogger.exception(
            "Improperly Configured Environment (imap connection for otp unsuccessful)")
        exit(0)

    found = False
    otp = keepTrying()
    imapper.quit()
    return otp
