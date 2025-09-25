import imaplib
import email
import re
import time
from typing import Dict
from config.config_manager import get_mfa_config

def fetch_otp_from_email() -> str:
    """
    Fetch OTP code from email using IMAP based on MFA configuration.

    Returns:
        str: OTP code extracted from email

    Raises:
        TimeoutError: If OTP email is not received within the configured timeout
    """
    mfa_config: Dict = get_mfa_config()
    email_cfg = mfa_config.get("email", {})

    server = email_cfg.get("server")
    port = email_cfg.get("port", 993)
    username = email_cfg.get("username")
    password = email_cfg.get("password")
    subject_filter = email_cfg.get("subject_filter", "Your OTP Code")
    otp_regex = email_cfg.get("otp_regex", r"\b\d{6}\b")
    timeout = email_cfg.get("timeout", 60)

    # Connect to IMAP server
    mail = imaplib.IMAP4_SSL(server, port)
    mail.login(username, password)
    mail.select("inbox")

    end_time = time.time() + timeout
    while time.time() < end_time:
        result, data = mail.search(None, f'(UNSEEN SUBJECT "{subject_filter}")')
        if result == "OK":
            for num in data[0].split():
                result, msg_data = mail.fetch(num, "(RFC822)")
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body += part.get_payload(decode=True).decode(errors="ignore")
                else:
                    body = msg.get_payload(decode=True).decode(errors="ignore")

                match = re.search(otp_regex, body)
                if match:
                    return match.group(0)

        time.sleep(5)

    raise TimeoutError("OTP email not received within the configured timeout.")