# file: actions/home_actions.py

from __future__ import annotations
from typing import Optional
from omsd_automation.pages.home_page import HomePage
from omsd_automation.pages.login_page import LoginPage
from omsd_automation.utils.logger_utils import setup_test_logger


class HomeActions:
    """
    Orchestrates HomePage methods into reusable business workflows.

    This class contains all logging and workflow logic, keeping the
    Page Object and tests clean. Handles all business operations
    related to the Home/Dashboard page.
    """

    def __init__(self, home_page: HomePage):
        """
        Initializes the actions with a HomePage instance.

        Args:
            home_page: HomePage instance for UI interactions
        """
        self.home_page = home_page
        self.logger = setup_test_logger("HomeActions")

    # ------------------------
    # Navigation Actions
    # ------------------------
    def open_home_page(self, url: str) -> None:
        """
        Opens the home page URL.

        Args:
            url: Home page URL to navigate to
        """
        self.logger.log_action(f"Opening home page: {url}")
        try:
            self.home_page.open(url)
            self.logger.log_info("Home page opened successfully")
        except Exception as e:
            self.logger.log_error(f"Failed to open home page: {e}")
            raise

    # ------------------------
    # User Profile Actions
    # ------------------------
    def get_logged_in_user_name(self) -> str:
        """
        Retrieves the display name of the currently logged-in user.

        Returns:
            str: The user's display name
        """
        self.logger.log_action("Retrieving logged-in user display name")
        try:
            username = self.home_page.get_user_display_name()
            self.logger.log_info(f"Retrieved username: '{username}'")
            return username
        except Exception as e:
            self.logger.log_error(f"Failed to retrieve username: {e}")
            raise

    def open_user_menu(self) -> None:
        """
        Opens the user profile menu.
        """
        self.logger.log_action("Opening user profile menu")
        try:
            self.home_page.do_open_user_menu()
            self.logger.log_info("User profile menu opened successfully")
        except Exception as e:
            self.logger.log_error(f"Failed to open user profile menu: {e}")
            raise

    # ------------------------
    # Authentication Workflows
    # ------------------------
    def sign_out(self, test_case_id: Optional[str] = None) -> LoginPage:
        """
        Performs the complete sign-out workflow.

        Args:
            test_case_id: Optional test case identifier for logging

        Returns:
            LoginPage: New LoginPage instance after sign out
        """
        log_prefix = f"[{test_case_id}] " if test_case_id else ""
        self.logger.log_info(f"{log_prefix}Starting sign-out workflow")

        try:
            # Step 1: Open user menu
            self.logger.log_action(f"{log_prefix}Opening user profile menu")
            self.home_page.do_open_user_menu()

            # Step 2: Verify sign-out link is visible
            if not self.home_page.is_sign_out_link_visible():
                raise Exception("Sign out link is not visible after opening user menu")

            # Step 3: Click sign out
            self.logger.log_action(f"{log_prefix}Clicking sign out link")
            self.home_page.do_click_sign_out()

            # Step 4: Take screenshot for verification
            screenshot_path = f"sign-out_{test_case_id}" if test_case_id else "sign-out"
            self.home_page.take_screenshot(path=f"screenshots/{screenshot_path}.png")
            self.logger.log_info(f"{log_prefix}Screenshot captured: {screenshot_path}.png")

            # Step 5: Return LoginPage instance
            login_page = LoginPage(self.home_page.page)
            self.logger.log_info(f"{log_prefix}Sign-out workflow completed successfully")
            return login_page

        except Exception as e:
            error_screenshot = f"sign-out_error_{test_case_id}" if test_case_id else "sign-out_error"
            self.home_page.take_screenshot(path=f"screenshots/{error_screenshot}.png")
            self.logger.log_error(f"{log_prefix}Sign-out workflow failed: {e}")
            raise

    # ------------------------
    # Cookie Management
    # ------------------------
    def accept_cookies_if_present(self) -> bool:
        """
        Accepts cookies popup if it's present on the page.

        Returns:
            bool: True if cookies were accepted, False if popup wasn't present
        """
        self.logger.log_action("Checking for cookies acceptance popup")
        try:
            if self.home_page.is_cookies_popup_present():
                self.logger.log_info("Cookies popup detected, accepting cookies")
                self.home_page.do_accept_cookies()
                self.logger.log_info("Cookies accepted successfully")
                return True
            else:
                self.logger.log_info("No cookies popup present, skipping")
                return False
        except Exception as e:
            self.logger.log_error(f"Error while handling cookies popup: {e}")
            raise

    # ------------------------
    # Page State Verifications
    # ------------------------
    def verify_user_logged_in(self, expected_username: Optional[str] = None, timeout_ms: int = 10000) -> bool:
        """
        Verifies that a user is successfully logged in.

        Args:
            expected_username: Optional expected username to verify against
            timeout_ms: Timeout in milliseconds for waiting for elements

        Returns:
            bool: True if user is logged in (and matches expected username if provided)
        """
        self.logger.log_action("Verifying user login status")
        try:
            # Wait for user profile to be visible
            if not self.home_page.wait_for_user_profile(timeout=timeout_ms):
                self.logger.log_verification("User profile not visible", result=False)
                return False

            # Basic login verification
            is_logged_in = self.home_page.verify_user_logged_in()

            if not is_logged_in:
                self.logger.log_verification("User login verification failed", result=False)
                return False

            # Optional username verification
            if expected_username:
                actual_username = self.home_page.get_user_display_name()
                username_matches = expected_username.lower() in actual_username.lower()

                if not username_matches:
                    self.logger.log_verification(
                        f"Username mismatch - Expected: '{expected_username}', Actual: '{actual_username}'",
                        result=False
                    )
                    return False

                self.logger.log_verification(
                    f"User logged in successfully as: '{actual_username}'",
                    result=True
                )
            else:
                self.logger.log_verification("User login verified successfully", result=True)

            return True

        except Exception as e:
            self.logger.log_error(f"Error during login verification: {e}")
            return False

    def verify_on_home_page(self, expected_url_fragment: Optional[str] = None, timeout_ms: int = 10000) -> bool:
        """
        Verifies that the current page is the home page.

        Args:
            expected_url_fragment: Optional URL fragment to verify
            timeout_ms: Timeout in milliseconds for waiting

        Returns:
            bool: True if on home page, False otherwise
        """
        self.logger.log_action("Verifying current page is home page")
        try:
            # Wait for page to load
            if not self.home_page.wait_for_page_load(timeout=timeout_ms):
                self.logger.log_verification("Home page failed to load within timeout", result=False)
                return False

            # Verify we're on home page
            is_home_page = self.home_page.verify_on_home_page(expected_url_fragment)

            if is_home_page:
                current_url = self.home_page.page.url
                self.logger.log_verification(f"Successfully verified on home page: {current_url}", result=True)
            else:
                current_url = self.home_page.page.url
                self.logger.log_verification(f"Not on expected home page. Current URL: {current_url}", result=False)

            return is_home_page

        except Exception as e:
            self.logger.log_error(f"Error during home page verification: {e}")
            return False

    # ------------------------
    # Wait Operations
    # ------------------------
    def wait_for_home_page_load(self, timeout_ms: int = 30000) -> bool:
        """
        Waits for the home page to fully load.

        Args:
            timeout_ms: Timeout in milliseconds

        Returns:
            bool: True if page loaded successfully, False on timeout
        """
        self.logger.log_action(f"Waiting for home page to load (timeout: {timeout_ms}ms)")
        try:
            page_loaded = self.home_page.wait_for_page_load(timeout=timeout_ms)

            if page_loaded:
                self.logger.log_info("Home page loaded successfully")
            else:
                self.logger.log_error(f"Home page failed to load within {timeout_ms}ms")

            return page_loaded

        except Exception as e:
            self.logger.log_error(f"Error while waiting for home page load: {e}")
            return False

    # ------------------------
    # Complete Workflows
    # ------------------------
    def complete_initial_setup(self, timeout_ms: int = 10000) -> bool:
        """
        Performs initial setup tasks when landing on home page.
        This includes accepting cookies and waiting for page load.

        Args:
            timeout_ms: Timeout for page load operations

        Returns:
            bool: True if setup completed successfully
        """
        self.logger.log_info("Starting home page initial setup")
        try:
            # Wait for page to load
            if not self.wait_for_home_page_load(timeout_ms):
                return False

            # Accept cookies if present
            self.accept_cookies_if_present()

            # Final verification
            setup_successful = self.verify_user_logged_in()

            if setup_successful:
                self.logger.log_info("Home page initial setup completed successfully")
            else:
                self.logger.log_error("Home page initial setup failed final verification")

            return setup_successful

        except Exception as e:
            self.logger.log_error(f"Error during home page initial setup: {e}")
            return False