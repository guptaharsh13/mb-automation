from dotenv import dotenv_values
import sendgrid
from sendgrid.helpers.mail import Mail
import logging


u_format = "[%(asctime)s]\t%(name)s | Line number - %(lineno)d | %(levelname)s | %(message)s"


config = dotenv_values(".env")
try:
    email_id = config["email_id"]
    sendgrid_apikey = config["sendgrid_apikey"]
except Exception as e:
    logging.basicConfig(
        filename="app.log", format=u_format, level=logging.INFO)
    logging.critical("Improperly Configured Environment")
    exit(0)


sg = sendgrid.SendGridAPIClient(sendgrid_apikey)


def sendEmail(subject, html):
    message = Mail(
        from_email=email_id,
        to_emails=["mail2bbo@gmail.com", "hg242322@gmail.com"],
        subject=subject,
        html_content=html,
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
