"""Page object for the application's login screen.

This module defines the LoginPage, a Page Object Model (POM) abstraction over
low-level Playwright interactions for the login UI. It exposes fine‑grained
UI actions only (no business workflows, assertions, or logging), keeping a
clear separation between the Page layer and the Actions/tests layers.

Design principles:
- POM: Encapsulates selectors and interactions for maintainability.
- SOLID: Single Responsibility — only low-level UI operations live here.
- DRY: Centralized locators prevent duplication across tests.
"""

from __future__ import annotations

from typing import ClassVar

from playwright.sync_api import Page

from apps.omsd_automation.pages.base_page import BasePage


class LoginPage(BasePage):
    """Page Object for the Login page.

    The LoginPage provides typed locators and small, composable methods that wrap
    Playwright calls. It deliberately avoids business logic and logging to keep
    responsibilities focused and test code readable.

    Attributes:
        USERNAME_INPUT: CSS selector for the username field.
        PASSWORD_INPUT: CSS selector for the password field.
        NEXT_BUTTON: CSS selector for the Next/Submit button.
        FORGOT_PASSWORD_LINK: CSS selector for the Forgot Password link.
    """

    # --- Locators (kept as class-level constants to promote reuse and DRY) ---
    FORGOT_PASSWORD_LINK: ClassVar[str] = "#forgotPassword"

    # --- Locators ---
    EMAIL_INPUT = 'input[aria-label="Email Address"]'
    PASSWORD = 'input[aria-label="Password"]'
    SIGNIN_BUTTON = 'button:has-text("Sign in")'
    MFA_LABEL = 'text=Please select your preferred MFA method'

    def __init__(self, page: Page) -> None:
        """Initialize the page object.

        Args:
            page: The Playwright Page instance to use for interactions.
        """
        super().__init__(page)

    # --- UI Interaction Methods ---

    def enter_username(self, username: str) -> None:
        """Type the username into the username input field.

        Args:
            username: The username or email to input.

        Returns:
            LoginPage: The same page object to allow fluent chaining.
        """
        self.do_fill(self.EMAIL_INPUT, username)


    def enter_password(self, password: str) -> None:
        """Type the password into the password input field.

        Args:
            password: The clear-text password to input.

        Returns:
            LoginPage: The same page object to allow fluent chaining.
        """
        self.do_fill(self.PASSWORD, password)


    def click_next(self) -> None:
        """Click the Next button to submit the current step of login.

        Returns:
            None
        """
        self.do_click(self.SIGNIN_BUTTON)

    def click_forgot_password(self) -> None:
        """Open the Forgot Password flow by clicking its link.

        Returns:
            None
        """
        self.do_click(self.FORGOT_PASSWORD_LINK)



    def is_mfa_required(self) -> bool:
        return self.to_be_visible(self.MFA_LABEL)