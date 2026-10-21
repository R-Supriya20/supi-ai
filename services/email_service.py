
import smtplib
from email.message import EmailMessage

from config.settings import settings


def send_otp_email(to_email: str, otp: str) -> None:
    message = EmailMessage()

    message["Subject"] = "Verify Your AI Customer Support Account"
    message["From"] = settings.gmail_address
    message["To"] = to_email

    message.set_content(
        f"""
Hello,

Your email verification OTP is: {otp}

This OTP expires in 10 minutes.

If you did not request this code, please ignore this email.

AI Customer Support Team
"""
    )

    with smtplib.SMTP_SSL(
        "smtp.gmail.com", 465, timeout=20
    ) as smtp:
        smtp.login(
            settings.gmail_address,
            settings.gmail_app_password,
        )
        smtp.send_message(message)