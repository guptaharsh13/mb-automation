from dotenv import dotenv_values
import sendgrid
from sendgrid.helpers.mail import Mail
from logger_config import configLogger


emailLogger = configLogger(__name__)


config = dotenv_values(".env")
try:
    email_id = config["email_id"]
    sendgrid_apikey = config["sendgrid_apikey"]
except:
    emailLogger.critical("Improperly Configured Environment")
    exit(0)


def sendEmail(subject, html):
    try:
        sg = sendgrid.SendGridAPIClient(sendgrid_apikey)
    except:
        emailLogger.critical(
            "Connection to sendgrid api unsuccessful (maybe due to an improper api key)")
    message = Mail(
        from_email=email_id,
        to_emails=["mail2bbo@gmail.com", "hg242322@gmail.com"],
        subject=subject,
        html_content=html,
    )
    try:
        response = sg.send(message)
        emailLogger.info(f"Email sent with status code {response.status_code}")
        emailLogger.debug(response.body)
        emailLogger.debug(response.headers)
    except:
        emailLogger.exception("Something went wrong")
        exit(0)
