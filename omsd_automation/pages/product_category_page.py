"""Product Category Page Object.

This module provides a Playwright Page Object for interacting with the
Product Category screen. It exposes typed helper methods that return
Playwright Locator objects for:
- Selecting a specific product's "Software List" button from the Medical products box.
- Selecting a specific product's "Software List" button from the Other products box.
- Accessing the Back button.

Notes:
- We rely on accessible roles where possible to keep selectors resilient.
- Constants are defined for CSS containers to keep selectors in one place.
"""

from playwright.sync_api import Page, Locator
from omsd_automation.pages.base_page import BasePage


class ProductCategoryPage(BasePage):
    """Encapsulates interactions on the Product Category page.

    Attributes:
        page: The Playwright Page instance used to query and interact with the DOM.

    Selectors:
        PRODUCT_BOX_SELECTOR: CSS selector that narrows to Medical products container.
        OTHER_PRODUCT_BOX_SELECTOR: CSS selector that narrows to Other products container.
        BACK_BUTTON_SELECTOR: CSS selector for the Back button (maybe unused if we rely on role-based locator).
    """

    # CSS containers for product grids
    PRODUCT_BOX_SELECTOR = "#medical-product-box div"
    OTHER_PRODUCT_BOX_SELECTOR = "#other-product-box div"

    # Back button selector kept for reference; the role-based locator is preferred below
    BACK_BUTTON_SELECTOR = "#back"

    def __init__(self, page: Page) -> None:
        """Initialize the page object with a Playwright Page instance."""
        super().__init__(page)
        self.page = page

    def get_product_button(self, product_name: str) -> Locator:
        """Return the Locator for a Medical product's "Software List" button.

        Args:
            product_name: Visible name of the product as it appears on the page.

        Returns:
            A Locator pointing to the "Software List" button for the given product
            inside the Medical products section.
        """
        # We first scope to the Medical products container, filter by the visible text
        # "<product_name> Software List", then ask Playwright for the button role inside it.
        return (
            self.page
            .locator(self.PRODUCT_BOX_SELECTOR)
            .filter(has_text=f"{product_name} Software List")
            .get_by_role("button")
        )

    def other_product_button(self, product_name: str) -> Locator:
        """Return the Locator for an Other product's "Software List" button.

        Args:
            product_name: Visible name of the product as it appears on the page.

        Returns:
            A Locator pointing to the "Software List" button for the given product
            inside the Other products section.
        """
        return (
            self.page
            .locator(self.OTHER_PRODUCT_BOX_SELECTOR)
            .filter(has_text=f"{product_name} Software List")
            .get_by_role("button")
        )

    def get_back_button(self) -> Locator:
        """Return the Locator for the Back button.

        We prefer an accessible role-based query to keep the selector robust
        against minor DOM changes. If necessary, you can switch to the CSS
        selector stored in BACK_BUTTON_SELECTOR.
        """
        # Alternative: return self.page.locator(self.BACK_BUTTON_SELECTOR)
        return self.page.get_by_role("button", name="Back")
