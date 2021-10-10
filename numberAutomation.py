import re
import easyimap
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from pymongo import MongoClient
from mailer import sendEmail
from logger_config import configLogger


numberLogger = configLogger(__name__)


config = dotenv_values(".env")
try:
    mongodb_url = config["mongodb_url"]
    sendgrid_apikey = config["sendgrid_apikey"]
except Exception as e:
    numberLogger.exception("Improperly Configured Environment")
    exit(0)


try:
    connection = MongoClient(mongodb_url)
    db = connection.get_database("magicbricks")
    collection = db.get_collection("numbers")
except Exception as e:
    numberLogger.exception("Connection to mongodb failed")
    exit(0)


def getNumbers():
    try:
        imapper = easyimap.connect(
            "imap.gmail.com", config["email_id"], config["password"])
        numberLogger.info("imap connection for numberAutomation successful")

    except:
        numberLogger.exception(
            "imap connection for numberAutomation unsuccessful")
        exit(0)
    emails = imapper.unseen(100)
    data = []

    for email in emails:

        if "info@magicbricks.com" in email.from_addr:

            subject = email.title
            soup = BeautifulSoup(email.body, "lxml")
            spans = soup.find_all("span")
            spans = map(lambda span: span.get_text().strip(), spans)
            numbers = list(filter(isNumber, spans))
            numbers = numbers[0]
            content = soup.get_text()
            property_id = re.findall(r"Property ID: (\d+)", content)[0]

            if numbers:
                temp = {
                    "subject": subject,
                    "numbers": numbers,
                    "property_id": property_id
                }
                data.append(temp)
                collection.insert_one(temp)
            else:
                sendEmail(subject, email.body)

    data = map(beautify, data)
    data = "<br><br><hr><br>".join(data)
    if data:
        data = f"Numbers from magicbricks.com -<br><br><br>{data}"
    else:
        data = "No numbers from magicbricks.com"
    sendEmail("Numbers from magicbricks.com", data)
    numberLogger.info("Email successful: numbers sent")
    imapper.quit()


def beautify(data):
    return f"Subject - {data['subject']}<br><br>Numbers -<br>{data['numbers']}<br><br>Property ID - {data['property_id']}"


def isNumber(number):
    if re.search(r"\d+", number):
        return True
    return False


getNumbers()
