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
        EMAIL_INPUT: CSS selector for the email/username field.
        PASSWORD: CSS selector for the password field.
        SIGNIN_BUTTON: CSS selector for the Sign in/submit button.
        FORGOT_PASSWORD_LINK: CSS selector for the Forgot Password link.
        MFA_LABEL: Text locator used to detect if MFA is required.
    """

    # --- Locators (kept as class-level constants to promote reuse and DRY) ---
    FORGOT_PASSWORD_LINK: ClassVar[str] = "#forgotPassword"

    # --- Locators ---
    EMAIL_INPUT: ClassVar[str] = 'input[aria-label="Email Address"]'
    PASSWORD: ClassVar[str] = 'input[aria-label="Password"]'
    SIGNIN_BUTTON: ClassVar[str] = 'button:has-text("Sign in")'
    MFA_LABEL: ClassVar[str] = 'text=Please select your preferred MFA method'

    def __init__(self, page: Page) -> None:
        """Initialize the page object.

        Args:
            page: The Playwright Page instance to use for interactions.
        """
        super().__init__(page)

    # --- UI Interaction Methods ---

    def enter_username(self, username: str) -> None:
        """Type the username into the email/username input field.

        Args:
            username: The username or email to input.

        Returns:
            None

        Raises:
            playwright.sync_api.Error: If the element cannot be found or interacted with.
        """
        self.do_fill(self.EMAIL_INPUT, username)


    def enter_password(self, password: str) -> None:
        """Type the password into the password input field.

        Args:
            password: The clear-text password to input.

        Returns:
            None

        Raises:
            playwright.sync_api.Error: If the element cannot be found or interacted with.
        """
        self.do_fill(self.PASSWORD, password)


    def click_next(self) -> None:
        """Click the Sign-in button to submit the login form.

        Returns:
            None

        Raises:
            playwright.sync_api.Error: If the element cannot be found or clicked.
        """
        self.do_click(self.SIGNIN_BUTTON)

    def click_forgot_password(self) -> None:
        """Open the Forgot Password flow by clicking its link.

        Returns:
            None

        Raises:
            playwright.sync_api.Error: If the element cannot be found or clicked.
        """
        self.do_click(self.FORGOT_PASSWORD_LINK)



    def is_mfa_required(self) -> bool:
        """Determine whether the MFA step is required.

        This checks for visibility of an MFA-specific label. Using a visibility
        check instead of relying on navigation avoids flakiness when the page
        updates dynamically after sign-in.

        Returns:
            bool: True if the MFA label is visible, otherwise False.
        """
        # Visibility is a robust signal that the MFA flow has been triggered.
        return self.to_be_visible(self.MFA_LABEL)