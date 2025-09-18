from playwright.sync_api import Page
from omsd_automation.pages.base_page import BasePage
from omsd_automation.pages.home_page import HomePage  # For action chaining


class LoginPage(BasePage):
    """Page Object for the Login Page with all locators, actions, and verifications."""

    # ----------------------------------------------------------------
    # Locators (constants with _LOCATOR suffix)
    # ----------------------------------------------------------------
    USERNAME_INPUT_LOCATOR = "#signInName"
    PASSWORD_INPUT_LOCATOR = "#password"
    NEXT_BUTTON_LOCATOR = "#next"
    FORGOT_PASSWORD_LINK_LOCATOR = "#forgotPassword"
    LOGIN_ERROR_MESSAGE_LOCATOR = "div.error[data-testid='login-error']"

    # ----------------------------------------------------------------
    # Constructor
    # ----------------------------------------------------------------
    def __init__(self, page: Page):
        super().__init__(page)

    # ----------------------------------------------------------------
    # Business Action Methods
    # ----------------------------------------------------------------
    def login(self, username: str, password: str, test_case_id: str = None) -> HomePage:
        """
        Perform login with given credentials, mask password in logs, and take screenshot.
        Returns HomePage object for action chaining.

        :param username: User email/ID
        :param password: User password (masked in logs)
        :param test_case_id: Test case identifier for screenshot naming
        :return: HomePage
        """
        self.do_fill(self.USERNAME_INPUT_LOCATOR, username)
        self.do_fill(self.PASSWORD_INPUT_LOCATOR, password)
        self.do_click(self.NEXT_BUTTON_LOCATOR)
        self.take_screenshot(step_name="after_login", test_case=test_case_id)
        return HomePage(self.page)

    def navigate_to_forgot_password(self, test_case_id: str = None):
        """
        Navigate to the forgotten password page and take a screenshot.

        :param test_case_id: Test case identifier for screenshot naming
        """
        self.do_click(self.FORGOT_PASSWORD_LINK_LOCATOR)
        self.take_screenshot(step_name="forgot_password", test_case=test_case_id)

    # ----------------------------------------------------------------
    # Verification Methods
    # ----------------------------------------------------------------
    def verify_login_error(self, expected_text: str):
        """
        Verify that the login error message is visible and contains the expected text.

        :param expected_text: Text expected in the error message
        """
        error_element = self.page.locator(self.LOGIN_ERROR_MESSAGE_LOCATOR)
        if error_element.is_visible():
            actual_text = error_element.inner_text()
            result = expected_text in actual_text
            self.logger.log_verification(
                f"Login error message contains '{expected_text}'", result
            )
            return result
        self.logger.log_verification("Login error message not visible", False)
        return False
