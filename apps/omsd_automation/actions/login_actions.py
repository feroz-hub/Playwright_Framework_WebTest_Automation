# file: actions/login_actions.py
from apps.omsd_automation.actions.base_actions import BaseActions
from apps.omsd_automation.pages.login_page import LoginPage


class LoginActions(BaseActions):
    """
    Orchestrates LoginPage methods into reusable business workflows.

    This class contains all logging and workflow logic, keeping the
    Page Object and tests clean.
    """
    def __init__(self, login_page: LoginPage | None = None, logger=None):
        """Initializes the actions with a LoginPage instance.

        Args:
            login_page: Page object for login interactions.
        """
        super().__init__(logger)
        self.login_page = login_page

    # def open_login_page(self, url: str) -> None:
    #     """Opens the login page URL."""
    #     self.logger.log_action(f"Opening login page: {url}")
    #     self.login_page.open(url)

    def login(self, username: str, password: str) -> None:
        """
        Performs the full login workflow with specific error handling.
        """
        self.logger.log_info(f"Attempting to log in as user: '{username}'")
        try:
            self.login_page.enter_username(username)
            self.login_page.enter_password(password)
            self.login_page.click_next()
            self.take_screenshot(test_case="SC_01")
            # if self.login_page.is_mfa_required():
            #     if
            self.logger.log_info("Login form submitted successfully.")
        except Exception as e:
            # This broad catch is acceptable here ONLY because we log and re-raise.
            # This ensures the test fails correctly while providing a useful error message and screenshot.
            self.logger.log_error(f"A critical error occurred during the login process: {e}")
            # self.login_page.take_screenshot("login_failure")
            raise  # ✅ Re-raising the exception is crucial to fail the test.

    def is_logged_in(self, timeout_ms: int = 10000) -> bool:
        """Verifies if the user is logged in by checking the presence of a user profile element."""
        selector = "#sysUserDisplayName"
        visible = self.login_page.wait_for_element(selector, state="visible", timeout=timeout_ms)
        self.logger.log_verification("User appears to be logged in", result=visible)
        return visible

    def navigate_to_forgot_password(self) -> None:
        """Navigates to the forgot password page."""
        self.logger.log_action("Navigating to the 'Forgot Password' page.")
        self.login_page.click_forgot_password()
