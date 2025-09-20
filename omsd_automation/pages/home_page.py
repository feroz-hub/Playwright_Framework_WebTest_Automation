from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from omsd_automation.pages.base_page import BasePage
from omsd_automation.pages.login_page import LoginPage


class HomePage(BasePage):
    """Page Object representing the Home (Dashboard) Page."""

    # ------------------------
    # Locators (constants, UPPER_SNAKE_CASE)
    # ------------------------
    USER_PROFILE = "#sysUserDisplayName"
    SIGN_OUT_LINK = "//span[text()='Sign Out']/parent::a"
    ACCEPT_COOKIES_BTN = "#onetrust-accept-btn-handler"

    def __init__(self, page: Page):
        super().__init__(page)

    # ------------------------
    # Generic Actions (do_*)
    # ------------------------
    def do_open_user_menu(self):
        """Click on the user profile menu (generic action)."""
        self.do_click(self.USER_PROFILE)

    def do_accept_cookies(self):
        """Accept cookies popup if present (only appears once on HomePage)."""
        try:
            cookie_btn = self.page.locator(self.ACCEPT_COOKIES_BTN)
            cookie_btn.wait_for(state="visible", timeout=3000)
            cookie_btn.click()
        except PlaywrightTimeoutError:
            # Popup not present → continue silently
            pass

    # ------------------------
    # Business Flows (user_*)
    # ------------------------
    def user_sign_out(self, test_case_id: str = None) -> LoginPage:
        """Business flow: sign out of the application and return the LoginPage."""
        self.do_open_user_menu()
        self.do_click(self.SIGN_OUT_LINK)
        self.take_screenshot(test_case=test_case_id, step_name="sign_out")
        return LoginPage(self.page)

    # ------------------------
    # Verifications (verify_*)
    # ------------------------
    def verify_user_logged_in(self) -> bool:
        """Verify if user profile is visible (indicates successful login)."""
        return self.verify_visible(self.USER_PROFILE)
