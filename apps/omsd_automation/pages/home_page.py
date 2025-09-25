"""Page object for the application's Home (Dashboard) page.

This module defines the HomePage, a Page Object Model (POM) abstraction over
low-level Playwright interactions for the authenticated landing area. It
exposes fine‑grained UI operations only and leaves workflows, assertions, and
logging to the Actions layer and tests. This separation improves readability
and maintainability.

Design principles:
- POM: Encapsulates selectors and interactions for reuse and stability.
- SOLID: Single Responsibility — only low-level UI operations live here.
- DRY: Centralized locators prevent duplication across tests.
"""

from __future__ import annotations
from typing import ClassVar, Optional
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, Locator
from apps.omsd_automation.pages.base_page import BasePage


class HomePage(BasePage):
    """Page Object for the Home (Dashboard) page.

    The HomePage centralizes stable selectors and small, composable methods
    around Playwright calls. It purposefully avoids business logic and logging,
    keeping responsibilities focused on low-level UI interactions. Higher-level
    workflows belong in the Actions layer.

    Attributes:
        USER_PROFILE: CSS selector for the visible user display name element.
        SIGN_OUT_LINK: XPath selector for the Sign Out menu item.
        ACCEPT_COOKIES_BTN: CSS selector for the cookie consent accept button.
        PRODUCT_CATEGORY_HEADING: CSS selector for the Product Category heading.
    """

    # ------------------------
    # Locators (constants, UPPER_SNAKE_CASE)
    # ------------------------
    USER_PROFILE: ClassVar[str] = "#sysUserDisplayName"
    SIGN_OUT_LINK: ClassVar[str] = "//span[text()='Sign Out']/parent::a"
    ACCEPT_COOKIES_BTN: ClassVar[str] = "#onetrust-accept-btn-handler"
    PRODUCT_CATEGORY_HEADING: ClassVar[str] = "h4:has-text('Product Category')"

    def __init__(self, page: Page) -> None:
        """Initialize the HomePage.

        Args:
            page: The Playwright Page instance to use for interactions.
        """
        super().__init__(page)

    # ------------------------
    # Navigation Methods
    # ------------------------
    def open(self, url: str) -> "HomePage":
        """Open the home page URL.

        Args:
            url: The absolute or relative URL to navigate to.

        Returns:
            HomePage: The same page object to allow fluent chaining.
        """
        self.go_to(url)
        return self

    # ------------------------
    # UI Interaction Methods (do_*)
    # ------------------------
    def do_open_user_menu(self) -> HomePage:
        """Click on the user profile menu."""
        self.do_click(self.USER_PROFILE)
        return self

    def do_click_sign_out(self) -> HomePage:
        """Click on the sign-out link."""
        self.do_click(self.SIGN_OUT_LINK)
        return self

    def do_accept_cookies(self) -> "HomePage":
        """Accept the cookie consent banner if present.

        This banner may appear only once. If it is not visible within a short
        timeout, the method returns silently without raising.

        Returns:
            HomePage: The same page object to allow fluent chaining.
        """
        try:
            cookie_btn = self.page.locator(self.ACCEPT_COOKIES_BTN)
            cookie_btn.wait_for(state="visible", timeout=7000)
            cookie_btn.click()
        except PlaywrightTimeoutError:
            # Popup not present → continue silently
            pass
        return self

    def get_product_category_heading(self) -> Locator:
        """Returns the locator for the 'Product Category' heading."""
        return self.get_locator(self.PRODUCT_CATEGORY_HEADING)

    # ------------------------
    # State & Data Retrieval Methods
    # ------------------------
    def get_user_display_name(self) -> str:
        """Get the display name of the logged-in user.

        Returns:
            str: The text content of the user profile element.
        """
        return self.do_get_text(self.USER_PROFILE)

    # ------------------------
    # Verification Methods (is_*, verify_*)
    # ------------------------
    def is_user_profile_visible(self) -> bool:
        """Checks if the user profile element is visible."""
        return self.to_be_visible(self.USER_PROFILE)

    def is_sign_out_link_visible(self) -> bool:
        """Checks if the sign-out link is visible (after opening a user menu)."""
        return self.to_be_visible(self.SIGN_OUT_LINK)

    def is_cookies_popup_present_enabled(self) -> bool:
        """Checks if the cookies acceptance popup is currently visible."""
        self.wait_for_element(self.ACCEPT_COOKIES_BTN, state="visible", timeout=5000)
        return self.to_be_enabled(self.ACCEPT_COOKIES_BTN)

    def verify_user_logged_in(self) -> bool:
        """Verify if user profile is visible (indicates successful login)."""
        return self.to_be_visible(self.USER_PROFILE)

    def verify_on_home_page(self, expected_url_fragment: Optional[str] = None) -> bool:
        """Check whether the browser is currently on the Home page.

        If an expected URL fragment is provided, this method checks the
        current page URL for that fragment. Otherwise, it falls back to a UI
        signal — the visibility of the user profile element — as a heuristic
        that the Home page has loaded.

        Args:
            expected_url_fragment: An optional URL substring expected to be
                present in the current page URL.

        Returns:
            bool: True if on the home page, False otherwise.
        """
        if expected_url_fragment:
            return expected_url_fragment in self.page.url
        # If no specific URL check, verify by presence of user profile
        return self.is_user_profile_visible()

    # ------------------------
    # Wait Methods
    # ------------------------
    def wait_for_user_profile(self, timeout: int = 10000) -> bool:
        """
        Wait for user profile element to be visible.

        Args:
            timeout: Timeout in milliseconds

        Returns:
            bool: True if element becomes visible, False on timeout
        """
        return self.wait_for_element(self.USER_PROFILE, state="visible", timeout=timeout)

    def wait_for_page_load(self, timeout: int = 10000) -> bool:
        """
        Wait for the home page to fully load by waiting for the user profile.

        Args:
            timeout: Timeout in milliseconds

        Returns:
            bool: True if the page loads successfully, False on timeout
        """
        return self.wait_for_user_profile(timeout)