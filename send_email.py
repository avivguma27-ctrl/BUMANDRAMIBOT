import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

EMAIL_USER = "avivguma12@gmail.com"  # תחליף בהתאם למשתנה סביבה שלך
EMAIL_PASS = "fxgqtmhqcrszrzyj"     # סיסמת אפליקציה

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_email(subject: str, body: str, to_email: str, html: bool = False):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = EMAIL_USER
        msg["To"] = to_email

        if html:
            part = MIMEText(body, "html")
        else:
            part = MIMEText(body, "plain")

        msg.attach(part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, to_email, msg.as_string())

        logging.info(f"Email sent successfully to {to_email}")

    except Exception as e:
        logging.error(f"Failed to send email to {to_email}: {e}")
