import imaplib
import email
from email import message_from_bytes
from email.message import Message
import re
import time
from typing import Dict
from config.config_manager import config


def _parse_email_body(msg: Message) -> str:
    """Helper function to extract the text body from an email message."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode(errors="ignore")
    else:
        return msg.get_payload(decode=True).decode(errors="ignore")
    return ""
def fetch_otp_from_email() -> str:
    """
    Fetch OTP code from email using IMAP based on MFA configuration.

    Returns:
        str: OTP code extracted from email

    Raises:
        TimeoutError: If OTP email is not received within the configured timeout
    """
    mfa_config: Dict = config.get_mfa_config()
    email_cfg = mfa_config.get("email", {})

    server = email_cfg.get("server")
    port = email_cfg.get("port", 993)
    username = email_cfg.get("username")
    password = email_cfg.get("password")
    subject_filter = email_cfg.get("subject_filter", "Your OTP Code")
    otp_regex = email_cfg.get("otp_regex", r"\b\d{6}\b")
    timeout = email_cfg.get("timeout", 60)
    if not all([server, username, password, subject_filter]):
        raise ValueError("MFA email configuration is incomplete. Check server, username, password, and subject_filter.")
    mail = None
    try:
        # 1. Connect and login

        mail = imaplib.IMAP4_SSL(server,port)
        mail.login(username, password)
        mail.select("inbox")

        # 2. Poll for the email
        end_time = time.time() + timeout
        while time.time() < end_time:
            result, data = mail.search(None, f'(UNSEEN SUBJECT "{subject_filter}")')
            email_ids = data[0].split()

            if email_ids:
                latest_email_id = email_ids[-1]

                _, msg_data = mail.fetch(latest_email_id, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])

                body = _parse_email_body(msg)
                match = re.search(otp_regex, body)

                if match:
                    otp = match.group(0)
                    return otp

            time.sleep(5)  # Wait before polling again

        # 3. Handle timeout

        raise TimeoutError("OTP email not received within the configured timeout.")

    except imaplib.IMAP4.error as e:

        raise ConnectionError(f"IMAP login failed: {e}") from e

    finally:
        # 4. Ensure the connection is always closed
        if mail and mail.state == 'SELECTED':
            mail.logout()