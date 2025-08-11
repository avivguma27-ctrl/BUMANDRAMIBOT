import os

def main():
    print("===== בדיקת סקרטים =====")
    target_emails = os.getenv("TARGET_EMAILS")
    email_user = os.getenv("EMAIL_USER")
    email_password = os.getenv("EMAIL_PASSWORD")
    quiver_api_key = os.getenv("QUIVER_API_KEY")

    print(f"TARGET_EMAILS: {target_emails if target_emails else 'NOT SET'}")
    print(f"EMAIL_USER: {email_user if email_user else 'NOT SET'}")
    print(f"EMAIL_PASSWORD: {'SET' if email_password else 'NOT SET'}")
    print(f"QUIVER_API_KEY: {'SET' if quiver_api_key else 'NOT SET'}")

if __name__ == "__main__":
    main()
