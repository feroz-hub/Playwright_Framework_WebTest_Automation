from playwright.sync_api import Page
from base_page import BasePage
class MFAPage(BasePage):

    MFA_RADIO_EMAIL = 'input[type="radio"][value="Email"]'
    MFA_CONTINUE_BUTTON = 'button:has-text("Continue")'
    MFA_SEND_CODE_BUTTON = 'button:has-text("Send verification code")'
    MFA_CODE_INPUT = 'input[name="Verification code"]'
    MFA_VERIFY_BUTTON = 'button:has-text("Verify code")'
    MFA_FINAL_CONTINUE = 'button:has-text("Continue")'
    MFA_LABEL = 'text=Please select your preferred MFA method'
    MFA_SEND_NEW_CODE_BUTTON = 'button:has-text("Send new code")'
    def __init__(self, page: Page):
        super().__init__(page)

    def is_mfa_required(self) -> bool:
        return self.to_be_visible(self.MFA_LABEL)

    def select_email_mfa(self) -> None:
        self.do_click(self.MFA_RADIO_EMAIL)

    def click_continue_mfa(self) -> None:
        self.do_click(self.MFA_CONTINUE_BUTTON)

    def click_send_verification_code(self) -> None:
        self.do_click(self.MFA_SEND_CODE_BUTTON)

    def enter_otp_code(self, otp: str) -> None:
        self.do_fill(self.MFA_CODE_INPUT, otp)

    def click_verify_code(self) -> None:
        self.do_click(self.MFA_VERIFY_BUTTON)

    def click_final_continue(self) -> None:
        self.do_click(self.MFA_FINAL_CONTINUE)