import pytest

@pytest.mark.usefixtures("screenshot_on_failure")
class TestLogin:
    def test_valid_login(self, page, login_actions,home_actions, software_uploader_credentials):
        """Verify valid user can log in successfully."""
        # Arrange: Prepare inputs and initial state
        username = software_uploader_credentials["username"]
        password = software_uploader_credentials["password"]

        # Act: Perform the login action
        login_actions.login(username, password)
        home_actions.accept_cookies_if_present()


        # Assert: Verify the product category heading is visible
        home_actions.verify_product_category_heading_is_visible()

    def test_software_category(self, page, login_actions,home_actions, product_category_actions, valid_user_credentials):
        """Verify valid user can log in successfully."""
        # Arrange: Prepare inputs and initial state
        username = valid_user_credentials["username"]
        password = valid_user_credentials["password"]

        # Act: Perform the login action
        login_actions.login(username, password)

        home_actions.accept_cookies_if_present()
        product_category_actions.open_medical_product("ESG-410")



        # Assert: Verify the product category heading is visible


