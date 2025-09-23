# product_category_page.py

from playwright.sync_api import Page
from omsd_automation.pages.base_page import BasePage

class ProductCategoryPage(BasePage):
    """Page class for Product Category interactions."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

    def get_product_button(self, product_name: str):
        """Returns the button locator for a given product's software list."""
        return self.page.locator("#medical-product-box div").filter(has_text=f"{product_name} Software List").get_by_role("button")
    def other_product_button(self, product_name: str):
        return self.page.locator("#other-product-box div").filter(has_text=f"{product_name} Software List").get_by_role("button")
    def get_back_button(self):
        """Returns the back button locator."""
        return self.page.get_by_role("button", name="Back")
