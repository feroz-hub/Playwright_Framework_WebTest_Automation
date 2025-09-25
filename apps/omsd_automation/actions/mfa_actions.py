from apps.omsd_automation.actions.base_actions import BaseActions
from apps.omsd_automation.pages.mfa_page import MFAPage
from utils.otp_utils import fetch_otp_from_email


class MFAActions(BaseActions):
    def __init__(self, page: MFAPage, logger=None):
        super().__init__(logger=logger)
        self.mfa_page = page

    def complete_mfa(self) -> None:
        if self.mfa_page.is_mfa_required():
            self.mfa_page.select_email_mfa()
            self.mfa_page.click_continue_mfa()
            self.mfa_page.click_send_verification_code()
            otp = fetch_otp_from_email()
            self.mfa_page.enter_otp_code(otp)
            self.mfa_page.click_verify_code()
            self.mfa_page.click_final_continue()
