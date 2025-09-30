from providers.mfa_code_provider import IMFACodeProvider
from utils.otp_utils import fetch_otp_from_email


class EmailCodeProvider(IMFACodeProvider):
    def get_mfa_code(self, user: str) -> str:
        code = fetch_otp_from_email()
        return code