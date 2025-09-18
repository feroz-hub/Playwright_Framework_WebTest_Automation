from omsd_automation.utils.config_reader import Config
from tests import test_config as C
from playwright.sync_api import expect


class LoginUtils:
    @staticmethod
    def login_as_role(login_page, base_page, page, role: str, test_case_id: str):
        """Log in and take a screenshot with test_case_id."""
        creds = Config.get_user(role)
        login_page.login(creds["username"], creds["password"])
        expect(page).to_have_title(C.APP_TITLE, timeout=C.LOGIN_TIMEOUT * 1000)
        # Take login evidence screenshot
        base_page.take_screenshot(f"{test_case_id}")
        # Handle cookies if needed
        base_page.accept_cookies()
