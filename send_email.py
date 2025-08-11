import os
import smtplib
from email.mime.text import MIMEText

def send_email(subject, body, to_emails):
    from_email = os.getenv("EMAIL_USER")
    app_password = os.getenv("EMAIL_PASSWORD")

    if not from_email or not app_password:
        print("ERROR: EMAIL_USER or EMAIL_PASSWORD not set in env.")
        return False

    if isinstance(to_emails, str):
        to_emails = [to_emails]

    msg = MIMEText(body, "plain")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = ", ".join(to_emails)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(from_email, app_password)
            server.sendmail(from_email, to_emails, msg.as_string())
        print(f"Email sent to {msg['To']}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

if __name__ == "__main__":
    # לבדיקה מקומית (כאן תעדכן מיילים שלך)
    send_email("Test Email", "This is a test email from bot.", ["youremail@gmail.com", "friend@gmail.com"])
