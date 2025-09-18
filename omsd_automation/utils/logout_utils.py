from playwright.sync_api import expect

class LogoutUtils:
    @staticmethod
    def sign_out_user(home_page, base_page, page, test_case_id: str = None):
        """
        Signs out the user and verifies redirection to the login page using Playwright.

        Parameters:
        - home_page: HomePage object for dashboard operations
        - base_page: BasePage object for common helpers (screenshots, waits)
        - login_page: LoginPage object
        - log: Logger object for logging steps and actions
        - page: Playwright Page object
        - test_case_id: Optional string for screenshot naming
        """

        #log.step("Step 7: Sign out")

        # Sign out using HomePage method
        home_page.sign_out(test_case_id=test_case_id)

        # Wait for page ready if needed
        base_page.wait_for_page_ready()  # Optional if you implemented in BasePage

        # Take logout screenshot with organized naming
        base_page.take_screenshot("logout", test_case=test_case_id)

        # Wait for login page element
        login_locator = page.locator("#signInName")
        login_locator.wait_for(state="visible", timeout=5000)

        # Verify user is on login page
        is_on_login_page = login_locator.is_visible()
        #log.verification("User is redirected to login page after sign out", is_on_login_page)
        assert is_on_login_page, "User was not redirected to the login page after logout"
