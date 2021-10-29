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
    mb_emails = config["mb_emails"].split()
    nna_emails = config["nna_emails"].split()
except Exception as e:
    numberLogger.exception("Improperly Configured Environment")
    exit(0)

try:
    connection = MongoClient(mongodb_url)
    db = connection.get_database("numbers")
    mb_collection = db.get_collection("magicbricks")
    nna_collection = db.get_collection("99acres")
except Exception as e:
    numberLogger.exception("Connection to mongodb failed")
    exit(0)


def beautify(data):
    return f"Subject - {data['subject']}<br><br>Numbers -<br>{data['numbers']}<br><br>Property ID - {data['property_id']}"


def isNumber(number):
    if re.search(r"\d+", number):
        return True
    return False


def magicbricks():
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
        for mb_email in mb_emails:
            if mb_email in email.from_addr:

                subject = email.title
                try:
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
                        mb_collection.insert_one(temp)
                    else:
                        raise Exception(
                            "email did not contain any number information")
                except:
                    sendEmail(subject, email.body)
                    numberLogger.exception(
                        "email did not contain any number information")

    data = map(beautify, data)
    data = "<br><br><hr><br>".join(data)
    if data:
        data = f"Numbers from magicbricks.com -<br><br><br>{data}"
    else:
        data = "No numbers from magicbricks.com"
    sendEmail("Numbers from magicbricks.com", data)
    numberLogger.info("Email successful: numbers sent")
    imapper.quit()


def extractInfo(content):
    lines = content.split("\n")
    count = 0

    for index, line in enumerate(lines):

        if re.search(r"Property Detail", line):
            prop_index = index
            count += 1

        elif re.search(r"Advertiser details", line):
            adv_index = index
            count += 1

    if count < 2:
        return (None, None)

    prop_details = ""
    adv_details = ""

    for index in range(3):
        prop_details += f"{lines[prop_index + index + 1]}\n"
        adv_details += f"{lines[adv_index + index + 1]}\n"

    return (prop_details, adv_details)


def ninetynineacres():
    try:
        imapper = easyimap.connect(
            "imap.gmail.com", config["email_id"], config["password"])
        numberLogger.info("imap connection for numberAutomation successful")

    except:
        numberLogger.exception(
            "imap connection for numberAutomation unsuccessful")
        exit(0)

    emails = imapper.unseen(10)
    data = "Numbers from 99acres.com -<br><br><br>"
    for email in emails:

        for nna_email in nna_emails:
            if nna_email in email.from_addr:

                prop_details, adv_details = extractInfo(email.body)
                if prop_details and adv_details:

                    temp = adv_details.split()
                    name = temp[0]
                    adv_email = temp[1]
                    number = temp[2]

                    data = f"{data}Property Details -<br>{prop_details}<br><br>Advertiser details -<br>Name - {name}<br>Email - {adv_email}<br>Number - {number}<br><br><br>"

                    nna_collection.insert_one(
                        {"Property Details": prop_details, "Advertiser details": {"name": name, "email": adv_email, "number": number}})

    sendEmail("Numbers from 99accres.com", html=data)
    numberLogger.info("Email send successful: Numbers from 99acres.com")
    imapper.quit()


ninetynineacres()
