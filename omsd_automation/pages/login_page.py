# file: pages/login_page.py

from __future__ import annotations
from playwright.sync_api import Page
from omsd_automation.pages.base_page import BasePage

class LoginPage(BasePage):
    """
    Page Object for the Login page.

    This class encapsulates UI elements and low-level interactions.
    It has no knowledge of business workflows or logging.
    """
    # --- Locators ---
    USERNAME_INPUT = "#signInName"
    PASSWORD_INPUT = "#password"
    NEXT_BUTTON = "#next"
    FORGOT_PASSWORD_LINK = "#forgotPassword"

    def __init__(self, page: Page):
        """Initializes the LoginPage with the Playwright Page and inherits from BasePage."""
        super().__init__(page)

    # --- Navigation ---
    def open(self, url: str) -> "LoginPage":
        """Opens the login page URL and returns self for chaining."""
        self.go_to(url)
        return self

    # --- UI Interaction Methods ---

    def enter_username(self, username: str) -> LoginPage:
        """Enters text into the username input field."""
        self.do_fill(self.USERNAME_INPUT, username)
        return self

    def enter_password(self, password: str) -> LoginPage:
        """Enters text into the password input field."""
        self.do_fill(self.PASSWORD_INPUT, password)
        return self

    def click_next(self) -> None:
        """Clicks the 'Next' button."""
        self.do_click(self.NEXT_BUTTON)

    def click_forgot_password(self) -> None:
        """Clicks the 'Forgot Password' link."""
        self.do_click(self.FORGOT_PASSWORD_LINK)