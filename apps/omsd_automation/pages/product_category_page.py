"""Product Category Page Object.

This module implements a Playwright Page Object that models the "Product
Category" screen. It centralizes CSS selectors and provides small, readable
helper methods to interact with UI elements on that page.

Exposed interactions:
- Open a Medical product's Software List by product name.
- Open an Other product's Software List by product name.
- Click the Back button to navigate away.

Design notes:
- Keep selectors in one place via constants to simplify maintenance when the UI changes.
- Prefer resilient, readable selectors. Where roles are available, they are usually
  preferred; in this specific page we use container-scoped CSS for clarity.
- Methods intentionally perform the action (click) rather than return locators to keep
  the public API concise for test authors.
"""


from apps.omsd_automation.pages.base_page import BasePage


class ProductCategoryPage(BasePage):
    """Page Object for the Product Category screen.

    This class provides high-level interactions with the Product Category page,
    such as opening a product's Software List or navigating back.

    Attributes:
        page (Page): The Playwright Page instance used to query and interact with the DOM.

    Selector constants:
        PRODUCT_BOX_SELECTOR (str): CSS selector scoping queries to the Medical products area.
        OTHER_PRODUCT_BOX_SELECTOR (str): CSS selector scoping queries to the Other products area.
        BACK_BUTTON (str): CSS selector for the Back button. Kept as a constant for clarity.
    """

    # CSS containers for product grids. We scope to the inner "div" so product tiles are targeted.
    PRODUCT_BOX_SELECTOR = "#medical-product-box"
    OTHER_PRODUCT_BOX_SELECTOR = "#other-product-box"

    # Back button selector. We keep a clear, explicit selector (text-based) for stability.
    BACK_BUTTON = "button:has-text('Back')"

    def __init__(self) -> None:
        """Initialize the page object.

        Args:
            page: A Playwright Page instance.
        """
        super().__init__()

    @staticmethod
    def _category_button(container_selector: str, product_name: str) -> str:
        """
        Build a Playwright-compatible selector string for a product's "Software List" button.

        Args:
            container_selector: CSS selector that scopes the search (e.g., medical products container).
            product_name: The exact product display name as rendered in the UI.

        Returns:
            A selector string that targets the button inside the product tile.
        """
        return f"{container_selector} div:has-text('{product_name} Software List') >> role=button"


    def open_software(self, product_name: str) -> None:
        """Open the Software List for a Medical product by clicking its button.

        Args:
            product_name: The product's display name as shown in the Medical products box.

        Notes:
            - This method clicks the element; it does not return a locator.
            - Waiting, visibility checks, and retry logic are delegated to BasePage.do_click.
        """
        locator_str = self._category_button(self.PRODUCT_BOX_SELECTOR,product_name)
        self._click_button_when_ready(locator_str)


    def open_other_product(self, product_name: str) -> None:
        """Open the Software List for an Other product by clicking its button.

        Args:
            product_name: The product's display name as shown in the Other products box.

        Notes:
            - This method clicks the element; it does not return a locator.
            - Waiting, visibility checks, and retry logic are delegated to BasePage.do_click.
        """
        locator = self._category_button(self.OTHER_PRODUCT_BOX_SELECTOR, product_name)
        self._click_button_when_ready(locator)
    def click_back(self) -> None:
        """Click the Back button to navigate to the previous page or listing.

        Notes:
            - The actual navigation target depends on the application's routing.
            - Waiting and click stability are delegated to BasePage.do_click.
        """
        self.do_click(self.BACK_BUTTON)

    def _click_button_when_ready(self, locator_str: str) -> None:
        """Wait for a button to be ready and click it.

        - Centralizes the wait-then-click sequence to keep methods short and DRY.
        """
        self.wait_for_selector_base(locator_str)
        self.to_be_visible(locator_str)
        self.to_be_enabled(locator_str)
        self.do_click(locator_str)
