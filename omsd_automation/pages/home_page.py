# file: pages/home_page.py

from __future__ import annotations
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from omsd_automation.pages.base_page import BasePage


class HomePage(BasePage):
    """
    Page Object representing the Home (Dashboard) Page.

    This class encapsulates UI elements and low-level interactions only.
    It has no knowledge of business workflows or logging.
    """

    # ------------------------
    # Locators (constants, UPPER_SNAKE_CASE)
    # ------------------------
    USER_PROFILE = "#sysUserDisplayName"
    SIGN_OUT_LINK = "//span[text()='Sign Out']/parent::a"
    ACCEPT_COOKIES_BTN = "#onetrust-accept-btn-handler"

    def __init__(self, page: Page):
        """Initializes the HomePage with the Playwright Page and inherits from BasePage."""
        super().__init__(page)

    # ------------------------
    # Navigation Methods
    # ------------------------
    def open(self, url: str) -> HomePage:
        """Opens the home page URL and returns self for chaining."""
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

    def do_accept_cookies(self) -> HomePage:
        """Accept cookies popup if present (only appears once on HomePage)."""
        try:
            cookie_btn = self.page.locator(self.ACCEPT_COOKIES_BTN)
            cookie_btn.wait_for(state="visible", timeout=3000)
            cookie_btn.click()
        except PlaywrightTimeoutError:
            # Popup not present → continue silently
            pass
        return self

    # ------------------------
    # State & Data Retrieval Methods
    # ------------------------
    def get_user_display_name(self) -> str:
        """Retrieves the displayed username from the user profile element."""
        return self.do_get_text(self.USER_PROFILE)

    # ------------------------
    # Verification Methods (is_*, verify_*)
    # ------------------------
    def is_user_profile_visible(self) -> bool:
        """Checks if the user profile element is visible."""
        return self.is_visible(self.USER_PROFILE)

    def is_sign_out_link_visible(self) -> bool:
        """Checks if the sign-out link is visible (after opening user menu)."""
        return self.is_visible(self.SIGN_OUT_LINK)

    def is_cookies_popup_present(self) -> bool:
        """Checks if the cookies acceptance popup is currently visible."""
        return self.is_visible(self.ACCEPT_COOKIES_BTN)

    def verify_user_logged_in(self) -> bool:
        """Verify if user profile is visible (indicates successful login)."""
        return self.is_visible(self.USER_PROFILE)

    def verify_on_home_page(self, expected_url_fragment: str = None) -> bool:
        """
        Verify if currently on the home page.

        Args:
            expected_url_fragment: Optional URL fragment to match against current URL

        Returns:
            bool: True if on home page, False otherwise
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
            bool: True if page loads successfully, False on timeout
        """
        return self.wait_for_user_profile(timeout)