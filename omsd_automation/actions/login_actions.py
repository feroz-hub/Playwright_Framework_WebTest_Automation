# file: actions/login_actions.py
from omsd_automation.pages.login_page import LoginPage
from omsd_automation.utils.logger_utils import setup_test_logger


class LoginActions:
    """
    Orchestrates LoginPage methods into reusable business workflows.

    This class contains all logging and workflow logic, keeping the
    Page Object and tests clean.
    """
    def __init__(self, login_page: LoginPage, base_url: str | None = None):
        """Initializes the actions with a LoginPage instance.

        Args:
            login_page: Page object for login interactions.
            base_url: Optional base URL of the AUT to support post-login navigation.
        """
        self.login_page = login_page
        self.base_url = base_url
        self.logger = setup_test_logger("LoginActions")

    def open_login_page(self, url: str) -> None:
        """Opens the login page URL."""
        self.logger.log_action(f"Opening login page: {url}")
        self.login_page.open(url)

    def login(self, username: str, password: str) -> None:
        """
        Performs the full login workflow.

        This method logs the high-level business action and uses the
        LoginPage to interact with the UI.
        """
        self.logger.log_info(f"Attempting to log in as user: '{username}'")
        try:
            self.login_page.enter_username(username).enter_password(password)
            self.login_page.click_next()
            self.logger.log_info("Login form submitted successfully.")

            # Best-effort: wait for the app home page after IDP redirect.
            # If not redirected, navigate directly to the known landing page.
            try:
                # Match the correct post-login landing page
                self.login_page.page.wait_for_url("**/Home/ProductCategory**", timeout=5000)
            except Exception:
                if self.base_url:
                    target = self.base_url.rstrip("/") + "/Home/ProductCategory"
                    self.logger.log_action(f"Navigating to expected home page: {target}")
                    self.login_page.open(target)
        except Exception as e:
            self.logger.log_error(f"An error occurred during the login process: {e}")
            # Optionally, take a screenshot on failure
            # self.login_page.take_screenshot("login_error")
            raise

    def is_logged_in(self, timeout_ms: int = 10000) -> bool:
        """Verifies if the user is logged in by checking presence of user profile element."""
        selector = "#sysUserDisplayName"
        visible = self.login_page.wait_for_element(selector, state="visible", timeout=timeout_ms)
        self.logger.log_verification("User appears to be logged in", result=visible)
        return visible

    def navigate_to_forgot_password(self) -> None:
        """Navigates to the forgot password page."""
        self.logger.log_action("Navigating to the 'Forgot Password' page.")
        self.login_page.click_forgot_password()

    def get_error_message(self) -> str:
        """Best-effort retrieval of an error message on the login screen.

        Tries a set of common selectors used by IDP/B2C pages and our app.
        Returns an empty string if no obvious error element is found.
        """
        candidates = [
            "[role='alert']",
            "#errorMessage",
            ".errorMessage",
            ".alert-error",
            "div[aria-live='assertive']",
            "#claimVerificationServerError",
        ]
        for sel in candidates:
            try:
                if self.login_page.is_visible(sel):
                    return self.login_page.do_get_text(sel)
            except Exception:
                continue
        return ""