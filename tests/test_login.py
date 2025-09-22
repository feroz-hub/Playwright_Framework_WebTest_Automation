import pytest

@pytest.mark.usefixtures("screenshot_on_failure")
class TestLogin:
    def test_valid_login(self, page, login_actions,home_actions, valid_user_credentials):
        """Verify valid user can log in successfully."""
        # Arrange: Prepare inputs and initial state
        username = valid_user_credentials["username"]
        password = valid_user_credentials["password"]

        # Act: Perform the login action
        login_actions.login(username, password)
        home_actions.accept_cookies_if_present()


        # Assert: Verify user is redirected to the expected landing page (case-insensitive)
        home_actions.verify_product_category_heading_is_visible()


