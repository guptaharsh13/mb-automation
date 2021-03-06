import logging
from datetime import datetime
from dotenv import dotenv_values
import sendgrid
from sendgrid.helpers.mail import Mail
from pymongo import MongoClient


u_format = "[%(asctime)s]\t%(name)s | Line number - %(lineno)d | %(levelname)s | %(message)s"


config = dotenv_values(".env")
try:
    email_id = config["email_id"]
    sendgrid_apikey = config["sendgrid_apikey"]
    mongodb_url = config["mongodb_url"]
except:
    logging.basicConfig(
        filename="app.log", format=u_format)
    logging.critical("Improperly Configured Environment")
    exit(0)


try:
    connection = MongoClient(mongodb_url)
    db = connection.get_database("magicbricks")
    collection = db.get_collection("logs")
except:
    logging.basicConfig(
        filename="app.log", format=u_format)
    logging.critical("Connection to mongodb failed")
    exit(0)


def sendEmail(subject, body):
    try:
        sg = sendgrid.SendGridAPIClient(sendgrid_apikey)
    except:
        logging.basicConfig(filename="app.log",
                            format=u_format, level=logging.INFO)
        logging.critical(
            "Connection to sendgrid api unsuccessful (maybe due to an improper api key)")
    message = Mail(
        from_email=email_id,
        to_emails=["hg242322@gmail.com"],
        subject=subject,
        plain_text_content=body,
    )
    try:
        response = sg.send(message)
        logging.basicConfig(
            filename="app.log", format=u_format, level=logging.INFO)
        logging.info(f"Email sent with status code {response.status_code}")
        logging.debug(response.body)
        logging.debug(response.headers)
    except:
        logging.basicConfig(
            filename="app.log", format=u_format, level=logging.INFO)
        logging.exception("Something went wrong")
        exit(0)


class EmailHandler(logging.StreamHandler):

    def emit(self, record):

        msg = self.format(record)
        sendEmail(subject="Logs from mb automation script", body=msg)


class MongoHandler(logging.StreamHandler):

    def emit(self, record):
        collection.insert_one({
            "asctime": datetime.now(),
            "name": record.name,
            "lineno": record.lineno,
            "levelname": record.levelname,
            "message": record.message
        })


def configLogger(name, filename="app.log"):

    u_format = logging.Formatter(
        "[%(asctime)s]\t%(name)s | Line number - %(lineno)d | %(levelname)s | %(message)s")

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(filename)
    f_handler.setLevel(logging.INFO)
    email_handler = EmailHandler()
    email_handler.setLevel(logging.ERROR)
    mongo_handler = MongoHandler()
    mongo_handler.setLevel(logging.ERROR)

    c_handler.setFormatter(u_format)
    f_handler.setFormatter(u_format)
    email_handler.setFormatter(u_format)
    mongo_handler.setFormatter(u_format)

    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
    logger.addHandler(email_handler)
    logger.addHandler(mongo_handler)

    return logger
