from apps.omsd_automation.pages.base_page import BasePage
from apps.omsd_automation.pages.mfa_page import MFAPage
from apps.omsd_automation.strategies.mfa_strategy import IMFAStrategy
from utils.otp_utils import fetch_otp_from_email


class EmailMFAStrategy(IMFAStrategy):

    def complete_mfa(self, page: BasePage, code: str) -> None:
        mfa = MFAPage(page.page)
        mfa.select_email_mfa()
        mfa.click_continue_mfa()
        mfa.click_send_verification_code()
        otp = fetch_otp_from_email()
        mfa.enter_otp_code(otp)
        mfa.click_verify_code()
        mfa.click_final_continue()