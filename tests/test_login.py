import pytest

@pytest.mark.usefixtures("screenshot_on_failure")
class TestLogin:

    def test_valid_login(self, page, login_actions, valid_user_credentials):
        """Verify valid user can log in successfully."""
        login_actions.login(
            valid_user_credentials["username"],
            valid_user_credentials["password"]
        )
        # Assertion: check the landing page (case-insensitive)
        assert "/home/productcategory" in page.url.lower()

    def test_invalid_login(self, page, login_actions, invalid_user_credentials):
        """Verify invalid user sees error message."""
        login_actions.login(
            invalid_user_credentials["username"],
            invalid_user_credentials["password"]
        )
        error_text = login_actions.get_error_message()
        assert "invalid" in error_text.lower()
