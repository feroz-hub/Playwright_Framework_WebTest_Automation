import pytest
from playwright.sync_api import expect
from omsd_automation.utils.config_reader import Config
from omsd_automation.utils.logger import setup_test_logging

@pytest.mark.parametrize("case", Config.get("tests.login"))
def test_login(page, case, login_page, home_page, base_page):
    """
    Playwright version of the login test with screenshots, logging, and logout validation.
    """

    # Setup logger for this test
    test_logger = setup_test_logging("test_login")
    test_name = f"Login Test ({case['username']})"
    test_logger.test_start(test_name)

    try:
        # Step 1: Perform login
        test_logger.step(f"Attempting login with username: {case['username']}")
        login_page.login(case["username"], case["password"], test_case_id="login_test")

        if case["expected"] == "success":
            test_logger.verification("Login expected to succeed", True)

            # Accept cookies if present
            base_page.accept_cookies()
            test_logger.action("Accepted cookies if present")

            # Wait for title
            base_page.wait_for_title("Olympus Medical Software Delivery", timeout=15000)
            test_logger.wait_success("Page title contains 'Olympus Medical Software Delivery'")

            # Short wait for stability
            page.wait_for_timeout(2000)
            base_page.take_screenshot("after_login", test_case="login_test")
            test_logger.action("Login screenshot captured")

            # Sign out
            test_logger.action("Signing out")
            home_page.sign_out(test_case_id="login_test")

            # Wait for login page to appear
            login_locator = page.locator("#signInName")
            login_locator.wait_for(state="visible", timeout=10000)
            test_logger.wait_success("Login page reappeared after logout")

            assert login_locator.is_visible()
            test_logger.verification("Login page is displayed after sign out", True)

        elif case["expected"] == "error":
            test_logger.verification("Login expected to fail (wrong credentials)", True)
            error_msg = login_page.get_error_message()
            test_logger.debug(f"Error message: {error_msg}")
            assert "incorrect" in error_msg.lower()
            test_logger.verification("Error message contains 'incorrect'", True)

        elif case["expected"] == "invalid_format":
            test_logger.verification("Login expected to fail (invalid email format)", True)
            validation_msg = login_page.get_email_validation_message()
            test_logger.debug(f"Validation message: {validation_msg}")
            assert "@" in validation_msg
            test_logger.verification("Validation message contains '@'", True)

        test_logger.test_end(test_name, success=True)

    except Exception as e:
        test_logger.error(f"Exception during test: {e}")
        base_page.take_screenshot("error_screenshot", test_case="login_test")
        test_logger.test_end(test_name, success=False)
        raise
